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

from kraken_web_doa import init_plot_doa
from kraken_web_interface import WebInterface
from kraken_web_spectrum import init_spectrum_fig
from quart import Quart, websocket
from variables import doa_fig, fig_layout, trace_colors
from waterfall import init_waterfall
from utils import fetch_dsp_data
app = Quart(__name__)


#############################################
#          Prepare Dash application         #
############################################
web_interface = WebInterface()
# print(web_interface.module_signal_processor.__dict__)
#############################################
#       Prepare component dependencies      #
#############################################
spectrum_fig = init_spectrum_fig(web_interface, fig_layout, trace_colors)
waterfall_fig = init_waterfall(web_interface)
doa_fig = init_plot_doa(web_interface, doa_fig)

@app.websocket("/krakenrf_data")
async def krakenrf_data():

    while True:
        fetch_dsp_data(web_interface)
        output = json.dumps({
            "daq_update_rate": web_interface.daq_update_rate,
            "daq_conn_status": web_interface.daq_conn_status
        })
        await websocket.send(output)
        await asyncio.sleep(1)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
