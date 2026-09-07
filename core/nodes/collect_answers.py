from core.state import GraphState
from langgraph.types import interrupt

def collect_answers_node(state:GraphState) -> dict:
    questions = state["prep_package"].mock_questions

    response = interrupt({
        "instructions":"Give answers to the given questions, exactly the way you'll give in interviews",
        "questions":[{"id":q.id,"text":q.text, "category": q.category} for q in questions]
    })

    answers: dict[str, str] = response.get("answers",{})

    return {
        "answers": answers,
        "messages":[
            {
                "role":"assistant",
                "content": f"[Mock Interviews] {len(answers)} answers collected"
            }
        ]
    }