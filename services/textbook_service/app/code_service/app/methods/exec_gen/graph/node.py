import json
from langchain_core.runnables import RunnableConfig
from typing import Literal
from langgraph.graph import END, START

from methods.exec_gen.graph.state import GraphState
from methods.generate_code import generate_code
from methods.exec_code import exec_code

def gen_code_node(state: GraphState):
    code = generate_code(
       request= state["request"].get("request", ""),
       query = state["request"].get("query", ""),
       code = state.get("code", ""),
       error = state.get("error", "")
    )

    return {"code": code}

def exec_code_node(state: GraphState):
    code = state["code"]

    status, result = exec_code(code)

    if status:
        return {"status": True, "result": result, "try_count": state["try_count"] + 1}
    else:
        return {"status": False, "error": result, "try_count": state["try_count"] + 1}

def routing(state: GraphState, config: RunnableConfig) -> Literal["generate_code", END]:
  if state["status"] or state["try_count"] >= 5: 
    return END
  else:
    return "generate_code"