from core.llm import get_llm
from core.state import GraphState, TailoredResume

TAILOR_PROMPT = """You are a resume perfectionist. Student will upload there resume and JD of the company. 
You have to critically judge the resume and rewrite the resume so that resume can succesfully pass the screening process.

Original Resume: {resume}

Job Description: {jd}


Missing skills which JD required -{missing_skills}

Do:
- professional_summary: 2-3 lines, JD-Optimized
- skills_section: skills list, ordered according to JD relevance
- experience_bullets: Rewritten bullets- quantified, JD keyword aligned but factually resume grounded. If no number is present instead of guessing give a [X] placeholder


"""

def generate_tailored_resume_node(state: GraphState) -> dict:
    llm = get_llm(temperature= 0.8)
    structured_llm = llm.with_structured_output(TailoredResume)

    analysis = state.get("resume_analysis")
    missing_skills = ", ".join(analysis.missing_skills) if analysis else "N/A"

    tailored: TailoredResume = structured_llm.invoke(TAILOR_PROMPT.format(
        resume = state["resume_text"],
        jd = state["jd_text"],
        missing_skills = missing_skills
    ))

    return {
        "tailored_resume": tailored,
        "messages": [{
            "role":"assistant",
            "content": "[Tailored Resume] Rewrite complete"
        }]
    }