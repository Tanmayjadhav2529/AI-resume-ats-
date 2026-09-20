import logging
from typing import Dict, List, Optional
import spacy
from sentence_transformers import SentenceTransformer

from backend.models.schemas import IssueDetail
from backend.services.groq_parser import parse_resume, parse_job_description
from backend.services.jd_matcher import compare_resume_with_jd
from backend.services.feedback_engine import analyze_issues, generate_issues_summary
from backend.services.ats_scorer import (
    calculate_overall_score,
    validate_skills_with_projects,
    detect_location_info,
    generate_strengths as generate_scorer_strengths,
    generate_critical_issues as generate_scorer_critical_issues,
    generate_improvements as generate_scorer_improvements,
)
from backend.services.recommendation_engine import generate_all_recommendations
from backend.utils.file_utils import (
    get_default_grammar_results,
    get_default_location_results,
)

logger = logging.getLogger('ats_resume_scorer')


def analyze_full_resume(
    resume_text: str,
    nlp: spacy.Language,
    embedder: SentenceTransformer,
    job_description: Optional[str] = None,
) -> Dict:
    # 1. Parse resume with Groq LLM
    parsed_resume = parse_resume(resume_text)
    logger.info(f"Groq parsed summary: {parsed_resume.get('professional_summary', '')[:100]!r}")
    logger.info(f"Groq parsed skills count: {len(parsed_resume.get('skills', []))}")
    logger.info(f"Groq parsed experience count: {len(parsed_resume.get('experience', []))}")

    skills       = parsed_resume.get('skills', [])
    projects     = parsed_resume.get('projects', [])
    keywords     = parsed_resume.get('keywords', [])
    action_verbs = parsed_resume.get('action_verbs', [])

    experience_months = sum(
        int(e.get('duration_months', 0))
        for e in parsed_resume.get('experience', [])
        if isinstance(e, dict)
    )

    contact_info = {
        'email':     parsed_resume.get('email'),
        'phone':     parsed_resume.get('phone'),
        'linkedin':  parsed_resume.get('linkedin'),
        'github':    parsed_resume.get('github'),
        'portfolio': None,
    }

    # 2. Skill validation against projects and experience entries
    skill_validation = validate_skills_with_projects(
        skills=skills,
        projects=projects,
        experience_entries=parsed_resume.get('experience', []),
        embedder=embedder,
    )

    # 3. JD Comparison (if JD provided)
    jd_comparison_result = None
    jd_keywords = None
    parsed_jd = None
    if job_description and job_description.strip():
        parsed_jd = parse_job_description(job_description.strip())
        jd_keywords = list(set(
            parsed_jd.get('keywords', []) +
            parsed_jd.get('required_skills', []) +
            parsed_jd.get('preferred_skills', [])
        ))
        jd_comparison_result = compare_resume_with_jd(
            resume_text=resume_text,
            resume_keywords=keywords,
            resume_skills=skills,
            jd_text=job_description.strip(),
            jd_keywords=jd_keywords,
            embedder=embedder,
            nlp=nlp,
        )

    # 4. Location & Privacy Analysis
    # Uses spaCy NER and regex for address/zip code privacy detection
    if nlp is not None and hasattr(nlp, '__call__'):
        try:
            location_results = detect_location_info(resume_text, nlp)
        except Exception as exc:
            logger.warning(f"Location detection failed: {exc}")
            location_results = get_default_location_results()
    else:
        location_results = get_default_location_results()

    # 5. Grammar Analysis
    # Note: Automated grammar analysis (e.g., LanguageTool) is not installed in the current environment.
    # We use default structure (no penalty) so the system does NOT claim fake grammar results.
    grammar_results = get_default_grammar_results()

    # 6. ATS Scoring
    scores = calculate_overall_score(
        text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        keywords=keywords,
        action_verbs=action_verbs,
        skill_validation_results=skill_validation,
        grammar_results=grammar_results,
        location_results=location_results,
        jd_keywords=jd_keywords,
        experience_months=experience_months,
    )

    # 7. Detailed Feedback Issues
    detailed_feedback = analyze_issues(
        resume_text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        projects=projects,
        action_verbs=action_verbs,
        skill_validation=skill_validation,
        scores=scores,
        contact_info=contact_info,
    )
    issues_summary = generate_issues_summary(detailed_feedback)

    # 8. Recommendations Engine
    sections = {
        'experience': '\n'.join(e.get('description', '') for e in parsed_resume.get('experience', []) if isinstance(e, dict)),
        'education':  '\n'.join(e.get('degree', '') for e in parsed_resume.get('education', []) if isinstance(e, dict)),
        'skills':     ', '.join(skills),
        'summary':    parsed_resume.get('professional_summary', ''),
        'projects':   '\n'.join(p.get('description', '') for p in parsed_resume.get('projects', []) if isinstance(p, dict)),
    }
    recs_all = generate_all_recommendations(
        skill_validation_results=skill_validation,
        grammar_results=grammar_results,
        location_results=location_results,
        score_results=scores,
        sections=sections,
        keyword_analysis=jd_comparison_result,
        resume_keywords=keywords,
    )

    # 9. Aggregate Strengths, Critical Issues, Suggestions, Warnings
    strengths_raw = generate_scorer_strengths(scores, skill_validation, grammar_results) + _generate_strengths(parsed_resume, skills, projects, action_verbs, skill_validation, scores)
    # Deduplicate while preserving order
    strengths = []
    for s in strengths_raw:
        cleaned_s = s.strip()
        if cleaned_s and cleaned_s not in strengths:
            strengths.append(cleaned_s)

    critical_issues_raw = generate_scorer_critical_issues(scores, grammar_results, location_results)
    for rec in recs_all.get('critical_recommendations', []):
        critical_issues_raw.append(rec.title)
    critical_issues = []
    for ci in critical_issues_raw:
        cleaned_ci = ci.strip()
        if cleaned_ci and cleaned_ci not in critical_issues:
            critical_issues.append(cleaned_ci)

    suggestions_raw = generate_scorer_improvements(scores, skill_validation)
    for rec in recs_all.get('high_recommendations', []) + recs_all.get('medium_recommendations', []):
        suggestions_raw.append(rec.title)
    suggestions = []
    for sg in suggestions_raw:
        cleaned_sg = sg.strip()
        if cleaned_sg and cleaned_sg not in suggestions:
            suggestions.append(cleaned_sg)

    warnings = list(location_results.get('recommendations', []))

    validated_raw   = skill_validation.get('validated_skills', [])
    unvalidated_raw = skill_validation.get('unvalidated_skills', [])
    total_skills    = len(validated_raw) + len(unvalidated_raw)
    val_pct         = round((len(validated_raw) / total_skills * 100) if total_skills > 0 else 0, 1)

    skill_validation_details = {
        "validated": [
            {
                "skill":    item['skill'],
                "projects": item.get('projects', []),
            }
            for item in validated_raw
        ],
        "unvalidated":     unvalidated_raw,
        "total":           total_skills,
        "validated_count": len(validated_raw),
        "validation_pct":  val_pct,
    }

    return {
        "ATS_score":          scores['overall_score'],
        "ats_score":          scores['overall_score'],
        "component_scores": {
            "formatting":       scores['formatting_score'],
            "keywords":         scores['keywords_score'],
            "content":          scores['content_score'],
            "skill_validation": scores['skill_validation_score'],
            "ats_compatibility": scores['ats_compatibility_score'],
        },
        "issues_summary":    issues_summary,
        "detailed_feedback": detailed_feedback,
        "jd_match_analysis": jd_comparison_result,
        "jd_comparison":     jd_comparison_result,
        "skills":            skills,
        "matched_keywords":  (
            jd_comparison_result['matched_keywords']
            if jd_comparison_result else list(keywords[:20])
        ),
        "missing_keywords":  (
            jd_comparison_result['missing_keywords']
            if jd_comparison_result else []
        ),
        "strengths":          strengths,
        "critical_issues":    critical_issues,
        "suggestions":        suggestions,
        "warnings":           warnings,
        "interpretation":     scores.get('overall_interpretation', ''),
        "skill_validation_details": skill_validation_details,
        "experience_months":  experience_months,
        "parsed_jd_job_title": parsed_jd.get('job_title', '') if parsed_jd else '',
    }


def _generate_strengths(
    parsed_resume: Dict, skills: List, projects: List,
    action_verbs: List, skill_validation: Dict, scores: Dict,
) -> List[str]:
    """Generate a list of things the resume does well, based on actual structured data."""
    strengths = []

    if parsed_resume.get('experience'):
        strengths.append("Has a dedicated Experience section")
    if parsed_resume.get('projects') or len(projects) > 0:
        strengths.append("Includes a Projects section showcasing applied skills")
    if parsed_resume.get('education'):
        strengths.append("Education section is present")
    if parsed_resume.get('skills'):
        strengths.append("Clear Skills section with listed technologies")
    if parsed_resume.get('professional_summary', '').strip():
        strengths.append("Professional Summary provides a quick overview")

    if len(skills) >= 8:
        strengths.append(f"Strong skill set — {len(skills)} skills detected")
    if len(action_verbs) >= 5:
        strengths.append(f"Uses {len(action_verbs)} strong action verbs in bullet points")

    validated = skill_validation.get('validated_skills', [])
    if len(validated) >= 3:
        strengths.append(f"{len(validated)} skills are backed by project/experience evidence")

    if scores.get('formatting_score', 0) >= 16:
        strengths.append("Well-formatted and ATS-friendly structure")
    if scores.get('content_score', 0) >= 20:
        strengths.append("Content quality is high with measurable achievements")

    return strengths