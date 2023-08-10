import asyncio
import json
import random
import os
import sys

from quart import Quart, websocket


current_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(os.path.dirname(current_path))
shared_path = os.path.join(root_path, "krakensdr_doa/_share")

# Import Kraken SDR modules
receiver_path = os.path.join(root_path, "_receiver")
signal_processor_path = os.path.join(root_path, "krakensdr_doa/_signal_processing")
ui_path = os.path.join(root_path, "krakensdr_doa/_UI/_web_interface")

sys.path.insert(0, receiver_path)
sys.path.insert(0, signal_processor_path)
sys.path.insert(0, ui_path)

#from krakenSDR_signal_processor import SignalProcessor
#from utils import fetch_dsp_data
# from kraken_web_interface import WebInterface

# web_interface = WebInterface()

app = Quart(__name__)



@app.websocket("/krakenrf_data")
async def krakenrf_data():

    while True:
        # fetch_dsp_data(web_interface)
        # print(web_interface.module_signal_processor.latitude, "websocket")
        output = json.dumps([random.random() for _ in range(10)])
        await websocket.send(output)
        await asyncio.sleep(1)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
