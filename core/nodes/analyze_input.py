from core.llm import get_llm
from core.state import DebriefAnalysis, GraphState, ResumeAnalysis

RESUME_ANALYSIS_PROMPT = """
You are an expert career coach and technical recruiter. Analyze the candidate's resume against the given job description honestly, objectively, and bluntly. Do not sugarcoat weaknesses, and do not give credit for skills or experience that are not actually present in the resume.

Resume:
{resume}

Job Description:
{jd}

Analyze the resume against the job description using the following steps:

1. match_score (0-100):
   - Give an overall match score based on how well the candidate's skills, experience, projects, education, and qualifications align with the job description.
   - Consider both required and preferred qualifications.
   - Do not inflate the score.

2. matched_skills:
   - List the skills, technologies, tools, frameworks, concepts, and qualifications from the job description that are clearly present in the resume.
   - Only include skills that are explicitly mentioned or strongly demonstrated in the resume.

3. missing_skills:
   - List the important skills, technologies, tools, frameworks, concepts, and qualifications required or preferred by the job description that are missing from the resume.
   - Do not consider a skill missing if the resume clearly demonstrates it under a different but equivalent term.

4. suggestions:
   - Provide practical and specific recommendations to improve the candidate's chances of getting shortlisted.
   - Suggest which missing skills should be learned first based on their importance to the JD.
   - Suggest specific resume improvements, such as:
     - Skills that should be added if genuinely possessed
     - Projects or experience that should be highlighted
     - Keywords that should be included for ATS compatibility
     - Bullet points that should be rewritten to better demonstrate relevant experience
   - Never recommend falsely adding a skill or experience that the candidate does not have.

Return the analysis in a clear, structured format.
"""

DEBRIEF_ANALYSIS_PROMPT = """
You are an experienced interview coach. Analyze the student's interview performance based strictly on the self-report provided below.

Be honest, practical, and constructive. Do not make assumptions beyond the information provided.

Company: {company}

Round: {round_name}

What went well for the student:
{what_went_well}

Where the student actually struggled:
{what_went_wrong}

Specific difficulty:
{difficulty}

Analyze the interview using the following:

1. strengths_shown:
   - Identify the strongest skills, behaviors, or qualities demonstrated by the student.
   - Return a short list.

2. weakness_identified:
   - Identify the most important weaknesses or knowledge gaps demonstrated during the interview.
   - Return a short list.

3. root_causes:
   - Identify the likely underlying reasons behind the student's difficulties.
   - Return a short list.

4. confidence_level:
   - Assess the student's confidence based strictly on the self-report.
   - Choose exactly one:
     - low
     - medium
     - high

Do not return markdown.
Do not return labels such as "strengths_shown:" manually.
Return only the structured information requested by the schema.
"""

def analyze_input_node(state: GraphState) -> dict:
    llm = get_llm(temperature= 0.2)

    if state["mode"] =="new_prep":
        structured_llm = llm.with_structured_output(ResumeAnalysis)
        analysis: ResumeAnalysis = structured_llm.invoke(
            RESUME_ANALYSIS_PROMPT.format(resume = state["resume_text"], jd = state["jd_text"])
        )
        return {
            "resume_analysis": analysis,
            "messages":[
                {
                    "role":"assistant",
                    "content": f"[Resume Analysis] match_score = {analysis.match_score}/100,"
                    f"{len(analysis.missing_skills)} skills missing"
                }
            ]
        }
    structured_llm = llm.with_structured_output(DebriefAnalysis)
    debriefing: DebriefAnalysis = structured_llm.invoke(
    DEBRIEF_ANALYSIS_PROMPT.format(company = state.get("company_name","Company"), round_name = state.get("round_name","N/A"), what_went_well = state.get("what_went_well",""),
                                   what_went_wrong = state.get("what_went_wrong",""), difficulty = state.get("difficulty_faced"," Not Specified") )
        )
    return {
        "debrief_analysis": debriefing,
        "messages":[
            {
                "role":"assistant",
                "content": f"[Debrief Analysis] confidenvce = {debriefing.confidence_level}"
                f"{len(debriefing.weakness_identified)} weak areas identified"
            }
        ]
    }
