from methods.exec_gen.graph.main import graph_app

def exec_gen(request:str, query: str):
    state = graph_app.invoke({
        "request": {"request":request,  "query": query},
        "try_count": 0
    })

    return state.get("result")