import os
import subprocess

from dash import Input, Output, State

# isort: off
from maindash import app, web_interface

# isort: on
from kraken_web_config import write_config_file_dict
from kraken_web_spectrum import init_spectrum_fig
from krakenSDR_receiver import ReceiverRTLSDR
from krakenSDR_signal_processor import SignalProcessor
from utils import (
    read_config_file_dict,
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

@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="btn_reconfig_daq_chain", component_property="n_clicks")],
    [
        State(component_id="daq_center_freq", component_property="value"),
        State(component_id="daq_rx_gain", component_property="value"),
    ],
    prevent_initial_call=True

)
def reconfig_daq_chain(input_value, freq, gain):
    print('reconfig_daq_chain')
    if input_value is None:
        # [no_update, no_update, no_update, no_update]
        return Output("dummy_output", "children", "")

    # TODO: Check data interface mode here !
    #    Update DAQ Subsystem config file
    config_res, config_err = write_config_file_dict(web_interface, web_interface.daq_ini_cfg_dict, dsp_settings)
    if config_res:
        web_interface.daq_cfg_ini_error = config_err[0]
        return Output("placeholder_recofnig_daq", "children", "-1")
    else:
        web_interface.logger.info("DAQ Subsystem configuration file edited")

    web_interface.daq_restart = 1
    #    Restart DAQ Subsystem

    # Stop signal processing
    web_interface.stop_processing()
    web_interface.logger.debug("Signal processing stopped")

    # time.sleep(2)

    # Close control and IQ data interfaces
    web_interface.close_data_interfaces()
    web_interface.logger.debug("Data interfaces are closed")

    os.chdir(daq_subsystem_path)
    # Kill DAQ subsystem
    # , stdout=subprocess.DEVNULL)
    daq_stop_script = subprocess.Popen(["bash", daq_stop_filename])
    daq_stop_script.wait()
    web_interface.logger.debug("DAQ Subsystem halted")

    # Start DAQ subsystem
    # , stdout=subprocess.DEVNULL)
    daq_start_script = subprocess.Popen(["bash", daq_start_filename])
    daq_start_script.wait()
    web_interface.logger.debug("DAQ Subsystem restarted")

    # time.sleep(3)

    os.chdir(root_path)

    # TODO: Try this reinit method again, if it works it would save us needing
    # to restore variable states

    # Reinitialize receiver data interface
    # if web_interface.module_receiver.init_data_iface() == -1:
    #    web_interface.logger.critical("Failed to restart the DAQ data interface")
    #    web_interface.daq_cfg_ini_error = "Failed to restart the DAQ data interface"
    # return Output('dummy_output', 'children', '') #[no_update, no_update,
    # no_update, no_update]

    # return [-1]

    # Reset channel number count
    # web_interface.module_receiver.M = web_interface.daq_ini_cfg_params[1]

    # web_interface.module_receiver.M = 0
    # web_interface.module_signal_processor.first_frame = 1

    # web_interface.module_receiver.eth_connect()
    # time.sleep(2)
    # web_interface.config_daq_rf(web_interface.daq_center_freq, web_interface.module_receiver.daq_rx_gain)

    # Recreate and reinit the receiver and signal processor modules from
    # scratch, keeping current setting values
    daq_center_freq = web_interface.module_receiver.daq_center_freq
    daq_rx_gain = web_interface.module_receiver.daq_rx_gain
    rec_ip_addr = web_interface.module_receiver.rec_ip_addr

    DOA_ant_alignment = web_interface.module_signal_processor.DOA_ant_alignment
    DOA_inter_elem_space = web_interface.module_signal_processor.DOA_inter_elem_space
    en_DOA_estimation = web_interface.module_signal_processor.en_DOA_estimation
    doa_decorrelation_method = web_interface.module_signal_processor.DOA_decorrelation_method
    ula_direction = web_interface.module_signal_processor.ula_direction

    doa_format = web_interface.module_signal_processor.DOA_data_format
    doa_station_id = web_interface.module_signal_processor.station_id
    doa_lat = web_interface.module_signal_processor.latitude
    doa_lon = web_interface.module_signal_processor.longitude
    doa_fixed_heading = web_interface.module_signal_processor.fixed_heading
    doa_heading = web_interface.module_signal_processor.heading
    # alt
    # speed
    doa_hasgps = web_interface.module_signal_processor.hasgps
    doa_usegps = web_interface.module_signal_processor.usegps
    doa_gps_connected = web_interface.module_signal_processor.gps_connected
    logging_level = web_interface.logging_level
    data_interface = web_interface.data_interface

    web_interface.module_receiver = ReceiverRTLSDR(
        data_que=web_interface.rx_data_que, data_interface=data_interface, logging_level=logging_level
    )
    web_interface.module_receiver.daq_center_freq = daq_center_freq
    # settings.uniform_gain #daq_rx_gain
    web_interface.module_receiver.daq_rx_gain = daq_rx_gain
    web_interface.module_receiver.rec_ip_addr = rec_ip_addr

    web_interface.module_signal_processor = SignalProcessor(
        data_que=web_interface.sp_data_que,
        module_receiver=web_interface.module_receiver,
        logging_level=logging_level,
    )
    web_interface.module_signal_processor.DOA_ant_alignment = DOA_ant_alignment
    web_interface.module_signal_processor.DOA_inter_elem_space = DOA_inter_elem_space
    web_interface.module_signal_processor.en_DOA_estimation = en_DOA_estimation
    web_interface.module_signal_processor.DOA_decorrelation_method = doa_decorrelation_method
    web_interface.module_signal_processor.ula_direction = ula_direction

    web_interface.module_signal_processor.DOA_data_format = doa_format
    web_interface.module_signal_processor.station_id = doa_station_id
    web_interface.module_signal_processor.latitude = doa_lat
    web_interface.module_signal_processor.longitude = doa_lon
    web_interface.module_signal_processor.fixed_heading = doa_fixed_heading
    web_interface.module_signal_processor.heading = doa_heading
    web_interface.module_signal_processor.hasgps = doa_hasgps
    web_interface.module_signal_processor.usegps = doa_usegps
    web_interface.module_signal_processor.gps_connected = doa_gps_connected

    # This must be here, otherwise the gains dont reinit properly?
    web_interface.module_receiver.M = web_interface.daq_ini_cfg_dict["num_ch"]
    print("M: " + str(web_interface.module_receiver.M))

    web_interface.module_signal_processor.start()

    # Reinit the spectrum fig, because number of traces may have changed if
    # tuner count is different
    global spectrum_fig
    spectrum_fig = init_spectrum_fig(web_interface, fig_layout, trace_colors)

    # Restart signal processing
    web_interface.start_processing()
    web_interface.logger.debug("Signal processing started")
    web_interface.daq_restart = 0

    web_interface.daq_cfg_ini_error = ""
    # web_interface.tmp_daq_ini_cfg
    web_interface.active_daq_ini_cfg = web_interface.daq_ini_cfg_dict["config_name"]

    return Output("daq_cfg_files", "value", daq_config_filename), Output(
        "active_daq_ini_cfg", "children", "Active Configuration: " + web_interface.active_daq_ini_cfg
    )