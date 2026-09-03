from __future__ import annotations
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

#Structured_output_schemas GRAPH 1

class ResumeSuggestions(BaseModel):
    original_line: str = Field(description= "Resume ki excat line jo weak hai")
    improved_line: str = Field(description= "Original_line ka imroved version jo better ho aur JD aligned ho")
    reason: str = Field(description="Why this particular change in important for this line, Give reason in 1 line")

class ResumeAnalysis(BaseModel):
    match_score: float = Field(ge=0, le=100, description="How much resume is matching with the JD")
    matched_skills: list[str] = Field(description="Skills from the resume which is matching with the JD required skills")
    missing_skills: list[str] = Field(description="Skills for JD which is not in the resume")
    suggestions: list[ResumeSuggestions] = Field(description="3-5 specific line-level improvenments")


#debriefing
class DebriefAnalysis(BaseModel):
    strengths_shown: list[str] = Field(description="interview me kya acha gaya, from the student perspective")
    weakness_identified: list[str] = Field(description="what went wrong and what student felt is weak part of interview")
    root_causes: list[str] = Field(description="Why this difficulty happens, what is the root cause for this problem")
    confidence_level: Literal["low","medium","high"] = Field(description="What is the overall confidence of the student")

class PrepDay(BaseModel):
    date: str
    focus: str = Field(description="What is the main focus area e.g, DSA revision + Company research")
    tasks: list[str] = Field(description="2-4 concrete tasks")

class InterviewQuestions(BaseModel):
    id : str
    text: str
    category: Literal["technical","behavioral","company_fit","resume_specific"]

class PrepPackage(BaseModel):
    days_remaining: int
    day_wise_plan: list[PrepDay]
    opening_pitch: str = Field(description="Tell me about yourself ka readymade answer based on your resume+JD+company")
    company_talking_points: list[str] = Field(description="3-4 points for the questions like what do you know about this Company")
    mock_questions: list[InterviewQuestions] = Field(description="5 targeted mock interview questions")

class QuestionFeedback(BaseModel):
    question_id: str
    score: float = Field(ge=0, le=100)
    feedback: str
    ideal_answer_points: list[str] = Field(description="What points must be in the ideal_answer")

class InterviewEvaluation(BaseModel):
    per_question_feedback: list[QuestionFeedback]
    overall_score: float= Field(ge=0, le=100)
    weak_areas: list[str]
    comeback_strategy: list[str] = Field(description="Concrete steps improve karne ke liye")


#Reducer
def _combine_evals(old: list[InterviewEvaluation], new: list[InterviewEvaluation]) -> list[InterviewEvaluation]:
    return operator.add(old or [], new or [])



#GRAPH 2
class TailoredResume(BaseModel):
    professional_summary : str = Field("2 to 3 lines summary , optimized for JD")
    skills_section: list[str] = Field(description= "skills, ordered based on JD-relevance ")
    experience_bullets: list[str] = Field(description="Rewritten bullets- quantified, JD keyword aligned but factually resume grounded. If no number is present instead of guessing give a [X] placeholder")



class GraphState(TypedDict, total = False):
    #--mode
    mode: Literal["new_prep","debrief"]

    #--input: new_prep
    resume_text: str
    jd_text: str

    # input - debrief

    round_name: str
    what_went_well: str
    what_went_wrong: str
    difficulty_faced: str