from langgraph.graph import END, START, StateGraph

from core.db import get_checkpointer
from core.nodes.analyze_input import analyze_input_node
from core.nodes.collect_answers import collect_answers_node
from core.nodes.compile_report import compile_report_node
from core.nodes.evaluate_interview import evaluate_interview_node
from core.nodes.fetch_company_info import fetch_company_info_node
from core.nodes.generate_prep_package import generate_prep_package
from core.state import GraphState

def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("analyze_input",analyze_input_node)
    builder.add_node("fetch_company",fetch_company_info_node)
    builder.add_node("generate_prep_package",generate_prep_package)
    builder.add_node("collect_answers",collect_answers_node)
    builder.add_node("evaluate_interview",evaluate_interview_node)
    builder.add_node("compile_report",compile_report_node)

    builder.add_edge(START,"analyze_input")
    builder.add_edge("analyze_input","fetch_company")
    builder.add_edge("fetch_company","generate_prep_package")
    builder.add_edge("generate_prep_package","collect_answers")
    builder.add_edge("collect_answers","evaluate_interview")

    builder.add_edge("compile_report", END)

    return builder.compile(checkpointer= get_checkpointer())