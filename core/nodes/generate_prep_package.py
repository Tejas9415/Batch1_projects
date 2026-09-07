from datetime import date, datetime

from core.llm import get_llm
from core.state import GraphState, PrepPackage

NEW_PREP_PROMPT = """
You are a interview prep coach. Give me a complete prep package from the details below:

Role:{role}
Company: {company}
{days_remaining} for the interview

Resume_analysis:
-Match Score: {match_score}/100
-Missing skills: {missing_skills}

Company_overview:
{company_overview}

Job Description:
{jd}

What you have to do?
- day_wise_plan : prep plan for {days_remaining} days (less number of days -> high-priority tasks first, more days-> thorough coverage and missing_skills coverage must)
- opening_pitch: 60-90 seconds answer of "tell me about yourself".
- company_talking_point: 3-4 points answer on what do you know about the company which can amaze the interviewer as well.
- mock_questions: 5 targeted questions (technical, behavioral, company_fit, resume_specific)
"""

DEBRIEF_PREP_PROMPT = """
You are an expert interview recovery and preparation coach.

Your job is to analyze a student's previous interview experience and create a
TARGETED COMEBACK PLAN for their next interview opportunity.

The student has already faced an interview at the company and struggled in a
specific round. Do NOT give generic interview preparation.

Your preparation must directly address:
1. What the student struggled with
2. Why they struggled
3. How their strengths can be leveraged
4. How their weaknesses should be corrected
5. What specific skills, concepts, communication patterns, or behaviors need
   improvement before the next interview
6. What is likely to be tested again based on the role, company, and previous
   round

-----------------------------------
STUDENT INTERVIEW DEBRIEF
-----------------------------------

Role: {role}
Company: {company}
Round where student faced difficulty: {round_name}
{days_line}

Strengths:
{strengths}

Weaknesses:
{weaknesses}

Root Causes of Difficulty:
{root_causes}

Company Overview:
{company_overview}



Days Available for Preparation:
{days_remaining}

-----------------------------------
YOUR TASK
-----------------------------------

Create a highly targeted comeback preparation package with the following:

### 1. day_wise_plan

Create a day-by-day preparation plan for {days_remaining} days.

The plan MUST be based on the student's previous interview failure points.

Prioritize:
- Root causes of failure first
- Critical weaknesses related to the failed round
- Topics/concepts that are likely to be tested again
- Practice and repetition of previously weak areas
- Mock interview practice
- Communication and confidence improvement where required
- Final revision and interview simulation

Rules:
- Fewer days → focus only on the highest-impact weaknesses and likely interview
  areas.
- More days → provide deeper concept coverage, repeated practice, mock
  interviews, and weakness correction.
- Do NOT spend significant preparation time on areas where the student is
  already strong unless they are highly relevant to the target role.
- Every day must have clear objectives, specific tasks, and expected outcomes.
- The plan should progressively move from "fix the weakness" → "practice" →
  "simulate the interview" → "final polish".

### 2. opening_pitch

Create a strong 60–90 second answer for:

"Tell me about yourself."

The answer should:
- Be relevant to the target Role and Company
- Highlight the student's strongest and most relevant experiences
- Naturally address the weaknesses/root causes indirectly by presenting the
  student's growth and learning
- Sound confident and authentic, not scripted
- Avoid mentioning that the student previously failed an interview
- Be suitable as the opening answer in the next interview

### 3. mock_questions

Create 5 highly targeted mock interview questions.

These questions MUST be derived from the student's previous interview experience.

Include a balanced mix of:
- Questions targeting the exact area where the student struggled
- Questions targeting the identified root causes
- Technical questions relevant to the Role
- Behavioral questions related to the student's weaknesses
- Company-fit questions
- Resume/experience-specific questions
- At least 1 question designed to test whether the student has actually
  corrected the previous weakness
- At least 1 challenging follow-up question

-----------------------------------
COMEBACK STRATEGY
-----------------------------------

The entire preparation package should answer one central question:

"What specifically should this student do differently in their next interview
to avoid repeating the mistakes from the previous interview?"

Use the student's Root Causes as the strongest signal.

Do not simply repeat the weaknesses.
Convert every weakness/root cause into an actionable preparation task,
practice exercise, or mock question.

The final output should be practical, specific, prioritized, and personalized
to this student's previous interview experience.
"""

def generate_prep_package(state:GraphState) -> dict:
    days_remaining = 7
    interview_date = state.get("interview_date","")

    if interview_date:
        try:
            days_remaining = max(0,(date.fromisoformat(interview_date) - date.today()).days)
        except ValueError:
            pass
    
    llm = get_llm(temperature=0.5)
    structured_llm = llm.with_structured_output(PrepPackage)

    company_overview = state.get("company_overview",{})
    overview_text = company_overview.get("summary") or company_overview.get("note") or "NO information fetched"

    if state["mode"] == "new_prep":
        resume_analysis = state["resume_analysis"]
        prompt = NEW_PREP_PROMPT.format(
            role = state.get("role_title","the role"),
            company = state["company_name"],
            days_remaining = days_remaining,
            match_score = resume_analysis.match_score,
            missing_skills = ", ".join(resume_analysis.missing_skills),
            company_overview = overview_text,
            jd = state["jd_text"]
        )
    else:
        debrief  = state["debrief_analysis"]
        days_line = {
            f"{days_remaining} for the next round"
            if interview_date 
            else "No date is confirmed for the next round give me general improvement plan"
        }

        prompt = DEBRIEF_PREP_PROMPT.format(
            role = state.get("role_title","the role"),
            company = state["company_name"],
            round_name = state.get("round_name","N/A"),
            days_line = days_line,
            days_remaining = days_remaining,
            company_overview = overview_text,
            strengths = ", ".join(debrief.strengths_shown) or "N/A",
            weaknesses = ", ".join(debrief.weaknesses_identified) or "N/A",
            root_causes = ", ".join(debrief.root_causes) or "N/A"
        )
    
    package: PrepPackage = structured_llm.invoke(prompt)
    package.days_remaining = days_remaining

    return {
        "prep_package": package,
        "messages":[
            {
            "role":"assistant",
            "content": f"[Prep Package] {days_remaining} day's plan, "
            f"{len(package.mock_questions)}mock questions ready"
        }
        ]
    }
