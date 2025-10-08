from service import generate_element
from shared.lib.gRPC import Server, Servicer


class ElementServicer(Servicer):
    def __init__(self):
        super().__init__()

    @Servicer.method()
    def GenerateDefinition(self, persona:str, title: str, message:str, textbook: str):
        return generate_element("定義", persona, title, message, textbook)

    @Servicer.method()
    def GenerateColumn(self, persona:str, title: str, message:str, textbook: str):
        return generate_element("コラム", persona, title, message, textbook)

    @Servicer.method()
    def GenerateFormula(self, persona:str, title: str, message:str, textbook: str):
        return generate_element("公式", persona, title, message, textbook)

    @Servicer.method()
    def GenerateSummary(self, persona:str, title: str, message:str, textbook: str):
        return generate_element("まとめ", persona, title, message, textbook)

    @Servicer.method()
    def GenerateText(self, persona:str, title: str, message:str, textbook: str):
        return generate_element("構成要素と構成要素のつなぎ", persona, title, message, textbook)

    @Servicer.method()
    def GenerateTheorem(self, persona:str, title: str, message:str, textbook: str):
        return generate_element("定理", persona, title, message, textbook)

def main():
    server = Server(ElementServicer())
    server.serve()

if __name__ == '__main__':
    main()