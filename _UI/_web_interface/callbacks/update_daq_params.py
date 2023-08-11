import copy

import numpy as np
from dash import Input, Output, State
from maindash import app, web_interface
from variables import AGC_WARNING_DEFAULT_STYLE, AUTO_GAIN_VALUE


@app.callback(
    Output("agc_warning", "style", allow_duplicate=True),
    [Input(component_id="btn-update_rx_param", component_property="n_clicks")],
    [
        State(component_id="daq_center_freq", component_property="value"),
        State(component_id="daq_rx_gain", component_property="value"),
    ],
    prevent_initial_call=True,
)
def update_daq_params(input_value, f0, gain):
    if web_interface.module_signal_processor.run_processing:
        web_interface.daq_center_freq = f0
        agc = True if (gain == AUTO_GAIN_VALUE) else False
        web_interface.config_daq_rf(f0, gain, agc)

        agc_warning_style = copy.deepcopy(AGC_WARNING_DEFAULT_STYLE)
        agc_warning_style["display"] = "block" if agc else "none"

        wavelength = 300 / web_interface.daq_center_freq
        # web_interface.module_signal_processor.DOA_inter_elem_space = web_interface.ant_spacing_meters / wavelength

        if web_interface.module_signal_processor.DOA_ant_alignment == "UCA":
            # Convert RADIUS to INTERELEMENT SPACING
            inter_elem_spacing = (
                np.sqrt(2)
                * web_interface.ant_spacing_meters
                * np.sqrt(1 - np.cos(np.deg2rad(360 / web_interface.module_signal_processor.channel_number)))
            )
            web_interface.module_signal_processor.DOA_inter_elem_space = inter_elem_spacing / wavelength
        else:
            web_interface.module_signal_processor.DOA_inter_elem_space = web_interface.ant_spacing_meters / wavelength

        ant_spacing_wavelength = round(web_interface.module_signal_processor.DOA_inter_elem_space, 3)
        app.push_mods(
            {
                "body_ant_spacing_wavelength": {"children": str(ant_spacing_wavelength)},
            }
        )
    return agc_warning_style


vfos_freq_outputs = []
for i in range(web_interface.module_signal_processor.max_vfos):
    vfos_freq_outputs.append(Output(f"vfo_{i}_freq", "value"))

@app.callback(
    vfos_freq_outputs,
    [Input(component_id="btn-update_rx_param", component_property="n_clicks")],
    [
        State(component_id="daq_center_freq", component_property="value"),
    ],
    prevent_initial_call=True,
)
def update_vfo_freq_params(n_clicks, f0):
    result_array = []
    if n_clicks and web_interface.module_signal_processor.run_processing:
        for i in range(web_interface.module_signal_processor.max_vfos):
            half_band_width = (web_interface.module_signal_processor.vfo_bw[i] / 10 ** 6) / 2
            min_freq = web_interface.daq_center_freq - web_interface.daq_fs / 2 + half_band_width
            max_freq = web_interface.daq_center_freq + web_interface.daq_fs / 2 - half_band_width
            if not (min_freq < (web_interface.module_signal_processor.vfo_freq[i] / 10 ** 6) < max_freq):
                web_interface.module_signal_processor.vfo_freq[i] = f0
                result_array.append(f0)
        return result_array