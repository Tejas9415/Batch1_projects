from datetime import datetime

from core.state import GraphState


def compile_report_node(state: GraphState) -> dict:
    prep = state["prep_package"]
    company = state.get("company_overview", {})
    mode = state["mode"]
    lines: list[str] = []

    if mode == "new_prep":
        lines.append(f"# Interview Prep Report: {state['company_name']}")
    else:
        lines.append(f"# Comeback Plan: {state['company_name']} ({state.get('round_name', 'Interview')})")

    lines.append(f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    lines.append(f"\n**Role:** {state.get('role_title', 'N/A')} | "
                 f"**Days Remaining (at generation time):** {prep.days_remaining}\n")

    if mode == "new_prep":
        resume_analysis = state["resume_analysis"]
        lines.append("## Resume vs JD Analysis")
        lines.append(f"**Match Score:** {resume_analysis.match_score:.0f}/100")
        lines.append(f"**Matched Skills:** {', '.join(resume_analysis.matched_skills) or 'N/A'}")
        lines.append(f"**Missing Skills:** {', '.join(resume_analysis.missing_skills) or 'None'}")
        lines.append("\n**Suggested Resume Rewrites:**")
        for s in resume_analysis.suggestions:
            lines.append(f"- ❌ _{s.original_line}_")
            lines.append(f"  ✅ **{s.improved_line}**")
            lines.append(f"  _Why: {s.reason}_")
    else:
        debrief = state["debrief_analysis"]
        lines.append(f"## What Happened Last Time ({state.get('round_name', 'the interview')})")
        lines.append(f"**Confidence level:** {debrief.confidence_level}")
        lines.append(f"**Strengths shown:** {', '.join(debrief.strengths_shown) or 'N/A'}")
        lines.append(f"**Weaknesses identified:** {', '.join(debrief.weaknesses_identified) or 'N/A'}")
        lines.append(f"**Root causes:** {', '.join(debrief.root_causes) or 'N/A'}")

    lines.append(f"\n## About {state['company_name']}")
    if company.get("found"):
        lines.append(company.get("summary", ""))
    else:
        lines.append("_Wikipedia par nahi mila - company website/LinkedIn khud check karo._")
    lines.append("\n**Talking points if asked \"do you know about us?\":**")
    for point in prep.company_talking_points:
        lines.append(f"- {point}")

    lines.append("\n## Your Opening Pitch")
    lines.append(f"> {prep.opening_pitch}")

    plan_title = "Prep Plan" if mode == "new_prep" else "Comeback Plan"
    lines.append(f"\n## {prep.days_remaining}-Day {plan_title}")
    for day in prep.day_wise_plan:
        lines.append(f"\n**{day.date} — {day.focus}**")
        for task in day.tasks:
            lines.append(f"- {task}")

    lines.append("\n## Mock Interview Results")
    for i, evaluation in enumerate(state.get("evaluation_history", []), start=1):
        lines.append(f"\n### Attempt {i} — Overall Score: {evaluation.overall_score:.0f}/100")
        for fb in evaluation.per_question_feedback:
            lines.append(f"- **{fb.question_id}** (score={fb.score:.0f}): {fb.feedback}")
        lines.append(f"\n**Weak areas:** {', '.join(evaluation.weak_areas) or 'None major'}")
        lines.append("**Comeback strategy:**")
        for step in evaluation.comeback_strategy:
            lines.append(f"- {step}")

    report = "\n".join(lines)
    return {
        "final_report": report,
        "messages": [{"role": "assistant", "content": "[Report] Report ready."}],
    }
