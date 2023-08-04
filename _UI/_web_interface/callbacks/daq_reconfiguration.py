import os
import subprocess

import dash
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


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [
        Input("cfg_rx_channels", "value"),
        Input("cfg_daq_buffer_size", "value"),
        Input("cfg_sample_rate", "value"),
        Input("en_noise_source_ctr", "value"),
        Input("cfg_cpi_size", "value"),
        Input("cfg_decimation_ratio", "value"),
        Input("cfg_fir_bw", "value"),
        Input("cfg_fir_tap_size", "value"),
        Input("cfg_fir_window", "value"),
        Input("en_filter_reset", "value"),
        Input("cfg_corr_size", "value"),
        Input("cfg_std_ch_ind", "value"),
        Input("en_iq_cal", "value"),
        Input("cfg_gain_lock", "value"),
        Input("en_req_track_lock_intervention", "value"),
        Input("cfg_cal_track_mode", "value"),
        Input("cfg_amplitude_cal_mode", "value"),
        Input("cfg_cal_frame_interval", "value"),
        Input("cfg_cal_frame_burst_size", "value"),
        Input("cfg_amplitude_tolerance", "value"),
        Input("cfg_phase_tolerance", "value"),
        Input("cfg_max_sync_fails", "value"),
        Input("cfg_data_block_len", "value"),
        Input("cfg_recal_interval", "value"),
        Input("cfg_en_bias_tee", "value"),
        Input("cfg_iq_adjust_source", "value"),
        Input("cfg_iq_adjust_amplitude", "value"),
        Input("cfg_iq_adjust_time_delay_ns", "value"),
    ],
    prevent_initial_call=True,
)
def update_daq_ini_params(
        cfg_rx_channels,
        cfg_daq_buffer_size,
        cfg_sample_rate,
        en_noise_source_ctr,
        cfg_cpi_size,
        cfg_decimation_ratio,
        cfg_fir_bw,
        cfg_fir_tap_size,
        cfg_fir_window,
        en_filter_reset,
        cfg_corr_size,
        cfg_std_ch_ind,
        en_iq_cal,
        cfg_gain_lock,
        en_req_track_lock_intervention,
        cfg_cal_track_mode,
        cfg_amplitude_cal_mode,
        cfg_cal_frame_interval,
        cfg_cal_frame_burst_size,
        cfg_amplitude_tolerance,
        cfg_phase_tolerance,
        cfg_max_sync_fails,
        cfg_data_block_len,
        cfg_recal_interval,
        cfg_en_bias_tee,
        cfg_iq_adjust_source,
        cfg_iq_adjust_amplitude,
        cfg_iq_adjust_time_delay_ns,
        config_fname=daq_config_filename,
):
    ctx = dash.callback_context
    component_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if ctx.triggered:
        if len(ctx.triggered) == 1:  # User manually changed one parameter
            web_interface.tmp_daq_ini_cfg = "Custom"

        # If the input was from basic DAQ config, update the actual DAQ params
        if component_id == "cfg_data_block_len" or component_id == "cfg_recal_interval":
            if not cfg_data_block_len or not cfg_recal_interval:
                # [no_update, no_update, no_update, no_update]
                return "input was not from basic DAQ config"

            cfg_daq_buffer_size = 262144  # This is a reasonable DAQ buffer size to use

            decimated_bw = ((cfg_sample_rate * 10 ** 6) / cfg_decimation_ratio) / 10 ** 3
            cfg_cpi_size = round((cfg_data_block_len / 10 ** 3) * decimated_bw * 10 ** 3)
            cfg_cal_frame_interval = round((cfg_recal_interval * 60) / (cfg_data_block_len / 10 ** 3))

            while cfg_decimation_ratio * cfg_cpi_size < cfg_daq_buffer_size:
                cfg_daq_buffer_size = (int)(cfg_daq_buffer_size / 2)

            # app.push_mods(
            #     {
            #         "cfg_cpi_size": {"value": cfg_cpi_size},
            #         "cfg_cal_frame_interval": {"value": cfg_cal_frame_interval},
            #         "cfg_fir_tap_size": {"value": cfg_fir_tap_size},
            #         "cfg_daq_buffer_size": {"value": cfg_daq_buffer_size},
            #     }
            # )

        # If we updated advanced daq, update basic DAQ params
        elif (
                component_id == "cfg_sample_rate"
                or component_id == "cfg_decimation_ratio"
                or component_id == "cfg_cpi_size"
                or component_id == "cfg_cal_frame_interval"
        ):
            if not cfg_sample_rate or not cfg_decimation_ratio or not cfg_cpi_size:
                # [no_update, no_update, no_update, no_update]
                return "no updated  advanced daq"

            decimated_bw = ((cfg_sample_rate * 10 ** 6) / cfg_decimation_ratio) / 10 ** 3

            cfg_data_block_len = cfg_cpi_size / (decimated_bw)
            cfg_recal_interval = (cfg_cal_frame_interval * (cfg_data_block_len / 10 ** 3)) / 60

            # app.push_mods(
            #     {
            #         "cfg_data_block_len": {"value": cfg_data_block_len},
            #         "cfg_recal_interval": {"value": cfg_recal_interval},
            #     }
            # )

    # Write calculated daq params to the ini param_dict
    param_dict = web_interface.daq_ini_cfg_dict
    param_dict["config_name"] = "Custom"
    param_dict["num_ch"] = cfg_rx_channels
    param_dict["en_bias_tee"] = cfg_en_bias_tee
    param_dict["daq_buffer_size"] = cfg_daq_buffer_size
    param_dict["sample_rate"] = int(cfg_sample_rate * 10 ** 6)
    param_dict["en_noise_source_ctr"] = 1 if len(en_noise_source_ctr) else 0
    param_dict["cpi_size"] = cfg_cpi_size
    param_dict["decimation_ratio"] = cfg_decimation_ratio
    param_dict["fir_relative_bandwidth"] = cfg_fir_bw
    param_dict["fir_tap_size"] = cfg_fir_tap_size
    param_dict["fir_window"] = cfg_fir_window
    param_dict["en_filter_reset"] = 1 if len(en_filter_reset) else 0
    param_dict["corr_size"] = cfg_corr_size
    param_dict["std_ch_ind"] = cfg_std_ch_ind
    param_dict["en_iq_cal"] = 1 if len(en_iq_cal) else 0
    param_dict["gain_lock_interval"] = cfg_gain_lock
    param_dict["require_track_lock_intervention"] = 1 if len(en_req_track_lock_intervention) else 0
    param_dict["cal_track_mode"] = cfg_cal_track_mode
    param_dict["amplitude_cal_mode"] = cfg_amplitude_cal_mode
    param_dict["cal_frame_interval"] = cfg_cal_frame_interval
    param_dict["cal_frame_burst_size"] = cfg_cal_frame_burst_size
    param_dict["amplitude_tolerance"] = cfg_amplitude_tolerance
    param_dict["phase_tolerance"] = cfg_phase_tolerance
    param_dict["maximum_sync_fails"] = cfg_max_sync_fails
    param_dict["iq_adjust_source"] = cfg_iq_adjust_source
    param_dict["iq_adjust_amplitude"] = cfg_iq_adjust_amplitude
    param_dict["iq_adjust_time_delay_ns"] = cfg_iq_adjust_time_delay_ns

    web_interface.daq_ini_cfg_dict = param_dict
