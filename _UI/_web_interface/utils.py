import json
import os
import queue
from configparser import ConfigParser

import numpy as np
from krakenSDR_signal_processor import DEFAULT_VFO_FIR_ORDER_FACTOR
from variables import DEFAULT_MAPPING_SERVER_ENDPOINT, HZ_TO_MHZ, daq_config_filename


def read_config_file_dict(config_fname=daq_config_filename):
    parser = ConfigParser()
    found = parser.read([config_fname])
    ini_data = {}
    if not found:
        return None

    ini_data["config_name"] = parser.get("meta", "config_name")
    ini_data["num_ch"] = parser.getint("hw", "num_ch")
    ini_data["en_bias_tee"] = parser.get("hw", "en_bias_tee")
    ini_data["daq_buffer_size"] = parser.getint("daq", "daq_buffer_size")
    ini_data["sample_rate"] = parser.getint("daq", "sample_rate")
    ini_data["en_noise_source_ctr"] = parser.getint("daq", "en_noise_source_ctr")
    ini_data["cpi_size"] = parser.getint("pre_processing", "cpi_size")
    ini_data["decimation_ratio"] = parser.getint("pre_processing", "decimation_ratio")
    ini_data["fir_relative_bandwidth"] = parser.getfloat("pre_processing", "fir_relative_bandwidth")
    ini_data["fir_tap_size"] = parser.getint("pre_processing", "fir_tap_size")
    ini_data["fir_window"] = parser.get("pre_processing", "fir_window")
    ini_data["en_filter_reset"] = parser.getint("pre_processing", "en_filter_reset")
    ini_data["corr_size"] = parser.getint("calibration", "corr_size")
    ini_data["std_ch_ind"] = parser.getint("calibration", "std_ch_ind")
    ini_data["en_iq_cal"] = parser.getint("calibration", "en_iq_cal")
    ini_data["gain_lock_interval"] = parser.getint("calibration", "gain_lock_interval")
    ini_data["require_track_lock_intervention"] = parser.getint("calibration", "require_track_lock_intervention")
    ini_data["cal_track_mode"] = parser.getint("calibration", "cal_track_mode")
    ini_data["amplitude_cal_mode"] = parser.get("calibration", "amplitude_cal_mode")
    ini_data["cal_frame_interval"] = parser.getint("calibration", "cal_frame_interval")
    ini_data["cal_frame_burst_size"] = parser.getint("calibration", "cal_frame_burst_size")
    ini_data["amplitude_tolerance"] = parser.getint("calibration", "amplitude_tolerance")
    ini_data["phase_tolerance"] = parser.getint("calibration", "phase_tolerance")
    ini_data["maximum_sync_fails"] = parser.getint("calibration", "maximum_sync_fails")
    ini_data["iq_adjust_source"] = parser.get("calibration", "iq_adjust_source")
    ini_data["iq_adjust_amplitude"] = parser.get("calibration", "iq_adjust_amplitude")
    ini_data["iq_adjust_time_delay_ns"] = parser.get("calibration", "iq_adjust_time_delay_ns")

    ini_data["adpis_gains_init"] = parser.get("adpis", "adpis_gains_init")

    ini_data["out_data_iface_type"] = parser.get("data_interface", "out_data_iface_type")

    return ini_data


def set_click_freq_spectrum(web_interface, clickData):
    M = web_interface.module_receiver.M
    curveNumber = clickData["points"][0]["curveNumber"]

    if curveNumber >= M:
        vfo_idx = int((curveNumber - M) / 2)
        web_interface.selected_vfo = vfo_idx
        if web_interface.module_signal_processor.output_vfo >= 0:
            web_interface.module_signal_processor.output_vfo = vfo_idx
    else:
        idx = 0
        if web_interface.module_signal_processor.output_vfo >= 0:
            idx = max(web_interface.module_signal_processor.output_vfo, 0)
        else:
            idx = web_interface.selected_vfo
        web_interface.module_signal_processor.vfo_freq[idx] = int(clickData["points"][0]["x"])


def fetch_signal_processing_data(web_interface):
    try:
        # Fetch new data from the signal processing module
        que_data_packet = web_interface.sp_data_que.get(False)
        for data_entry in que_data_packet:
            if data_entry[0] == "iq_header":
                web_interface.logger.debug("Iq header data fetched from signal processing que")
                iq_header = data_entry[1]
                # Unpack header
                web_interface.daq_frame_index = iq_header.cpi_index

                if iq_header.frame_type == iq_header.FRAME_TYPE_DATA:
                    web_interface.daq_frame_type = "Data"
                elif iq_header.frame_type == iq_header.FRAME_TYPE_DUMMY:
                    web_interface.daq_frame_type = "Dummy"
                elif iq_header.frame_type == iq_header.FRAME_TYPE_CAL:
                    web_interface.daq_frame_type = "Calibration"
                elif iq_header.frame_type == iq_header.FRAME_TYPE_TRIGW:
                    web_interface.daq_frame_type = "Trigger wait"
                else:
                    web_interface.daq_frame_type = "Unknown"

                web_interface.daq_frame_sync = iq_header.check_sync_word()
                web_interface.daq_power_level = iq_header.adc_overdrive_flags
                web_interface.daq_sample_delay_sync = iq_header.delay_sync_flag
                web_interface.daq_iq_sync = iq_header.iq_sync_flag
                web_interface.daq_noise_source_state = iq_header.noise_source_state

                # if web_interface.daq_center_freq != iq_header.rf_center_freq/10**6:
                #    freq_update = 1

                web_interface.daq_center_freq = iq_header.rf_center_freq / 10**6
                web_interface.daq_adc_fs = iq_header.adc_sampling_freq / 10**6
                web_interface.daq_fs = iq_header.sampling_freq / 10**6
                web_interface.daq_cpi = int(iq_header.cpi_length * 10**3 / iq_header.sampling_freq)
                gain_list_str = ""

                for m in range(iq_header.active_ant_chs):
                    gain_list_str += str(iq_header.if_gains[m] / 10)
                    gain_list_str += ", "

                web_interface.daq_if_gains = gain_list_str[:-2]
                web_interface.daq_status_update_flag = 1
            elif data_entry[0] == "update_rate":
                web_interface.daq_update_rate = data_entry[1]
            elif data_entry[0] == "latency":
                web_interface.daq_dsp_latency = data_entry[1] + web_interface.daq_cpi
            elif data_entry[0] == "max_amplitude":
                web_interface.max_amplitude = data_entry[1]
            elif data_entry[0] == "avg_powers":
                avg_powers_str = ""
                for avg_power in data_entry[1]:
                    avg_powers_str += "{:.1f}".format(avg_power)
                    avg_powers_str += ", "
                print(avg_powers_str, "avg_powers")
                web_interface.avg_powers = avg_powers_str[:-2]
            elif data_entry[0] == "spectrum":
                web_interface.logger.debug("Spectrum data fetched from signal processing que")
                web_interface.spectrum_update_flag = 1
                web_interface.spectrum = data_entry[1]
            elif data_entry[0] == "doa_thetas":
                web_interface.doa_thetas = data_entry[1]
                web_interface.doa_update_flag = 1
                web_interface.doa_results = []
                web_interface.doa_labels = []
                web_interface.doas = []
                web_interface.max_doas_list = []
                web_interface.doa_confidences = []
                web_interface.logger.debug("DoA estimation data fetched from signal processing que")
            elif data_entry[0] == "DoA Result":
                web_interface.doa_results.append(data_entry[1])
                web_interface.doa_labels.append(data_entry[0])
            elif data_entry[0] == "DoA Max":
                web_interface.doas.append(data_entry[1])
            elif data_entry[0] == "DoA Confidence":
                web_interface.doa_confidences.append(data_entry[1])
            elif data_entry[0] == "DoA Max List":
                web_interface.max_doas_list = data_entry[1].copy()
            elif data_entry[0] == "DoA Squelch":
                web_interface.squelch_update = data_entry[1].copy()
            elif data_entry[0] == "VFO-0 Frequency":
                print("VFO-0 Frequency")
                # app.push_mods(
                #     {
                #         "vfo_0_freq": {"value": data_entry[1] * HZ_TO_MHZ},
                #     }
                # )
            else:
                web_interface.logger.warning("Unknown data entry: {:s}".format(data_entry[0]))
    except queue.Empty:
        # Handle empty queue here
        web_interface.logger.debug("Signal processing que is empty")
    else:
        pass
        # Handle task here and call q.task_done()


def fetch_receiver_data(web_interface):
    # freq_update            = 0 #no_update
    #############################################
    #      Fetch new data from back-end ques    #
    #############################################
    try:
        # Fetch new data from the receiver module
        que_data_packet = web_interface.rx_data_que.get(False)
        for data_entry in que_data_packet:
            print(data_entry[0], "fetch_receiver_data")
            if data_entry[0] == "conn-ok":
                web_interface.daq_conn_status = 1
                web_interface.daq_status_update_flag = 1
            elif data_entry[0] == "disconn-ok":
                web_interface.daq_conn_status = 0
                web_interface.daq_status_update_flag = 1
            elif data_entry[0] == "config-ok":
                web_interface.daq_cfg_iface_status = 0
                web_interface.daq_status_update_flag = 1
    except queue.Empty:
        # Handle empty queue here
        web_interface.logger.debug("Receiver module que is empty")
    else:
        pass
        # Handle task here and call q.task_done()

    if web_interface.daq_restart:  # Set by the restarting script
        web_interface.daq_status_update_flag = 1


def fetch_dsp_data(web_interface):
    web_interface.daq_status_update_flag = 0
    web_interface.spectrum_update_flag = 0
    web_interface.doa_update_flag = 0

    fetch_receiver_data(web_interface)
    fetch_signal_processing_data(web_interface)


def settings_change_watcher(web_interface, settings_file_path):
    last_changed_time = os.stat(settings_file_path).st_mtime
    time_delta = last_changed_time - web_interface.last_changed_time_previous

    # Load settings file
    if time_delta > 0:  # If > 0, file was changed
        global dsp_settings
        if os.path.exists(settings_file_path):
            with open(settings_file_path, "r") as myfile:
                # update global dsp_settings, to ensureother functions using it
                # get the most up to date values??
                dsp_settings = json.loads(myfile.read())

        center_freq = float(dsp_settings.get("center_freq", 100.0))
        gain = float(dsp_settings.get("uniform_gain", 1.4))

        web_interface.ant_spacing_meters = float(dsp_settings.get("ant_spacing_meters", 0.5))

        web_interface.module_signal_processor.en_DOA_estimation = dsp_settings.get("en_doa", 0)
        web_interface.module_signal_processor.DOA_decorrelation_method = dsp_settings.get("doa_decorrelation_method", 0)

        web_interface.module_signal_processor.DOA_ant_alignment = dsp_settings.get("ant_arrangement", "ULA")
        web_interface.ant_spacing_meters = float(dsp_settings.get("ant_spacing_meters", 0.5))

        web_interface.custom_array_x_meters = np.float_(
            dsp_settings.get("custom_array_x_meters", "0.1,0.2,0.3,0.4,0.5").split(",")
        )
        web_interface.custom_array_y_meters = np.float_(
            dsp_settings.get("custom_array_y_meters", "0.1,0.2,0.3,0.4,0.5").split(",")
        )
        web_interface.module_signal_processor.custom_array_x = web_interface.custom_array_x_meters / (
            300 / web_interface.module_receiver.daq_center_freq
        )
        web_interface.module_signal_processor.custom_array_y = web_interface.custom_array_y_meters / (
            300 / web_interface.module_receiver.daq_center_freq
        )

        # Station Information
        web_interface.module_signal_processor.station_id = dsp_settings.get("station_id", "NO-CALL")
        web_interface.location_source = dsp_settings.get("location_source", "None")
        web_interface.module_signal_processor.latitude = dsp_settings.get("latitude", 0.0)
        web_interface.module_signal_processor.longitude = dsp_settings.get("longitude", 0.0)
        web_interface.module_signal_processor.heading = dsp_settings.get("heading", 0.0)
        web_interface.module_signal_processor.krakenpro_key = dsp_settings.get("krakenpro_key", 0.0)
        web_interface.mapping_server_url = dsp_settings.get("mapping_server_url", DEFAULT_MAPPING_SERVER_ENDPOINT)
        web_interface.module_signal_processor.RDF_mapper_server = dsp_settings.get(
            "rdf_mapper_server", "http://RDF_MAPPER_SERVER.com/save.php"
        )

        # VFO Configuration
        web_interface.module_signal_processor.spectrum_fig_type = dsp_settings.get("spectrum_calculation", "Single")
        web_interface.module_signal_processor.vfo_mode = dsp_settings.get("vfo_mode", "Standard")
        web_interface.module_signal_processor.vfo_default_demod = dsp_settings.get("vfo_default_demod", "None")
        web_interface.module_signal_processor.vfo_default_iq = dsp_settings.get("vfo_default_iq", "False")
        web_interface.module_signal_processor.max_demod_timeout = int(dsp_settings.get("max_demod_timeout", 60))
        web_interface.module_signal_processor.dsp_decimation = int(dsp_settings.get("dsp_decimation", 0))
        web_interface.module_signal_processor.active_vfos = int(dsp_settings.get("active_vfos", 0))
        web_interface.module_signal_processor.output_vfo = int(dsp_settings.get("output_vfo", 0))
        web_interface.compass_offset = dsp_settings.get("compass_offset", 0)
        web_interface.module_signal_processor.compass_offset = web_interface.compass_offset
        web_interface.module_signal_processor.optimize_short_bursts = dsp_settings.get("en_optimize_short_bursts", 0)
        web_interface.module_signal_processor.en_peak_hold = dsp_settings.get("en_peak_hold", 0)

        for i in range(web_interface.module_signal_processor.max_vfos):
            web_interface.module_signal_processor.vfo_bw[i] = int(dsp_settings.get("vfo_bw_" + str(i), 0))
            web_interface.module_signal_processor.vfo_fir_order_factor[i] = int(
                dsp_settings.get("vfo_fir_order_factor_" + str(i), DEFAULT_VFO_FIR_ORDER_FACTOR)
            )
            web_interface.module_signal_processor.vfo_freq[i] = float(dsp_settings.get("vfo_freq_" + str(i), 0))
            web_interface.module_signal_processor.vfo_squelch[i] = int(dsp_settings.get("vfo_squelch_" + str(i), 0))
            web_interface.module_signal_processor.vfo_demod[i] = dsp_settings.get("vfo_demod_" + str(i), "Default")
            web_interface.module_signal_processor.vfo_iq[i] = dsp_settings.get("vfo_iq_" + str(i), "Default")

        web_interface.module_signal_processor.DOA_algorithm = dsp_settings.get("doa_method", "MUSIC")
        web_interface.module_signal_processor.DOA_expected_num_of_sources = dsp_settings.get(
            "expected_num_of_sources", 1
        )
        web_interface._doa_fig_type = dsp_settings.get("doa_fig_type", "Linear")
        web_interface.module_signal_processor.doa_measure = web_interface._doa_fig_type
        web_interface.module_signal_processor.ula_direction = dsp_settings.get("ula_direction", "Both")
        web_interface.module_signal_processor.array_offset = int(dsp_settings.get("array_offset", 0))

        freq_delta = web_interface.daq_center_freq - center_freq
        gain_delta = web_interface.module_receiver.daq_rx_gain - gain

        if abs(freq_delta) > 0.001 or abs(gain_delta) > 0.001:
            web_interface.daq_center_freq = center_freq
            web_interface.config_daq_rf(center_freq, gain)
        # TODO: undestange what should i do with needs_refresh
        web_interface.needs_refresh = True

    web_interface.last_changed_time_previous = last_changed_time
