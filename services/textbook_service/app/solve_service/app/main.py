from service import solve_question
from shared.lib.gRPC import Server, Servicer

class SolveServicer(Servicer):
    def __init__(self):
        super().__init__()

    @Servicer.method()
    def solveMath(self, question: str):
        return solve_question(question)

def main():
    # print(solve_question(input(">>")))
    server = Server(SolveServicer())
    server.serve()

if __name__ == '__main__':
    main()