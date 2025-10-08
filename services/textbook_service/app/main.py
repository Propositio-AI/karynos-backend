from core_service import generate_plan, generate_textbook, generate_structure
from shared.lib.gRPC.serve import Server, Servicer
from schema import (
    Element,
)

class TextbookServicer(Servicer):
    def __init__(self):
        super().__init__()

    @Servicer.method()
    def GenerateStructure(self, persona: str, query: str):
        return generate_structure(persona, query)  

    @Servicer.method(method_type="unary_stream")
    def GenerateElement(self, persona: str, structures: list, elements: list = []):
        yield from generate_textbook(persona, [Element(**structure) for structure in structures], elements)

    @Servicer.method(method_type="unary_stream")
    def GeneratePlan(self, persona: str, query: str):
        yield from generate_plan(persona, query)

def main():
    server = Server(TextbookServicer())
    server.serve()

if __name__ == '__main__':
    main()