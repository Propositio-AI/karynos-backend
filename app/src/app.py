from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import websockets
import json
from .users.users import User

app = FastAPI()

AI_SERVER_URI = ""

async def ai_server_rcv(queue: asyncio.Queue, ai_ws: websockets.WebSocketClientProtocol):
    try:
        print("Connected to external API WebSocket")
        while True:
            message = await ai_ws.recv()
            data = json.loads(message)
            print(f"Received from ai_server: {data}")
            await queue.put(data)

    except Exception as e:
        print(f"AIServer connection error: {e}")
        await asyncio.sleep(5)

async def web_server_rcv(queue: asyncio.Queue, web_ws: WebSocket):
    try:
        while True:
            message = await web_ws.receive_text()
            data = json.loads(message)
            print(f"Received from web_server: {data}")
            await queue.put(data)
    
    except Exception as e:
        print(f"WebServer connection error: {e}")
        await asyncio.sleep(5)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

@app.websocket("/ws_api")
async def websocket_endpoint(web_ws: WebSocket):
    user = User()
    queue_ai_rcv = asyncio.Queue()
    queue_web_rcv = asyncio.Queue()
    while True:      
        try:
            async with websockets.connect(AI_SERVER_URI) as ai_ws:
                await web_ws.accept()
                print("WebSocket connection established")

                ai_rcv_task = asyncio.create_task(ai_server_rcv(queue_ai_rcv, ai_ws))
                web_rcv_task = asyncio.create_task(web_server_rcv(queue_web_rcv, web_ws))

                ai_rcv_data = asyncio.create_task(queue_ai_rcv.get())
                web_rcv_data = asyncio.create_task(queue_web_rcv.get())

                while True:
                    done, pending = await asyncio.wait(
                        [web_rcv_data, ai_rcv_data],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    if web_rcv_data in done:
                        iedeshozyo = web_rcv_data.result()
                        match iedeshozyo["type"]:
                            case "useropen":
                                send_data = user.open_user(iedeshozyo)
                            case "request":
                                send_data = user.open_request(iedeshozyo)
                                if send_data == "error":
                                    send_data = {
                                        "type":"response",
                                        "status":"error",
                                        "id":iedeshozyo["id"],
                                        "message":"ユーザーIDが登録されていません"
                                    }
                                    await web_ws.send_text(json.dumps(send_data))
                                else:
                                    await ai_ws.send(json.dumps(send_data))
                        web_rcv_data = asyncio.create_task(queue_web_rcv.get())

                    if ai_rcv_data in done:
                        iedeshozyo = ai_rcv_data.result()
                        send_data = user.response_save(iedeshozyo)
                        await web_ws.send_text(json.dumps(send_data))
                        ai_rcv_data = asyncio.create_task(queue_ai_rcv.get())

        except WebSocketDisconnect:
            print("WebSocket connection disconnected")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            try:
                ai_rcv_task.cancel()
                web_rcv_task.cancel()
            except Exception as e:
                print(f"Error canceling tasks: {e}")
            await web_ws.close()
            print("Retrying connection...")
            await asyncio.sleep(1)
