# 実行パスを通す
import sys
sys.path.append("../")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import websockets

import json
import os

# ユーザー管理クラス
from .user import User
user = User()

class User(BaseModel):
    id: str

AI_SERVER_URI = os.environ["AI_SERVER_URI"]

app = FastAPI()

"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)
"""



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

@app.post("/newuser")
async def newUser(userData: User):
    user.open_user(userData.id)

    print(user.userID_list)

    return True


@app.websocket("/")
async def websocket_endpoint(web_ws: WebSocket):
    """
    
    Parameters
    ----------
        web_ws : WebSocket

    Returns
    ---------- 

    """
    print("Web サーバーからの接続がありました")

    queue_ai_rcv = asyncio.Queue()
    queue_web_rcv = asyncio.Queue()

    while True:      
        try:
            async with websockets.connect(AI_SERVER_URI) as ai_ws:
                await web_ws.accept()
                print("Web Server WebSocket connection established")

                ai_rcv_task = asyncio.create_task(ai_server_rcv(queue_ai_rcv, ai_ws))
                web_rcv_task = asyncio.create_task(web_server_rcv(queue_web_rcv, web_ws))

                ai_rcv_data = asyncio.create_task(queue_ai_rcv.get())
                web_rcv_data = asyncio.create_task(queue_web_rcv.get())

                while True:
                    done_task, _ = await asyncio.wait(
                        [web_rcv_data, ai_rcv_data],
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    # webサーバーからのWebSocketの処理
                    if web_rcv_data in done_task:
                        receive_data = web_rcv_data.result()

                        print(receive_data)

                        match receive_data["type"]:
                            
                            case "useropen":
                                user.open_user(receive_data)

                                web_ws.send_text("サーバーから送りまーす")

                            case "request":
                                send_data = user.open_request(receive_data)

                                if send_data == "error":

                                    send_data = {
                                        "type" : "response",
                                        "status" : "error",
                                        "id" : receive_data["id"],
                                        "message" : "ユーザーIDが登録されていません"
                                    }

                                    await web_ws.send_text(json.dumps(send_data))

                                else:
                                    await ai_ws.send(json.dumps(send_data))

                        web_rcv_data = asyncio.create_task(queue_web_rcv.get())

                    # aiサーバーからのWebSocketの処理
                    if ai_rcv_data in done_task:
                        receive_data = ai_rcv_data.result()

                        send_data = user.response_save(receive_data)

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
