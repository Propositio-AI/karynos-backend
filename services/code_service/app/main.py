from methods.generate_code import generate_code
from methods.exec_code import exec_code
from methods.exec_gen import exec_gen
from shared.lib.gRPC.serve import Server, Servicer
import json

class CodeServicer(Servicer):
    def __init__(self):
        super().__init__()

    @Servicer.method()
    def GenerateCode(self, request: str, query:str):
        code = generate_code(request, query)

        return code

    @Servicer.method()
    def ExecCode(self, code: str):
        result = exec_code(code)

        return result
    
    @Servicer.method()
    def GenExecCode(self, request:str, query: str):
        result = exec_gen(request, query)

        return result

def main():
    # print(exec_gen("", "1+1の計算をするコード"), flush=True)
    server = Server(CodeServicer())
    server.serve()

if __name__ == '__main__':
    main()