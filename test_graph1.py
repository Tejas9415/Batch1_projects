"""
test_day3_graph1.py
----------------------
Poora Graph 1 ka end-to-end test - interrupt + resume + retry loop live
dikhane ke liye.

Run: python test_day3_graph1.py
"""

from langgraph.types import Command

from core.graph import build_graph

app = build_graph()

# thread_id = is student's session ka unique identifier. Checkpointer
# isi id se pata lagata hai "iska state kaha save kiya tha".
config = {"configurable": {"thread_id": "student-session-1"}}

initial_input = {
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

print("=== STEP 1: Graph shuru karo ===")
result = app.invoke(initial_input, config=config)

# Agar graph interrupt() tak pahunch gaya, result mein "__interrupt__"
# key hogi - poora state nahi milega, sirf interrupt() ka payload milega
if "__interrupt__" in result:
    interrupt_info = result["__interrupt__"][0]
    print("\n>>> GRAPH RUK GAYA HAI! Yeh poochha ja raha hai:")
    print(interrupt_info.value)

    # Yahan REAL app mein UI student se jawab lega. Test ke liye hum
    # dummy answers hardcode kar rahe hain.
    dummy_answers = {
        q["id"]: f"Dummy answer for: {q['text'][:40]}..."
        for q in interrupt_info.value["questions"]
    }

    print("\n=== STEP 2: Answers ke saath RESUME karo ===")
    result = app.invoke(Command(resume=dummy_answers), config=config)

    # Agar evaluation weak nikli, graph FIR SE interrupt hoga (retry loop)
    while "__interrupt__" in result:
        print("\n>>> RETRY LOOP: graph phir se ruk gaya (weak answers thay)")
        interrupt_info = result["__interrupt__"][0]
        retry_answers = {
            q["id"]: f"Better answer attempt for: {q['text'][:40]}..."
            for q in interrupt_info.value["questions"]
        }
        result = app.invoke(Command(resume=retry_answers), config=config)

print("\n=== FINAL REPORT ===")
print(result.get("final_report", "Report nahi bana - kuch check karo"))

print("\n=== Evaluation History (kitni baar evaluate hua) ===")
for i, ev in enumerate(result.get("evaluation_history", [])):
    print(f"Attempt {i+1}: score={ev.overall_score}")