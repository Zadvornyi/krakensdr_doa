
from dash import Input, Output

# isort: off
from maindash import app, web_interface

# isort: on

from utils import (
    read_config_file_dict,
)

@app.callback(Output("adv-cfg-container", "style"), [Input("en_advanced_daq_cfg", "value")])
def toggle_adv_daq(toggle_value):
    web_interface.en_advanced_daq_cfg = toggle_value
    if toggle_value:
        return {"display": "block"}
    else:
        return {"display": "none"}


@app.callback(Output("basic-cfg-container", "style"), [Input("en_basic_daq_cfg", "value")])
def toggle_basic_daq(toggle_value):
    web_interface.en_basic_daq_cfg = toggle_value
    if toggle_value:
        return {"display": "block"}
    else:
        return {"display": "none"}


@app.callback(
    [Output("url", "pathname")],
    [
        Input("daq_cfg_files", "value"),
        Input("placeholder_recofnig_daq", "children"),
        Input("placeholder_update_rx", "children"),
    ],
)
def reload_cfg_page(config_fname, dummy_0, dummy_1):
    web_interface.daq_ini_cfg_dict = read_config_file_dict(config_fname)
    web_interface.tmp_daq_ini_cfg = web_interface.daq_ini_cfg_dict["config_name"]
    web_interface.needs_refresh = False

    return ["/config"]


@app.callback(Output("system_control_container", "style"), [Input("en_system_control", "value")])
def toggle_system_control(toggle_value):
    web_interface.en_system_control = toggle_value
    if toggle_value:
        return {"display": "block"}
    else:
        return {"display": "none"}

