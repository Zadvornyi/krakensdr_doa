# KrakenSDR Signal Processor
#
# Copyright (C) 2018-2023  Carl Laufer, Tamás Pető, Mykola Dvornik, Andrii Zadvornyi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# - coding: utf-8 -*-

import asyncio
import json
from quart import websocket, Quart
import random

app = Quart(__name__)


@app.websocket("/krakenrf_data")
async def krakenrf_data():
    while True:
        output = json.dumps({
            "random": random(),
        })
        await websocket.send(output)
        await asyncio.sleep(1)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
