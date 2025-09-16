from fastapi import APIRouter, WebSocket
import asyncio

import json 
from functools import partial


from pydantic import BaseModel
from typing import Callable, Awaitable, Generator, Any

class WebSocketManager:
    def __init__(self, router: APIRouter, path: str, schema: BaseModel): 
        """
        
        fastAPI用のWebSocketクラス

        """
        
        self.ws: WebSocket = None
        self.router: APIRouter = router
        self.path: str = path
        self._handlers: dict[str, Callable] = {}
        self.schema: BaseModel = schema

    def websocket(self):
        """
        

        
        """

        def decorator(func: Callable[[BaseModel, WebSocketManager], Awaitable[None]]):
            async def endpoint(ws: WebSocket):
                self.ws = ws
                await ws.accept()
                manager = self
                try:
                    while True:
                        raw = await ws.receive_text()
                        msg = json.loads(raw)
                        await func(self.schema(**msg), manager)
                except Exception as e:
                    await manager.send_error(str(e))

            self.router.websocket(self.path)(endpoint)
        return decorator

    async def send_update(self, id: str, update, is_end: bool = False):
        await self.ws.send_text(json.dumps({
            "id": id,
            "data": update,
            "isEnd": is_end
        }))

    async def send_end(self, id: str, data = None):
        await self.ws.send_text(json.dumps({
            "id": id,
            "data": data,
            "isEnd": True
        }))

    async def send_error(self, message: str):
        await self.ws.send_text(json.dumps({
            "id": None,
            "update": {"error": message},
            "isEnd": True
        }))



async def streamer(
    generator_func: Callable[[], Generator[Any, None, None]],
    handler: Callable[[Any], Awaitable[None]],
):
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def sync(queue, loop):    
        for res in generator_func(): 
            print(res, flush=True)
            asyncio.run_coroutine_threadsafe(queue.put(res), loop)
        asyncio.run_coroutine_threadsafe(queue.put(None), loop)

    asyncio.get_running_loop().run_in_executor(None, partial(sync, queue, loop))

    while True:
        item = await queue.get()
        if item is None:
            break
        await handler(item)