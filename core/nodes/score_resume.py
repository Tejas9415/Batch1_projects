from core.llm import get_llm
from core.state import GraphState, ResumeAnalysis

SCORE_PROMPT = """
You are an expert resume analyzer. Score the resume against the JD provided.

Resume: {resume}
----

Job Description: {jd}
____

match_score(0-100), matched_skills, missing_skills, and 3 to 5 suggestions
"""

def _score(resume_text: str, jd_text: str) -> ResumeAnalysis:
    llm = get_llm(temperature= 0)
    structured_llm = llm.with_structured_output(ResumeAnalysis)
    return structured_llm.invoke(SCORE_PROMPT.format(resume = resume_text, jd = jd_text))

def score_resume_node(state: GraphState) -> dict:
    analysis = _score(state["resume_text"], state["jd_text"])
    return {
        "resume_analysis": analysis,
        "original_match_score": analysis.match_score,
        "messages":[
            {
                "role":"assistant",
                "content": f"[Original Score] {analysis.match_score}/100"
            }
        ]
    }
def score_tailored_resume_node(state: GraphState) -> dict:
    tailored = state["tailored_resume"]
    tailored_text = (
        f"Professional Summary:{tailored.professional_summary}\n"
        f"Skills:{', '.join(tailored.skills_section)}\n"
        f"Experience: {'; '.join(tailored.experience_bullets)}"
    )

    analysis = _score(tailored_text, state["jd_text"])
    return {
        "new_match_score": analysis.match_score,
        "messages":[
            {
                "role":"assistant",
                "content": f"[New Score] {analysis.match_score}/100"
            }
        ]
    }