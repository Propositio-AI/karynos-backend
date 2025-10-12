from service import generate_vision
from shared.lib.gRPC import Server, Servicer

class VisionServicer(Servicer):
    def __init__(self):
        super().__init__()

    @Servicer.method()
    def GenerateVision(self, persona: str, message: str):
        # response_data = generate_vision(persona, message)
        # return {"urls": response_data}
        return {"urls": []}

def main():
    server = Server(VisionServicer())
    server.serve()

if __name__ == '__main__':
    main()