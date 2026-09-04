"""
test_day2.py
------------
SIRF Day 2 milestone ke liye - 2 nodes ko chalta hua dekhne ke liye ek
chhota, temporary graph. Kal (Day 3) poora 6-node graph.py isko replace
kar dega.

Run: python test_day2.py
"""

from langgraph.graph import END, START, StateGraph

from core.nodes.analyze_input import analyze_input_node
from core.nodes.fetch_company_info import fetch_company_info_node
from core.state import GraphState

# Concept: StateGraph banane ke 3 steps - nodes add karo, edges add karo, compile karo
builder = StateGraph(GraphState)

builder.add_node("analyze_input", analyze_input_node)
builder.add_node("fetch_company_info", fetch_company_info_node)

builder.add_edge(START, "analyze_input")
builder.add_edge("analyze_input", "fetch_company_info")
builder.add_edge("fetch_company_info", END)

app = builder.compile()

if __name__ == "__main__":
    result = app.invoke(
        {
            "mode": "new_prep",
            "resume_text": (
                "B.Tech CS student. Skills: Python, Java, SQL, Git. Built a "
                "college project management system using Flask."
            ),
            "jd_text": (
                "Looking for SDE Intern with strong Python, REST API design, "
                "SQL, and Docker knowledge."
            ),
            "company_name": "Infosys",
            "role_title": "SDE Intern",
        }
    )

    print("\n--- Progress messages ---")
    for msg in result["messages"]:
        print(">>", msg.content)

    print("\n--- Resume Analysis ---")
    print(result["resume_analysis"])

    print("\n--- Company Overview (real Wikipedia data) ---")
    print(result["company_overview"])