from shared.lib.gRPC.client import gRPC_Client
from shared.lib.gRPC.serve import Server, Servicer
from shared.utils import readText, createPromptTemplate
from shared.lib.error import BaseError

# パス定義
STYLE_PROMPT_PATH = "./shared/prompts/style_prompt.txt"

# プロンプトの読み込み
STYLE_PROMPT = readText(STYLE_PROMPT_PATH)

class ChatServicer(Servicer):
    def __init__(self):
        super().__init__()
        
    @Servicer.method(method_type="unary_stream")
    def ChatInvoke(self, query: str):
        input = createPromptTemplate(STYLE_PROMPT, query),

        # LLMで推論
        for netSuccess, netRes, netError in gRPC_Client("LLM").call_server_stream("GeneralInvoke", {
            "input": input
        }):
            if netSuccess:
                serverSuccess, serverResponse, serverError = netRes
                
                if serverSuccess:
                    yield serverResponse
            
            else: raise netError
            
    
def main():
    server = Server(ChatServicer())
    server.serve()

if __name__ == '__main__':
    main()