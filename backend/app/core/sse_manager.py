import asyncio

class SSEManager:
    def __init__(self):
        self.connections: list[asyncio.Queue] = []

    async def connect(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.connections.append(queue)
        return queue

    def disconnect(self, queue: asyncio.Queue):
        if queue in self.connections:
            self.connections.remove(queue)

    async def broadcast(self, event: str, data: dict):
        """Call this after any DB change to push updates to all clients."""
        message = {"event": event, "data": data}
        for queue in self.connections:
            await queue.put(message)

# Single shared instance used across the entire app
sse_manager = SSEManager()