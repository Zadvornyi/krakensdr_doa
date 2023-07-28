import os

from dash import Input, Output, State, dcc

# isort: off
from maindash import app, spectrum_fig, waterfall_fig, web_interface

# isort: on

from utils import fetch_dsp_data, fetch_gps_data, set_clicked, settings_change_watcher
from variables import daq_config_filename, settings_file_path


# ============================================
#          CALLBACK FUNCTIONS
# ============================================
@app.callback(
    Output("dummy_output", "children"),
    Input(component_id="settings-refresh-timer", component_property="disabled"),
)
def init_app(event):
    print(event, "init_app")
    fetch_dsp_data(app, web_interface, spectrum_fig, waterfall_fig)
    fetch_gps_data(app, web_interface)
    settings_change_watcher(web_interface, settings_file_path)


# TODO: it was  callback_shared
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
    if n_clicks:
        web_interface.logger.info("Saving DAQ and DSP Configuration")
        web_interface.save_configuration()


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input("spectrum-graph", "clickData")],
    prevent_initial_call=True,
)
def click_to_set_freq_spectrum(clickData):
    print(clickData, "click_to_set_freq_spectrum")
    set_clicked(web_interface, clickData)


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input("waterfall-graph", "clickData")],
    prevent_initial_call=True,
)
def click_to_set_waterfall_spectrum(clickData):
    print(clickData, "click_to_set_waterfall_spectrum")
    set_clicked(web_interface, clickData)


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input("en_beta_features", "value")],
    prevent_initial_call=True,
)
def toggle_beta_features(toggle_value):
    web_interface.en_beta_features = toggle_value

    toggle_output = []

    # Toggle VFO default configuration settings
    if toggle_value:
        toggle_output.append(Output("beta_features_container", "style", {"display": "block"}))
    else:
        toggle_output.append(Output("beta_features_container", "style", {"display": "none"}))

    # Toggle individual VFO card settings
    for i in range(web_interface.module_signal_processor.max_vfos):
        if toggle_value:
            toggle_output.append(Output("beta_features_container " + str(i), "style", {"display": "block"}))
        else:
            toggle_output.append(Output("beta_features_container " + str(i), "style", {"display": "none"}))

    return toggle_output

# @app.callback(
#     Output("placeholder_update_rx", "children"),
#     Input("settings-refresh-timer", "n_intervals"),
#     [State("url", "pathname")],
# )
# def settings_change_refresh(toggle_value, pathname):
#     print(toggle_value, web_interface.needs_refresh, pathname, 'settings_change_refresh')
#     # if web_interface.needs_refresh:
#     #     if pathname == "/" or pathname == "/init" or pathname == "/config":
#     #         return "upd"
#     #
#     # return 'settings_change_refresh'
