from langgraph.graph import StateGraph, START, END

from methods.exec_gen.graph.state import GraphState
from methods.exec_gen.graph.node import gen_code_node, exec_code_node, routing

graph = StateGraph(GraphState)

graph.add_node("generate_code", gen_code_node)
graph.add_node("execute_code", exec_code_node)

graph.add_edge(START, "generate_code")
graph.add_edge("generate_code", "execute_code")
graph.add_conditional_edges(
    "execute_code",
    routing
)

graph_app = graph.compile()
