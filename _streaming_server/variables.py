import json
import os
import sys

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

trace_colors = px.colors.qualitative.Plotly
trace_colors[3] = "rgb(255,255,51)"

current_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.join("krakensdr_doa/", os.path.dirname(current_path))
shared_path = os.path.join(root_path, "_share")
# Load settings file
settings_file_path = os.path.join(shared_path, "settings.json")
settings_found = False
if os.path.exists(settings_file_path):
    settings_found = True
    with open(settings_file_path, "r") as myfile:
        dsp_settings = json.loads(myfile.read())
else:
    dsp_settings = dict()




# Import Kraken SDR modules
receiver_path = os.path.join(root_path, "_receiver")
signal_processor_path = os.path.join(root_path, "_signal_processing")
ui_path = os.path.join(root_path, "_UI")

sys.path.insert(0, receiver_path)
sys.path.insert(0, signal_processor_path)
sys.path.insert(0, ui_path)

daq_subsystem_path = os.path.join(os.path.join(os.path.dirname(root_path), "heimdall_daq_fw"), "Firmware")
daq_preconfigs_path = os.path.join(os.path.join(os.path.dirname(root_path), "heimdall_daq_fw"), "config_files")
daq_config_filename = os.path.join(daq_subsystem_path, "daq_chain_config.ini")

sys.path.insert(0, daq_subsystem_path)

figure_font_size = 20

y = np.random.normal(0, 1, 2**1)
x = np.arange(2**1)

fig_layout = go.Layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    template="plotly_dark",
    showlegend=True,
    margin=go.layout.Margin(t=0),  # top margin
)
doa_fig = go.Figure(layout=fig_layout)

option = [{"label": "", "value": 1}]



DEFAULT_MAPPING_SERVER_ENDPOINT = "wss://map.krakenrf.com:2096"
