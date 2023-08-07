import os

from dash import clientside_callback, Input, Output, State, dcc

# isort: off
from maindash import app, spectrum_fig, waterfall_fig, web_interface

# isort: on
from kraken_web_doa import plot_doa
from kraken_web_spectrum import plot_spectrum
from utils import fetch_dsp_data, settings_change_watcher
from variables import settings_file_path
from views import daq_status_card


# ============================================
#          CALLBACK FUNCTIONS
# ============================================


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [
        Input(component_id="filename_input", component_property="value"),
        Input(component_id="en_data_record", component_property="value"),
        Input(component_id="write_interval_input", component_property="value"),
    ],
    prevent_initial_call=True,
)
def update_data_recording_params(filename, en_data_record, write_interval):
    print(filename, en_data_record, write_interval, "update_data_recording_params")
    # web_interface.module_signal_processor.data_recording_file_name = filename
    web_interface.module_signal_processor.update_recording_filename(filename)
    # TODO: Call sig processor file update function here

    if en_data_record is not None and len(en_data_record):
        web_interface.module_signal_processor.en_data_record = True
    else:
        web_interface.module_signal_processor.en_data_record = False

    web_interface.module_signal_processor.write_interval = float(write_interval)


@app.callback(Output("download_recorded_file", "data"), [Input("btn_download_file", "n_clicks")])
def send_recorded_file(n_clicks):
    if n_clicks:
        return dcc.send_file(
            os.path.join(
                os.path.join(
                    web_interface.module_signal_processor.root_path,
                    web_interface.module_signal_processor.data_recording_file_name,
                )
            )
        )


# Set DOA Output Format
@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="doa_format_type", component_property="value")],
    prevent_initial_call=True,
)
def set_doa_format(doa_format):
    if doa_format:
        web_interface.module_signal_processor.DOA_data_format = doa_format


# Update Station ID
@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="station_id_input", component_property="value")],
    prevent_initial_call=True,
)
def set_station_id(station_id):
    if station_id:
        web_interface.module_signal_processor.station_id = station_id


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="krakenpro_key", component_property="value")],
    prevent_initial_call=True,
)
def set_kraken_pro_key(key):
    if key:
        web_interface.module_signal_processor.krakenpro_key = key


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="rdf_mapper_server_address", component_property="value")],
    prevent_initial_call=True,
)
def set_rdf_mapper_server(url):
    web_interface.module_signal_processor.RDF_mapper_server = url


# Enable of Disable Kraken Pro Key Box
@app.callback(
    [Output("krakenpro_field", "style"), Output("rdf_mapper_server_address_field", "style")],
    [Input("doa_format_type", "value")],
)
def toggle_kraken_pro_key(doa_format_type):
    kraken_pro_field_style = {"display": "block"} if doa_format_type == "Kraken Pro Remote" else {"display": "none"}
    rdf_mapper_server_address_field_style = (
        {"display": "block"}
        if doa_format_type == "RDF Mapper" or doa_format_type == "Full POST"
        else {"display": "none"}
    )
    return kraken_pro_field_style, rdf_mapper_server_address_field_style


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="btn-start_proc", component_property="n_clicks")],
    prevent_initial_call=True,
)
def start_proc_btn(n_clicks):
    if n_clicks:
        web_interface.logger.info("Start pocessing btn pushed")
        web_interface.start_processing()


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="btn-stop_proc", component_property="n_clicks")],
    prevent_initial_call=True,
)
def stop_proc_btn(n_clicks):
    if n_clicks:
        web_interface.logger.info("Stop pocessing btn pushed")
        web_interface.stop_processing()


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="btn-save_cfg", component_property="n_clicks")],
    prevent_initial_call=True,
)
def save_config_btn(n_clicks):
    resp_text = "Saving DAQ and DSP Configuration"
    if n_clicks:
        web_interface.logger.info(resp_text)
        web_interface.save_configuration()
        return resp_text


@app.callback(Output("daq_status_card", "children"), Input("settings-refresh-timer", "n_intervals"))
def update_daq_status_card(intervals):
    fetch_dsp_data(web_interface)
    settings_change_watcher(web_interface, settings_file_path)

    return daq_status_card.daq_status_content()


@app.callback([Output("spectrum-graph", "figure"), Output("waterfall-graph", "extendData")],
              Input("settings-refresh-timer", "n_intervals"))
def update_spectrum(intervals):
    fetch_dsp_data(web_interface)
    return plot_spectrum(web_interface, spectrum_fig, waterfall_fig)


@app.callback(Output("doa-graph", "extendData"), Input("settings-refresh-timer", "n_intervals"))
def update_doa_graph(intervals):
    fetch_dsp_data(web_interface)
    return plot_doa(web_interface)

# @app.callback(
#     Output("placeholder_update_rx", "children"),
#     Input("settings-refresh-timer", "n_intervals"),
#     [State("url", "pathname")],
# )
# def settings_change_refresh(intervals, pathname):
#     if web_interface.needs_refresh:
#         if pathname == "/" or pathname == "/init" or pathname == "/config":
#             return "upd"
#
#     return 'settings_change_refresh'
