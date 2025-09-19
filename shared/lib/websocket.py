from fastapi import APIRouter, WebSocket
import asyncio

import json 
from functools import partial


from pydantic import BaseModel
from typing import Callable, Awaitable, Generator, Any

class WebSocketManager: 
    def __init__(self, router: APIRouter):
        self.router = router

    def websocket(self, path: str, schema: BaseModel):
        """
        

        
        """
        self.path = path
        self.schema = schema

        def decorator(func: Callable[[BaseModel, WebSocketManager], Awaitable[None]]):
            async def endpoint(ws: WebSocket):
                self.ws = ws
                self.index = 0
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
    
    async def send_start(self, data):
        self.index = 0
        await self.ws.send_text(json.dumps({
            "success": True,
            "data": data,
            "index": self.index
        }))

        self.index += 1


    async def send_data(self, data):
        if(self.index == 0): self.index = 1
        await self.ws.send_text(json.dumps({
            "success": True,
            "data": data,
            "index": self.index
        }))

        self.index += 1

    async def send_end(self, data = None):
        await self.ws.send_text(json.dumps({
            "success": True,
            "data": data,
            "last_index": self.index,
            "index": -1
        }))
        self.index = 0

    async def send_error(self, message: str):
        self.index = 0
        await self.ws.send_text(json.dumps({
            "success": True,
            "data": {"error": message},
            "index": -1
        }))


async def streamer(
    generator_func: Callable[[], Generator[Any, None, None]],
    handler: Callable[[Any], Awaitable[None]],
):
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def sync(queue, loop):    
        for res in generator_func(): 
            asyncio.run_coroutine_threadsafe(queue.put(res), loop)
        
        asyncio.run_coroutine_threadsafe(queue.put(None), loop)

    asyncio.get_running_loop().run_in_executor(None, partial(sync, queue, loop))

    while True:
        item = await queue.get()
        if item is None:
            break
        await handler(item)