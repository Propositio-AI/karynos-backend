class GraphState(dict):
    request: dict
    code: str
    result: str
    status: bool
    error: str
    try_count: int
