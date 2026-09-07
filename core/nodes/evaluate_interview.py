from typing import Literal
from langgraph.types import Command

from core.llm import get_llm
from core.state import GraphState, InterviewEvaluation

MAX_RETRIES = 2
Threshold_score = 80

EVAL_PROMPT = """
You are a strict but fair interview evaluator. Given below are Q&A pairs, evaluate them.
{qa_pairs}

For every question:
- score between 0-100 based on quality of answer
- feedback - what's good in the answer and what's the missing part
- ideal_answer_points: what points must be in the answer so that answer can be perfect

Overall:
- overall_score: weighted average for all the questions
- weak_areas: weak topic/skills
- comeback_strategy: 2-3 concrete steps for best comeback
"""

def evaluate_interview_node(state: GraphState) -> Command[Literal["collect_answers","compile_report"]]:
    questions = {q.id: q for q in state["prep_package"].mock_questions}
    answers = state.get("answers",{})

    qa_lines = []
    for qid, question in questions.items():
        answer = answers.get(qid,"NO answer")
        qa_lines.append(f"Q({question.category}):{question.text}\n A: {answer}\n")
    
    qa_block = "\n".join(qa_lines)

    llm= get_llm(temperature=0)
    structured_llm = llm.with_structured_output(InterviewEvaluation)
    evaluation: InterviewEvaluation = structured_llm.invoke(EVAL_PROMPT.format(qa_pairs =qa_block))

    retry_count = state.get("retry_count",0)
    log_msg = {
        "role":"assistant",
        "content": f"[Evaluation] attempt #{retry_count+1} -> overall_score = {evaluation.overall_score}/100"
    }

    if evaluation.overall_score < Threshold_score and  retry_count< MAX_RETRIES:
        return Command(
            goto = "collect_answers",
            update = {
                "evaluation_history":[evaluation],
                "retry_count": retry_count+1,
                "messages": [log_msg]
            }
        )
    
    return Command(
        goto = "compile_report",
        update = {
                "evaluation_history":[evaluation],
                "messages": [log_msg]
            }
    )