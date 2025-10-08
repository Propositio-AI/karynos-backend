from service import generate_exercise
from shared.lib.gRPC import Server, Servicer

class ExerciseServicer(Servicer):
    def __init__(self):
        super().__init__()
        
    @Servicer.method()
    def GenerateExercise(self, persona: str, title: str, message: str, textbook: str):
        return generate_exercise(persona, title, message, textbook)
    
def main():
    server = Server(ExerciseServicer())
    server.serve()

if __name__ == '__main__':
    main()