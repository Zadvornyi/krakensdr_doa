import os
import subprocess

from dash import Input, Output, State, callback, dcc

# isort: off
from maindash import app, spectrum_fig, waterfall_fig, web_interface

# isort: on

from variables import (
    current_path,
)


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="btn-restart_sw", component_property="n_clicks")],
    prevent_initial_call=True
)
def restart_sw_btn(n_clicks):
    if n_clicks:
        web_interface.logger.info("Restarting Software")
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
        os.chdir(root_path)
        subprocess.Popen(["bash", "kraken_doa_start.sh"])


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="btn-restart_system", component_property="n_clicks")],
    prevent_initial_call=True
)
def restart_system_btn(n_clicks):
    if n_clicks:
        web_interface.logger.info("Restarting System")
        subprocess.call(["reboot"])


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="btn-shtudown_system", component_property="n_clicks")],
    prevent_initial_call=True
)
def shutdown_system_btn(n_clicks):
    if n_clicks:
        web_interface.logger.info("Shutting System Down")
        subprocess.call(["shutdown", "now"])


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="btn-clear_cache", component_property="n_clicks")],
    prevent_initial_call=True
)
def clear_cache_btn(n_clicks):
    if n_clicks:
        responce_text = "Clearing Python and Numba Caches"
        web_interface.logger.info(responce_text)
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
        os.chdir(root_path)
        subprocess.Popen(["bash", "kraken_doa_start.sh", "-c"])
        return responce_text
