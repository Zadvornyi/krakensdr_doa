import asyncio
import json
import random

from quart import Quart, websocket

app = Quart(__name__)


@app.websocket("/krakenrf_data")
async def krakenrf_data():
    print("websocket")
    while True:
        output = json.dumps([random.random() for _ in range(10)])
        await websocket.send(output)
        await asyncio.sleep(1)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
