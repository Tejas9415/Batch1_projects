from langgraph.graph import END, START, StateGraph


from core.nodes.docx_writer import docx_writer_node
from core.nodes.generate_tailored_resume import generate_tailored_resume_node
from core.nodes.score_resume import score_resume_node, score_tailored_resume_node
from core.state import GraphState

def build_resume_editor_graph():
    builder = StateGraph(GraphState)

    builder.add_node("score_resume",score_resume_node)
    builder.add_node("generate_tailored_resume",generate_tailored_resume_node)
    builder.add_node("score_tailored_resume",score_tailored_resume_node)
    builder.add_node("docx_writer",docx_writer_node)


    builder.add_edge(START, "score_resume")
    builder.add_edge("score_resume","generate_tailored_resume")
    builder.add_edge("generate_tailored_resume", "score_tailored_resume")
    builder.add_edge("score_tailored_resume", "docx_writer")
    builder.add_edge("docx_writer", END)


    return builder.compile()