import os
import subprocess
import dash
from dash import Input, Output, State, callback, dcc

# isort: off
from maindash import app, spectrum_fig, waterfall_fig, web_interface

# isort: on

from kraken_web_config import write_config_file_dict
from kraken_web_spectrum import init_spectrum_fig
from krakenSDR_receiver import ReceiverRTLSDR
from krakenSDR_signal_processor import SignalProcessor
from utils import (
    fetch_dsp_data,
    fetch_gps_data,
    read_config_file_dict,
    set_clicked,
    settings_change_watcher,
)
from variables import (
    current_path,
    daq_config_filename,
    daq_start_filename,
    daq_stop_filename,
    daq_subsystem_path,
    dsp_settings,
    fig_layout,
    root_path,
    settings_file_path,
    trace_colors,
)

# ============================================
#          CALLBACK FUNCTIONS
# ============================================
# @app.callback(
#     Output("dummy_output", "children", ""),
#     Input(component_id="url", component_property="loading_state")
# )
# def init_app(event):
#     print(event, 'init_app')
#     fetch_dsp_data(app, web_interface, spectrum_fig, waterfall_fig)
#     fetch_gps_data(app, web_interface)
#     settings_change_watcher(web_interface, settings_file_path)

# @app.callback(
#     Output("dummy_output", "children", ""),
#     [
#         Input(component_id="filename_input", component_property="value"),
#         Input(component_id="en_data_record", component_property="value"),
#         Input(component_id="write_interval_input", component_property="value"),
#     ],
# )
# def update_data_recording_params(filename, en_data_record, write_interval):
#     print(filename, 'update_data_recording_params')
#     # web_interface.module_signal_processor.data_recording_file_name = filename
#     web_interface.module_signal_processor.update_recording_filename(filename)
#     # TODO: Call sig processor file update function here
#
#     if en_data_record is not None and len(en_data_record):
#         web_interface.module_signal_processor.en_data_record = True
#     else:
#         web_interface.module_signal_processor.en_data_record = False
#
#     web_interface.module_signal_processor.write_interval = float(write_interval)


@app.callback(Output("download_recorded_file", "data"), [Input("btn_download_file", "n_clicks")])
def send_recorded_file(n_clicks):
    print(n_clicks, "send_recorded_file")
    return dcc.send_file(
        os.path.join(
            os.path.join(
                web_interface.module_signal_processor.root_path,
                web_interface.module_signal_processor.data_recording_file_name,
            )
        )
    )


#
# # Set DOA Output Format
# @app.callback(Output("dummy_output", "children", ""), [Input(component_id="doa_format_type", component_property="value")])
# def set_doa_format(doa_format):
#     print(doa_format, 'set_doa_format')
#     web_interface.module_signal_processor.DOA_data_format = doa_format
#
#
# # Update Station ID
# @app.callback(Output("dummy_output", "children", ""), [Input(component_id="station_id_input", component_property="value")])
# def set_station_id(station_id):
#     print(station_id, 'set_station_id')
#     web_interface.module_signal_processor.station_id = station_id
#
#
# @app.callback(Output("dummy_output", "children", ""), [Input(component_id="krakenpro_key", component_property="value")])
# def set_kraken_pro_key(key):
#     print(key, 'set_kraken_pro_key')
#     web_interface.module_signal_processor.krakenpro_key = key


# @app.callback(Output("dummy_output", "children", ""), [Input(component_id="rdf_mapper_server_address", component_property="value")])
# def set_rdf_mapper_server(url):
#     web_interface.module_signal_processor.RDF_mapper_server = url
#


# Enable GPS Relevant fields
@app.callback(
    [Output("fixed_heading_div", "style"), Output("gps_status_info", "style")], [Input("loc_src_dropdown", "value")]
)
def toggle_gps_fields(toggle_value):
    if toggle_value == "gpsd":
        return [{"display": "block"}, {"display": "block"}]
    else:
        return [{"display": "none"}, {"display": "none"}]


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


# Enable or Disable Heading Input Fields
@app.callback(
    Output("heading_field", "style"),
    [
        Input("loc_src_dropdown", "value"),
        Input(component_id="fixed_heading_check", component_property="value"),
    ],
    [State("heading_input", component_property="value")],
)
def toggle_heading_info(static_loc, fixed_heading, heading):
    if static_loc == "Static":
        web_interface.module_signal_processor.fixed_heading = True
        web_interface.module_signal_processor.heading = heading
        return {"display": "block"}
    elif static_loc == "gpsd" and fixed_heading:
        web_interface.module_signal_processor.heading = heading
        return {"display": "block"}
    elif static_loc == "gpsd" and not fixed_heading:
        web_interface.module_signal_processor.fixed_heading = False
        return {"display": "none"}
    elif static_loc == "None":
        web_interface.module_signal_processor.fixed_heading = False
        return {"display": "none"}
    else:
        return {"display": "none"}


# Enable or Disable Location Input Fields
@app.callback(Output("location_fields", "style"), [Input("loc_src_dropdown", "value")])
def toggle_location_info(toggle_value):
    web_interface.location_source = toggle_value
    if toggle_value == "Static":
        return {"display": "block"}
    else:
        return {"display": "none"}


# Enable or Disable Location Input Fields
@app.callback(
    Output("min_speed_heading_fields", "style"),
    [Input("loc_src_dropdown", "value"), Input("fixed_heading_check", "value")],
)
def toggle_min_speed_heading_filter(toggle_value, fixed_heading):
    web_interface.location_source = toggle_value
    if toggle_value == "gpsd" and not fixed_heading:
        return {"display": "block"}
    else:
        return {"display": "none"}


# # Set location data
# @app.callback_shared(
#     None,
#     [
#         Input(component_id="latitude_input", component_property="value"),
#         Input(component_id="longitude_input", component_property="value"),
#         Input("loc_src_dropdown", "value"),
#     ],
# )
# def set_static_location(lat, lon, toggle_value):
#     if toggle_value == "Static":
#         web_interface.module_signal_processor.latitude = lat
#         web_interface.module_signal_processor.longitude = lon
#
#
# # Enable Fixed Heading
# @app.callback(None, [Input(component_id="fixed_heading_check", component_property="value")])
# def set_fixed_heading(fixed):
#     if fixed:
#         web_interface.module_signal_processor.fixed_heading = True
#     else:
#         web_interface.module_signal_processor.fixed_heading = False
#
#
# # Set heading data
# @app.callback_shared(None, [Input(component_id="heading_input", component_property="value")])
# def set_static_heading(heading):
#     web_interface.module_signal_processor.heading = heading
#
#
# # Set minimum speed for trustworthy GPS heading
# @app.callback_shared(None, [Input(component_id="min_speed_input", component_property="value")])
# def set_min_speed_for_valid_gps_heading(min_speed):
#     web_interface.module_signal_processor.gps_min_speed_for_valid_heading = min_speed
#
#
# # Set minimum speed duration for trustworthy GPS heading
# @app.callback_shared(None, [Input(component_id="min_speed_duration_input", component_property="value")])
# def set_min_speed_duration_for_valid_gps_heading(min_speed_duration):
#     web_interface.module_signal_processor.gps_min_duration_for_valid_heading = min_speed_duration
#
#
# Enable GPS (note that we need this to fire on load, so we cannot use callback_shared!)
@app.callback(
    [Output("gps_status", "children"), Output("gps_status", "style")],
    [Input("loc_src_dropdown", "value")],
)
def enable_gps(toggle_value):
    if toggle_value == "gpsd":
        status = web_interface.module_signal_processor.enable_gps()
        if status:
            web_interface.module_signal_processor.usegps = True
            return ["Connected", {"color": "#7ccc63"}]
        else:
            return ["Error", {"color": "#e74c3c"}]
    else:
        web_interface.module_signal_processor.usegps = False
        return ["-", {"color": "white"}]


# @app.callback_shared(None, web_interface.vfo_cfg_inputs)
# def update_vfo_params(*args):
#     # Get dict of input variables
#     input_names = [item.component_id for item in web_interface.vfo_cfg_inputs]
#     kwargs_dict = dict(zip(input_names, args))
#
#     web_interface.module_signal_processor.spectrum_fig_type = kwargs_dict["spectrum_fig_type"]
#     web_interface.module_signal_processor.vfo_mode = kwargs_dict["vfo_mode"]
#     web_interface.module_signal_processor.vfo_default_demod = kwargs_dict["vfo_default_demod"]
#     web_interface.module_signal_processor.vfo_default_iq = kwargs_dict["vfo_default_iq"]
#     web_interface.module_signal_processor.max_demod_timeout = int(kwargs_dict["max_demod_timeout"])
#
#     active_vfos = kwargs_dict["active_vfos"]
#     # If VFO mode is in the VFO-0 Auto Max mode, we active VFOs to 1 only
#     if kwargs_dict["vfo_mode"] == "Auto":
#         active_vfos = 1
#         app.push_mods({"active_vfos": {"value": 1}})
#
#     web_interface.module_signal_processor.dsp_decimation = max(int(kwargs_dict["dsp_decimation"]), 1)
#     web_interface.module_signal_processor.active_vfos = active_vfos
#     web_interface.module_signal_processor.output_vfo = kwargs_dict["output_vfo"]
#
#     en_optimize_short_bursts = kwargs_dict["en_optimize_short_bursts"]
#     if en_optimize_short_bursts is not None and len(en_optimize_short_bursts):
#         web_interface.module_signal_processor.optimize_short_bursts = True
#     else:
#         web_interface.module_signal_processor.optimize_short_bursts = False
#
#     for i in range(web_interface.module_signal_processor.max_vfos):
#         if i < kwargs_dict["active_vfos"]:
#             app.push_mods({"vfo" + str(i): {"style": {"display": "block"}}})
#         else:
#             app.push_mods({"vfo" + str(i): {"style": {"display": "none"}}})
#
#     if web_interface.daq_fs > 0:
#         bw = web_interface.daq_fs / web_interface.module_signal_processor.dsp_decimation
#         vfo_min = web_interface.daq_center_freq - bw / 2
#         vfo_max = web_interface.daq_center_freq + bw / 2
#
#         for i in range(web_interface.module_signal_processor.max_vfos):
#             web_interface.module_signal_processor.vfo_bw[i] = int(
#                 min(kwargs_dict["vfo_" + str(i) + "_bw"], bw * 10**6)
#             )
#             web_interface.module_signal_processor.vfo_fir_order_factor[i] = int(
#                 kwargs_dict["vfo_" + str(i) + "_fir_order_factor"]
#             )
#             web_interface.module_signal_processor.vfo_freq[i] = int(
#                 max(min(kwargs_dict["vfo_" + str(i) + "_freq"], vfo_max), vfo_min) * 10**6
#             )
#             web_interface.module_signal_processor.vfo_squelch[i] = int(kwargs_dict["vfo_" + str(i) + "_squelch"])
#             web_interface.module_signal_processor.vfo_demod[i] = kwargs_dict[f"vfo_{i}_demod"]
#             web_interface.module_signal_processor.vfo_iq[i] = kwargs_dict[f"vfo_{i}_iq"]
#
#
# @app.callback_shared(
#     None,
#     [Input(component_id="btn-start_proc", component_property="n_clicks")],
# )
# def start_proc_btn(input_value):
#     web_interface.logger.info("Start pocessing btn pushed")
#     web_interface.start_processing()
#
#
# @app.callback_shared(
#     None,
#     [Input(component_id="btn-stop_proc", component_property="n_clicks")],
# )
# def stop_proc_btn(input_value):
#     web_interface.logger.info("Stop pocessing btn pushed")
#     web_interface.stop_processing()
#
#
# @app.callback_shared(
#     None,
#     [Input(component_id="btn-save_cfg", component_property="n_clicks")],
# )
# def save_config_btn(input_value):
#     web_interface.logger.info("Saving DAQ and DSP Configuration")
#     web_interface.save_configuration()
#
#
# @app.callback_shared(
#     None,
#     [Input(component_id="btn-restart_sw", component_property="n_clicks")],
# )
# def restart_sw_btn(input_value):
#     web_interface.logger.info("Restarting Software")
#     root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
#     os.chdir(root_path)
#     subprocess.Popen(["bash", "kraken_doa_start.sh"])  # ,
#
#
# @app.callback_shared(
#     None,
#     [Input(component_id="btn-restart_system", component_property="n_clicks")],
# )
# def restart_system_btn(input_value):
#     web_interface.logger.info("Restarting System")
#     subprocess.call(["reboot"])
#
#
# @app.callback_shared(
#     None,
#     [Input(component_id="btn-shtudown_system", component_property="n_clicks")],
# )
# def shutdown_system_btn(input_value):
#     web_interface.logger.info("Shutting System Down")
#     subprocess.call(["shutdown", "now"])
#
#
# @app.callback_shared(
#     None,
#     [Input(component_id="btn-clear_cache", component_property="n_clicks")],
# )
# def clear_cache_btn(input_value):
#     web_interface.logger.info("Clearing Python and Numba Caches")
#     root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
#     os.chdir(root_path)
#     subprocess.Popen(["bash", "kraken_doa_start.sh", "-c"])  # ,
#
#
# @app.callback_shared(None, [Input("spectrum-graph", "clickData")])
# def click_to_set_freq_spectrum(clickData):
#     set_clicked(web_interface, clickData)
#
#
# @app.callback_shared(None, [Input("waterfall-graph", "clickData")])
# def click_to_set_waterfall_spectrum(clickData):
#     set_clicked(web_interface, clickData)
#
#

#
# @app.callback(
#     Output("dummy_output", "children", ""),
#     [
#         Input("cfg_rx_channels", "value"),
#         Input("cfg_daq_buffer_size", "value"),
#         Input("cfg_sample_rate", "value"),
#         Input("en_noise_source_ctr", "value"),
#         Input("cfg_cpi_size", "value"),
#         Input("cfg_decimation_ratio", "value"),
#         Input("cfg_fir_bw", "value"),
#         Input("cfg_fir_tap_size", "value"),
#         Input("cfg_fir_window", "value"),
#         Input("en_filter_reset", "value"),
#         Input("cfg_corr_size", "value"),
#         Input("cfg_std_ch_ind", "value"),
#         Input("en_iq_cal", "value"),
#         Input("cfg_gain_lock", "value"),
#         Input("en_req_track_lock_intervention", "value"),
#         Input("cfg_cal_track_mode", "value"),
#         Input("cfg_amplitude_cal_mode", "value"),
#         Input("cfg_cal_frame_interval", "value"),
#         Input("cfg_cal_frame_burst_size", "value"),
#         Input("cfg_amplitude_tolerance", "value"),
#         Input("cfg_phase_tolerance", "value"),
#         Input("cfg_max_sync_fails", "value"),
#         Input("cfg_data_block_len", "value"),
#         Input("cfg_recal_interval", "value"),
#         Input("cfg_en_bias_tee", "value"),
#         Input("cfg_iq_adjust_source", "value"),
#         Input("cfg_iq_adjust_amplitude", "value"),
#         Input("cfg_iq_adjust_time_delay_ns", "value"),
#     ],
# )
# def update_daq_ini_params(
#     cfg_rx_channels,
#     cfg_daq_buffer_size,
#     cfg_sample_rate,
#     en_noise_source_ctr,
#     cfg_cpi_size,
#     cfg_decimation_ratio,
#     cfg_fir_bw,
#     cfg_fir_tap_size,
#     cfg_fir_window,
#     en_filter_reset,
#     cfg_corr_size,
#     cfg_std_ch_ind,
#     en_iq_cal,
#     cfg_gain_lock,
#     en_req_track_lock_intervention,
#     cfg_cal_track_mode,
#     cfg_amplitude_cal_mode,
#     cfg_cal_frame_interval,
#     cfg_cal_frame_burst_size,
#     cfg_amplitude_tolerance,
#     cfg_phase_tolerance,
#     cfg_max_sync_fails,
#     cfg_data_block_len,
#     cfg_recal_interval,
#     cfg_en_bias_tee,
#     cfg_iq_adjust_source,
#     cfg_iq_adjust_amplitude,
#     cfg_iq_adjust_time_delay_ns,
#     config_fname=daq_config_filename,
# ):
#     ctx = dash.callback_context
#     component_id = ctx.triggered[0]["prop_id"].split(".")[0]
#     if ctx.triggered:
#         if len(ctx.triggered) == 1:  # User manually changed one parameter
#             web_interface.tmp_daq_ini_cfg = "Custom"
#
#         # If the input was from basic DAQ config, update the actual DAQ params
#         if component_id == "cfg_data_block_len" or component_id == "cfg_recal_interval":
#             if not cfg_data_block_len or not cfg_recal_interval:
#                 # [no_update, no_update, no_update, no_update]
#                 return Output("dummy_output", "children", "")
#
#             cfg_daq_buffer_size = 262144  # This is a reasonable DAQ buffer size to use
#
#             decimated_bw = ((cfg_sample_rate * 10**6) / cfg_decimation_ratio) / 10**3
#             cfg_cpi_size = round((cfg_data_block_len / 10**3) * decimated_bw * 10**3)
#             cfg_cal_frame_interval = round((cfg_recal_interval * 60) / (cfg_data_block_len / 10**3))
#
#             while cfg_decimation_ratio * cfg_cpi_size < cfg_daq_buffer_size:
#                 cfg_daq_buffer_size = (int)(cfg_daq_buffer_size / 2)
#
#             app.push_mods(
#                 {
#                     "cfg_cpi_size": {"value": cfg_cpi_size},
#                     "cfg_cal_frame_interval": {"value": cfg_cal_frame_interval},
#                     "cfg_fir_tap_size": {"value": cfg_fir_tap_size},
#                     "cfg_daq_buffer_size": {"value": cfg_daq_buffer_size},
#                 }
#             )
#
#         # If we updated advanced daq, update basic DAQ params
#         elif (
#             component_id == "cfg_sample_rate"
#             or component_id == "cfg_decimation_ratio"
#             or component_id == "cfg_cpi_size"
#             or component_id == "cfg_cal_frame_interval"
#         ):
#             if not cfg_sample_rate or not cfg_decimation_ratio or not cfg_cpi_size:
#                 # [no_update, no_update, no_update, no_update]
#                 return Output("dummy_output", "children", "")
#
#             decimated_bw = ((cfg_sample_rate * 10**6) / cfg_decimation_ratio) / 10**3
#
#             cfg_data_block_len = cfg_cpi_size / (decimated_bw)
#             cfg_recal_interval = (cfg_cal_frame_interval * (cfg_data_block_len / 10**3)) / 60
#
#             app.push_mods(
#                 {
#                     "cfg_data_block_len": {"value": cfg_data_block_len},
#                     "cfg_recal_interval": {"value": cfg_recal_interval},
#                 }
#             )
#
#     # Write calculated daq params to the ini param_dict
#     param_dict = web_interface.daq_ini_cfg_dict
#     param_dict["config_name"] = "Custom"
#     param_dict["num_ch"] = cfg_rx_channels
#     param_dict["en_bias_tee"] = cfg_en_bias_tee
#     param_dict["daq_buffer_size"] = cfg_daq_buffer_size
#     param_dict["sample_rate"] = int(cfg_sample_rate * 10**6)
#     param_dict["en_noise_source_ctr"] = 1 if len(en_noise_source_ctr) else 0
#     param_dict["cpi_size"] = cfg_cpi_size
#     param_dict["decimation_ratio"] = cfg_decimation_ratio
#     param_dict["fir_relative_bandwidth"] = cfg_fir_bw
#     param_dict["fir_tap_size"] = cfg_fir_tap_size
#     param_dict["fir_window"] = cfg_fir_window
#     param_dict["en_filter_reset"] = 1 if len(en_filter_reset) else 0
#     param_dict["corr_size"] = cfg_corr_size
#     param_dict["std_ch_ind"] = cfg_std_ch_ind
#     param_dict["en_iq_cal"] = 1 if len(en_iq_cal) else 0
#     param_dict["gain_lock_interval"] = cfg_gain_lock
#     param_dict["require_track_lock_intervention"] = 1 if len(en_req_track_lock_intervention) else 0
#     param_dict["cal_track_mode"] = cfg_cal_track_mode
#     param_dict["amplitude_cal_mode"] = cfg_amplitude_cal_mode
#     param_dict["cal_frame_interval"] = cfg_cal_frame_interval
#     param_dict["cal_frame_burst_size"] = cfg_cal_frame_burst_size
#     param_dict["amplitude_tolerance"] = cfg_amplitude_tolerance
#     param_dict["phase_tolerance"] = cfg_phase_tolerance
#     param_dict["maximum_sync_fails"] = cfg_max_sync_fails
#     param_dict["iq_adjust_source"] = cfg_iq_adjust_source
#     param_dict["iq_adjust_amplitude"] = cfg_iq_adjust_amplitude
#     param_dict["iq_adjust_time_delay_ns"] = cfg_iq_adjust_time_delay_ns
#
#     web_interface.daq_ini_cfg_dict = param_dict


# @app.callback(Output("dummy_output", "children", ""), [Input("en_beta_features", "value")])
# def toggle_beta_features(toggle_value):
#     web_interface.en_beta_features = toggle_value
#
#     toggle_output = []
#
#     # Toggle VFO default configuration settings
#     if toggle_value:
#         toggle_output.append(Output("beta_features_container", "style", {"display": "block"}))
#     else:
#         toggle_output.append(Output("beta_features_container", "style", {"display": "none"}))
#
#     # Toggle individual VFO card settings
#     for i in range(web_interface.module_signal_processor.max_vfos):
#         if toggle_value:
#             toggle_output.append(Output("beta_features_container " + str(i), "style", {"display": "block"}))
#         else:
#             toggle_output.append(Output("beta_features_container " + str(i), "style", {"display": "none"}))
#
#     return toggle_output
#

# @app.callback(
#     [Output("placeholder_update_rx", "children")],
#     [Input("settings-refresh-timer", "n_intervals")],
#     [State("url", "pathname")],
# )
# def settings_change_refresh(toggle_value, pathname):
#     if web_interface.needs_refresh:
#         if pathname == "/" or pathname == "/init" or pathname == "/config":
#             return ["upd"]
#
#     return Output("dummy_output", "children", "")


# @app.callback(
#     Output("dummy_output", "children", ""),
#     [Input(component_id="btn_reconfig_daq_chain", component_property="n_clicks")],
#     [
#         State(component_id="daq_center_freq", component_property="value"),
#         State(component_id="daq_rx_gain", component_property="value"),
#     ],
# )
# def reconfig_daq_chain(input_value, freq, gain):
#     if input_value is None:
#         # [no_update, no_update, no_update, no_update]
#         return Output("dummy_output", "children", "")
#
#     # TODO: Check data interface mode here !
#     #    Update DAQ Subsystem config file
#     config_res, config_err = write_config_file_dict(web_interface, web_interface.daq_ini_cfg_dict, dsp_settings)
#     if config_res:
#         web_interface.daq_cfg_ini_error = config_err[0]
#         return Output("placeholder_recofnig_daq", "children", "-1")
#     else:
#         web_interface.logger.info("DAQ Subsystem configuration file edited")
#
#     web_interface.daq_restart = 1
#     #    Restart DAQ Subsystem
#
#     # Stop signal processing
#     web_interface.stop_processing()
#     web_interface.logger.debug("Signal processing stopped")
#
#     # time.sleep(2)
#
#     # Close control and IQ data interfaces
#     web_interface.close_data_interfaces()
#     web_interface.logger.debug("Data interfaces are closed")
#
#     os.chdir(daq_subsystem_path)
#     # Kill DAQ subsystem
#     # , stdout=subprocess.DEVNULL)
#     daq_stop_script = subprocess.Popen(["bash", daq_stop_filename])
#     daq_stop_script.wait()
#     web_interface.logger.debug("DAQ Subsystem halted")
#
#     # Start DAQ subsystem
#     # , stdout=subprocess.DEVNULL)
#     daq_start_script = subprocess.Popen(["bash", daq_start_filename])
#     daq_start_script.wait()
#     web_interface.logger.debug("DAQ Subsystem restarted")
#
#     # time.sleep(3)
#
#     os.chdir(root_path)
#
#     # TODO: Try this reinit method again, if it works it would save us needing
#     # to restore variable states
#
#     # Reinitialize receiver data interface
#     # if web_interface.module_receiver.init_data_iface() == -1:
#     #    web_interface.logger.critical("Failed to restart the DAQ data interface")
#     #    web_interface.daq_cfg_ini_error = "Failed to restart the DAQ data interface"
#     # return Output('dummy_output', 'children', '') #[no_update, no_update,
#     # no_update, no_update]
#
#     # return [-1]
#
#     # Reset channel number count
#     # web_interface.module_receiver.M = web_interface.daq_ini_cfg_params[1]
#
#     # web_interface.module_receiver.M = 0
#     # web_interface.module_signal_processor.first_frame = 1
#
#     # web_interface.module_receiver.eth_connect()
#     # time.sleep(2)
#     # web_interface.config_daq_rf(web_interface.daq_center_freq, web_interface.module_receiver.daq_rx_gain)
#
#     # Recreate and reinit the receiver and signal processor modules from
#     # scratch, keeping current setting values
#     daq_center_freq = web_interface.module_receiver.daq_center_freq
#     daq_rx_gain = web_interface.module_receiver.daq_rx_gain
#     rec_ip_addr = web_interface.module_receiver.rec_ip_addr
#
#     DOA_ant_alignment = web_interface.module_signal_processor.DOA_ant_alignment
#     DOA_inter_elem_space = web_interface.module_signal_processor.DOA_inter_elem_space
#     en_DOA_estimation = web_interface.module_signal_processor.en_DOA_estimation
#     doa_decorrelation_method = web_interface.module_signal_processor.DOA_decorrelation_method
#     ula_direction = web_interface.module_signal_processor.ula_direction
#
#     doa_format = web_interface.module_signal_processor.DOA_data_format
#     doa_station_id = web_interface.module_signal_processor.station_id
#     doa_lat = web_interface.module_signal_processor.latitude
#     doa_lon = web_interface.module_signal_processor.longitude
#     doa_fixed_heading = web_interface.module_signal_processor.fixed_heading
#     doa_heading = web_interface.module_signal_processor.heading
#     # alt
#     # speed
#     doa_hasgps = web_interface.module_signal_processor.hasgps
#     doa_usegps = web_interface.module_signal_processor.usegps
#     doa_gps_connected = web_interface.module_signal_processor.gps_connected
#     logging_level = web_interface.logging_level
#     data_interface = web_interface.data_interface
#
#     web_interface.module_receiver = ReceiverRTLSDR(
#         data_que=web_interface.rx_data_que, data_interface=data_interface, logging_level=logging_level
#     )
#     web_interface.module_receiver.daq_center_freq = daq_center_freq
#     # settings.uniform_gain #daq_rx_gain
#     web_interface.module_receiver.daq_rx_gain = daq_rx_gain
#     web_interface.module_receiver.rec_ip_addr = rec_ip_addr
#
#     web_interface.module_signal_processor = SignalProcessor(
#         data_que=web_interface.sp_data_que,
#         module_receiver=web_interface.module_receiver,
#         logging_level=logging_level,
#     )
#     web_interface.module_signal_processor.DOA_ant_alignment = DOA_ant_alignment
#     web_interface.module_signal_processor.DOA_inter_elem_space = DOA_inter_elem_space
#     web_interface.module_signal_processor.en_DOA_estimation = en_DOA_estimation
#     web_interface.module_signal_processor.DOA_decorrelation_method = doa_decorrelation_method
#     web_interface.module_signal_processor.ula_direction = ula_direction
#
#     web_interface.module_signal_processor.DOA_data_format = doa_format
#     web_interface.module_signal_processor.station_id = doa_station_id
#     web_interface.module_signal_processor.latitude = doa_lat
#     web_interface.module_signal_processor.longitude = doa_lon
#     web_interface.module_signal_processor.fixed_heading = doa_fixed_heading
#     web_interface.module_signal_processor.heading = doa_heading
#     web_interface.module_signal_processor.hasgps = doa_hasgps
#     web_interface.module_signal_processor.usegps = doa_usegps
#     web_interface.module_signal_processor.gps_connected = doa_gps_connected
#
#     # This must be here, otherwise the gains dont reinit properly?
#     web_interface.module_receiver.M = web_interface.daq_ini_cfg_dict["num_ch"]
#     print("M: " + str(web_interface.module_receiver.M))
#
#     web_interface.module_signal_processor.start()
#
#     # Reinit the spectrum fig, because number of traces may have changed if
#     # tuner count is different
#     global spectrum_fig
#     spectrum_fig = init_spectrum_fig(web_interface, fig_layout, trace_colors)
#
#     # Restart signal processing
#     web_interface.start_processing()
#     web_interface.logger.debug("Signal processing started")
#     web_interface.daq_restart = 0
#
#     web_interface.daq_cfg_ini_error = ""
#     # web_interface.tmp_daq_ini_cfg
#     web_interface.active_daq_ini_cfg = web_interface.daq_ini_cfg_dict["config_name"]
#
#     return Output("daq_cfg_files", "value", daq_config_filename), Output(
#         "active_daq_ini_cfg", "children", "Active Configuration: " + web_interface.active_daq_ini_cfg
#     )
