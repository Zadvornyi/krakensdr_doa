from dash import html

# isort: off
from maindash import web_interface


# isort: on


def get_daq_update_rate():
    if web_interface.daq_update_rate < 1:
        daq_update_rate_str = "{:d} ms".format(round(web_interface.daq_update_rate * 1000))
    else:
        daq_update_rate_str = "{:.2f} s".format(web_interface.daq_update_rate)

    return daq_update_rate_str


def get_daq_conn_status_str():
    if web_interface.daq_conn_status == 1:
        if not web_interface.daq_cfg_iface_status:
            daq_conn_status_str = "Connected"
        else:  # Config interface is busy
            daq_conn_status_str = "Reconfiguration.."
    else:
        daq_conn_status_str = "Disconnected"

    if web_interface.daq_restart:
        daq_conn_status_str = "Restarting.."

    return daq_conn_status_str


def get_daq_conn_status_style():
    if web_interface.daq_conn_status == 1:
        if not web_interface.daq_cfg_iface_status:
            conn_status_style = {"color": "#7ccc63"}
        else:  # Config interface is busy
            conn_status_style = {"color": "#f39c12"}
    else:
        conn_status_style = {"color": "#e74c3c"}

    if web_interface.daq_restart:
        conn_status_style = {"color": "#f39c12"}

    return conn_status_style


def get_daq_power_level_str():
    if web_interface.daq_power_level:
        daq_power_level_str = "Overdrive"
    else:
        daq_power_level_str = "OK"
    return daq_power_level_str


def get_daq_power_level_style():
    if web_interface.daq_power_level:
        daq_power_level_style = {"color": "#e74c3c"}
    else:
        daq_power_level_style = {"color": "#7ccc63"}
    return daq_power_level_style


def get_daq_frame_sync():
    if web_interface.daq_frame_sync:
        daq_frame_sync_str = "LOSS"
    else:
        daq_frame_sync_str = "Ok"
    return daq_frame_sync_str


def get_daq_frame_sync_style():
    if web_interface.daq_frame_sync:
        frame_sync_style = {"color": "#e74c3c"}
    else:
        frame_sync_style = {"color": "#7ccc63"}
    return frame_sync_style


def get_frame_type_style():
    if web_interface.daq_frame_type == "Data":
        frame_type_style = {"color": "#7ccc63"}
    elif web_interface.daq_frame_type == "Dummy":
        frame_type_style = {"color": "white"}
    elif web_interface.daq_frame_type == "Calibration":
        frame_type_style = {"color": "#f39c12"}
    elif web_interface.daq_frame_type == "Trigger wait":
        frame_type_style = {"color": "#f39c12"}
    else:
        frame_type_style = {"color": "#e74c3c"}

    return frame_type_style


def get_daq_delay_sync_str():
    if web_interface.daq_sample_delay_sync:
        daq_delay_sync_str = "Ok"
    else:
        daq_delay_sync_str = "LOSS"
    return daq_delay_sync_str


def get_daq_delay_sync_style():
    if web_interface.daq_sample_delay_sync:
        delay_sync_style = {"color": "#7ccc63"}
    else:
        delay_sync_style = {"color": "#e74c3c"}
    return delay_sync_style


def get_daq_iq_sync_str():
    if web_interface.daq_iq_sync:
        daq_iq_sync_str = "Ok"
    else:
        daq_iq_sync_str = "LOSS"
    return daq_iq_sync_str


def get_daq_iq_sync_style():
    if web_interface.daq_iq_sync:
        iq_sync_style = {"color": "#7ccc63"}
    else:
        iq_sync_style = {"color": "#e74c3c"}
    return iq_sync_style


def get_daq_noise_source_str():
    if web_interface.daq_noise_source_state:
        daq_noise_source_str = "Enabled"
    else:
        daq_noise_source_str = "Disabled"

    return daq_noise_source_str


def get_daq_noise_source_style():
    if web_interface.daq_noise_source_state:
        noise_source_style = {"color": "#e74c3c"}
    else:
        noise_source_style = {"color": "#7ccc63"}

    return noise_source_style


def get_dsp_decimated_bw_str():
    bw = web_interface.daq_fs / web_interface.module_signal_processor.dsp_decimation
    dsp_decimated_bw_str = "{0:.3f}".format(bw)

    return dsp_decimated_bw_str


def get_vfo_range_str():
    bw = web_interface.daq_fs / web_interface.module_signal_processor.dsp_decimation
    vfo_range_str = (
            "{0:.3f}".format(web_interface.daq_center_freq - bw / 2)
            + " - "
            + "{0:.3f}".format(web_interface.daq_center_freq + bw / 2)
    )
    return vfo_range_str


def get_gps_en_str():
    if web_interface.module_signal_processor.gps_status == "Connected":
        gps_en_str = "Connected"
    else:
        gps_en_str = web_interface.module_signal_processor.gps_status
    return gps_en_str


def get_gps_en_style():
    if web_interface.module_signal_processor.gps_status == "Connected":
        gps_en_str_style = {"color": "#7ccc63"}
    else:
        gps_en_str_style = {"color": "#e74c3c"}

    return gps_en_str_style


def daq_status_content():
    content = [
        html.H2("DAQ Subsystem Status", id="init_title_s"),
        html.Div(
            [
                html.Div("Update Rate:", id="label_daq_update_rate", className="field-label"),
                html.Div(get_daq_update_rate(), id="body_daq_update_rate", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Latency:", id="label_daq_dsp_latency", className="field-label"),
                html.Div(
                    "{:d} ms".format(web_interface.daq_dsp_latency), id="body_daq_dsp_latency", className="field-body"
                ),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Frame Index:", id="label_daq_frame_index", className="field-label"),
                html.Div(str(web_interface.daq_frame_index), id="body_daq_frame_index", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Frame Type:", id="label_daq_frame_type", className="field-label"),
                html.Div(
                    web_interface.daq_frame_type,
                    id="body_daq_frame_type",
                    className="field-body",
                    style=get_frame_type_style(),
                ),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Frame Sync:", id="label_daq_frame_sync", className="field-label"),
                html.Div(
                    get_daq_frame_sync(),
                    id="body_daq_frame_sync",
                    className="field-body",
                    style=get_daq_frame_sync_style(),
                ),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Power Level:", id="label_daq_power_level", className="field-label"),
                html.Div(
                    get_daq_power_level_str(),
                    id="body_daq_power_level",
                    className="field-body",
                    style=get_daq_power_level_style(),
                ),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Connection Status:", id="label_daq_conn_status", className="field-label"),
                html.Div(
                    get_daq_conn_status_str(),
                    id="body_daq_conn_status",
                    className="field-body",
                    style=get_daq_conn_status_style(),
                ),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Sample Delay Sync:", id="label_daq_delay_sync", className="field-label"),
                html.Div(
                    get_daq_delay_sync_str(),
                    id="body_daq_delay_sync",
                    className="field-body",
                    style=get_daq_delay_sync_style(),
                ),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("IQ Sync:", id="label_daq_iq_sync", className="field-label"),
                html.Div(
                    get_daq_iq_sync_str(), id="body_daq_iq_sync", className="field-body", style=get_daq_iq_sync_style()
                ),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Noise Source State:", id="label_daq_noise_source", className="field-label"),
                html.Div(
                    get_daq_noise_source_str(),
                    id="body_daq_noise_source",
                    className="field-body",
                    style=get_daq_noise_source_style(),
                ),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Center Frequecy [MHz]:", id="label_daq_rf_center_freq", className="field-label"),
                html.Div(str(web_interface.daq_center_freq), id="body_daq_rf_center_freq", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Sampling Frequency [MHz]:", id="label_daq_sampling_freq", className="field-label"),
                html.Div(str(web_interface.daq_fs), id="body_daq_sampling_freq", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("DSP Decimated BW [MHz]:", id="label_dsp_decimated_bw", className="field-label"),
                html.Div(get_dsp_decimated_bw_str(), id="body_dsp_decimated_bw", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("VFO Range [MHz]:", id="label_vfo_range", className="field-label"),
                html.Div(get_vfo_range_str(), id="body_vfo_range", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Data Block Length [ms]:", id="label_daq_cpi", className="field-label"),
                html.Div(str(web_interface.daq_cpi), id="body_daq_cpi", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("RF Gains [dB]:", id="label_daq_if_gain", className="field-label"),
                html.Div(web_interface.daq_if_gains, id="body_daq_if_gain", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("VFO-0 Power [dB]:", id="label_max_amp", className="field-label"),
                html.Div("{:.1f}".format(web_interface.max_amplitude), id="body_max_amp", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("Average Power:", id="label_daq_avg_powers", className="field-label"),
                html.Div(web_interface.avg_powers, id="body_daq_avg_powers", className="field-body"),
            ],
            className="field",
        ),
        html.Div(
            [
                html.Div("GPS status:", id="label_gps_en", className="field-label"),
                html.Div(get_gps_en_str(), id="body_gps_en", className="field-body", style=get_gps_en_style()),
            ],
            className="field",
        ),
    ]

    return content


# -----------------------------
#       DAQ Status Card
# -----------------------------
def daq_status_card_layout():
    layout = html.Div(
        daq_status_content(),
        id="daq_status_card",
        className="card daq-status-card",
    )

    return layout
