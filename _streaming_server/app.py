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
import queue
import sys
import time

from quart import Quart, websocket

# isort: off
from variables import (
    receiver_path,
)

# Import Kraken SDR modules
sys.path.insert(0, receiver_path)
from krakenSDR_receiver import ReceiverRTLSDR

# isort: on
import random

rx_data_que = queue.Queue(1)
# Instantiate and configure Kraken SDR modules
streaming_receiver = ReceiverRTLSDR(data_que=rx_data_que)
streaming_receiver.get_iq_online()
print(streaming_receiver.iq_samples, "iq_samples")
while True:
    # data_que = rx_data_que.get(False)
    # print(data_que[0], 'data_que')
    print(streaming_receiver.receiver_connection_status, "conection status")
    print(streaming_receiver.iq_samples, "iq_samples")
    time.sleep(3)
# app = Quart(__name__)
#
#
# @app.websocket("/krakenrf_data")
# async def krakenrf_data():
#     while True:
#         output = json.dumps({
#             "random": random(),
#         })
#         await websocket.send(output)
#         await asyncio.sleep(1)
#
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
