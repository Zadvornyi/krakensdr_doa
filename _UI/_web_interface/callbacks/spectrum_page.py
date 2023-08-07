from dash import Input, Output
from maindash import app, web_interface
from utils import set_click_freq_spectrum


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input("spectrum-graph", "clickData")],
    prevent_initial_call=True,
)
def click_to_set_freq_spectrum(clickData):
    if clickData:
        set_click_freq_spectrum(web_interface, clickData)


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input("waterfall-graph", "clickData")],
    prevent_initial_call=True,
)
def click_to_set_waterfall_spectrum(clickData):
    if clickData:
        set_click_freq_spectrum(web_interface, clickData)
