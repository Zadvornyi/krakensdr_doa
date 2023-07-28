import numpy as np
from dash import Input, Output

# isort: off
from maindash import app, web_interface
from krakenSDR_signal_processor import xi

# isort: on

from variables import DECORRELATION_OPTIONS, DOA_METHODS


# Enable custom input fields
@app.callback(
    [Output("customx", "style"), Output("customy", "style"), Output("antspacing", "style")],
    [Input("radio_ant_arrangement", "value")],
)
def toggle_custom_array_fields(toggle_value):
    if toggle_value == "UCA" or toggle_value == "ULA":
        return [{"display": "none"}, {"display": "none"}, {"display": "block"}]
    else:
        return [{"display": "block"}, {"display": "block"}, {"display": "none"}]


# Fallback to MUSIC if "Custom" arrangement is selected for ROOT-MUSIC
@app.callback(
    [Output("doa_method", "value")],
    [Input("radio_ant_arrangement", "value")],
)
def fallback_custom_array_to_music(toggle_value):
    if toggle_value == "Custom" and web_interface.module_signal_processor.DOA_algorithm == "ROOT-MUSIC":
        return ["MUSIC"]
    else:
        return [web_interface.module_signal_processor.DOA_algorithm]


# Disable ROOT-MUSIC if "Custom" arrangement is selected
@app.callback(
    [Output("doa_method", "options")],
    [Input("radio_ant_arrangement", "value")],
)
def disable_root_music_for_custom_array(toggle_value):
    if toggle_value == "Custom":
        return [
            [
                dict(doa_method, disabled=True)
                if doa_method["value"] == "ROOT-MUSIC"
                else dict(doa_method, disabled=False)
                for doa_method in DOA_METHODS
            ]
        ]
    else:
        return [[dict(doa_method, disabled=False) for doa_method in DOA_METHODS]]


@app.callback(
    [
        Output(component_id="body_ant_spacing_wavelength", component_property="children"),
        Output(component_id="label_ant_spacing_meter", component_property="children"),
        Output(component_id="ambiguity_warning", component_property="children"),
        Output(component_id="doa_decorrelation_method", component_property="options"),
        Output(component_id="doa_decorrelation_method", component_property="disabled"),
        Output(component_id="uca_decorrelation_warning", component_property="children"),
        Output(component_id="uca_root_music_warning", component_property="children"),
        Output(component_id="expected_num_of_sources", component_property="options"),
        Output(component_id="expected_num_of_sources", component_property="disabled"),
    ],
    [
        Input(component_id="placeholder_update_freq", component_property="children"),
        Input(component_id="en_doa_check", component_property="value"),
        Input(component_id="doa_decorrelation_method", component_property="value"),
        Input(component_id="ant_spacing_meter", component_property="value"),
        Input(component_id="radio_ant_arrangement", component_property="value"),
        Input(component_id="doa_fig_type", component_property="value"),
        Input(component_id="doa_method", component_property="value"),
        Input(component_id="ula_direction", component_property="value"),
        Input(component_id="expected_num_of_sources", component_property="value"),
        Input(component_id="array_offset", component_property="value"),
        Input(component_id="compass_offset", component_property="value"),
        Input(component_id="custom_array_x_meters", component_property="value"),
        Input(component_id="custom_array_y_meters", component_property="value"),
        Input(component_id="en_peak_hold", component_property="value"),
    ],
)
def update_dsp_params(
    update_freq,
    en_doa,
    doa_decorrelation_method,
    spacing_meter,
    ant_arrangement,
    doa_fig_type,
    doa_method,
    ula_direction,
    expected_num_of_sources,
    array_offset,
    compass_offset,
    custom_array_x_meters,
    custom_array_y_meters,
    en_peak_hold,
):  # , input_value):
    web_interface.ant_spacing_meters = spacing_meter
    wavelength = 300 / web_interface.daq_center_freq

    # web_interface.module_signal_processor.DOA_inter_elem_space = web_interface.ant_spacing_meters / wavelength

    if ant_arrangement == "UCA":
        web_interface.module_signal_processor.DOA_UCA_radius_m = web_interface.ant_spacing_meters
        # Convert RADIUS to INTERELEMENT SPACING
        inter_elem_spacing = (
            np.sqrt(2)
            * web_interface.ant_spacing_meters
            * np.sqrt(1 - np.cos(np.deg2rad(360 / web_interface.module_signal_processor.channel_number)))
        )
        web_interface.module_signal_processor.DOA_inter_elem_space = inter_elem_spacing / wavelength
    else:
        web_interface.module_signal_processor.DOA_UCA_radius_m = np.Infinity
        web_interface.module_signal_processor.DOA_inter_elem_space = web_interface.ant_spacing_meters / wavelength

    ant_spacing_wavelength = round(web_interface.module_signal_processor.DOA_inter_elem_space, 3)

    spacing_label = ""

    # Split CSV input in custom array

    web_interface.custom_array_x_meters = np.float_(custom_array_x_meters.split(","))
    web_interface.custom_array_y_meters = np.float_(custom_array_y_meters.split(","))

    web_interface.module_signal_processor.custom_array_x = web_interface.custom_array_x_meters / wavelength
    web_interface.module_signal_processor.custom_array_y = web_interface.custom_array_y_meters / wavelength

    # Max phase diff and ambiguity warning and Spatial smoothing control
    if ant_arrangement == "ULA":
        max_phase_diff = web_interface.ant_spacing_meters / wavelength
        spacing_label = "Interelement Spacing [m]:"
    elif ant_arrangement == "UCA":
        UCA_ant_spacing = (
            np.sqrt(2)
            * web_interface.ant_spacing_meters
            * np.sqrt(1 - np.cos(np.deg2rad(360 / web_interface.module_signal_processor.channel_number)))
        )
        max_phase_diff = UCA_ant_spacing / wavelength
        spacing_label = "Array Radius [m]:"
    elif ant_arrangement == "Custom":
        max_phase_diff = 0.25  # ant_spacing_meter / wavelength
        spacing_label = "Interelement Spacing [m]"

    if max_phase_diff > 0.5:
        ambiguity_warning = "WARNING: Array size is too large for this frequency. DoA estimation is ambiguous. Max phase difference:{:.1f}°.".format(
            np.rad2deg(2 * np.pi * max_phase_diff)
        )
    elif max_phase_diff < 0.1:
        ambiguity_warning = "WARNING: Array size may be too small.  Max phase difference: {:.1f}°.".format(
            np.rad2deg(2 * np.pi * max_phase_diff)
        )
    else:
        ambiguity_warning = ""

    if en_doa is not None and len(en_doa):
        web_interface.logger.debug("DoA estimation enabled")
        web_interface.module_signal_processor.en_DOA_estimation = True
    else:
        web_interface.module_signal_processor.en_DOA_estimation = False

    web_interface.module_signal_processor.DOA_algorithm = doa_method

    is_odd_number_of_channels = web_interface.module_signal_processor.channel_number % 2 != 0
    # UCA->VULA transformation works best if we have odd number of channels
    is_decorrelation_applicable = ant_arrangement != "Custom" and is_odd_number_of_channels
    web_interface.module_signal_processor.DOA_decorrelation_method = (
        doa_decorrelation_method if is_decorrelation_applicable else DECORRELATION_OPTIONS[0]["value"]
    )

    doa_decorrelation_method_options = (
        DECORRELATION_OPTIONS
        if is_decorrelation_applicable
        else [{**DECORRELATION_OPTION, "label": "N/A"} for DECORRELATION_OPTION in DECORRELATION_OPTIONS]
    )
    doa_decorrelation_method_state = False if is_decorrelation_applicable else True

    if (
        ant_arrangement == "UCA"
        and web_interface.module_signal_processor.DOA_decorrelation_method != DECORRELATION_OPTIONS[0]["value"]
    ):
        uca_decorrelation_warning = "WARNING: Using decorrelation methods with UCA array is still experimental as it might produce inconsistent results."
        _, L = xi(web_interface.ant_spacing_meters, web_interface.daq_center_freq * 1.0e6)
        M = web_interface.module_signal_processor.channel_number // 2
        if L < M:
            if ambiguity_warning != "":
                ambiguity_warning += "\n"
            ambiguity_warning += "WARNING: If decorrelation is used with UCA, please try to keep radius of the array as large as possible."
    else:
        uca_decorrelation_warning = ""

    if ant_arrangement == "UCA" and doa_method == "ROOT-MUSIC":
        uca_root_music_warning = "WARNING: Using ROOT-MUSIC method with UCA array is still experimental as it might produce inconsistent results."
    elif ant_arrangement == "Custom" and doa_method == "ROOT-MUSIC":
        uca_root_music_warning = "WARNING: ROOT-MUSIC cannot be used with 'Custom' antenna arrangement."
    else:
        uca_root_music_warning = ""

    web_interface.module_signal_processor.DOA_ant_alignment = ant_arrangement
    web_interface._doa_fig_type = doa_fig_type
    web_interface.module_signal_processor.doa_measure = doa_fig_type
    web_interface.compass_offset = compass_offset
    web_interface.module_signal_processor.compass_offset = compass_offset
    web_interface.module_signal_processor.ula_direction = ula_direction
    web_interface.module_signal_processor.array_offset = array_offset

    if en_peak_hold is not None and len(en_peak_hold):
        web_interface.module_signal_processor.en_peak_hold = True
    else:
        web_interface.module_signal_processor.en_peak_hold = False

    web_interface.module_signal_processor.DOA_expected_num_of_sources = expected_num_of_sources
    num_of_sources = (
        [
            {
                "label": f"{c}",
                "value": c,
            }
            for c in range(1, web_interface.module_signal_processor.channel_number)
        ]
        if "MUSIC" in doa_method
        else [
            {
                "label": "N/A",
                "value": c,
            }
            for c in range(1, web_interface.module_signal_processor.channel_number)
        ]
    )

    num_of_sources_state = False if "MUSIC" in doa_method else True

    return [
        str(ant_spacing_wavelength),
        spacing_label,
        ambiguity_warning,
        doa_decorrelation_method_options,
        doa_decorrelation_method_state,
        uca_decorrelation_warning,
        uca_root_music_warning,
        num_of_sources,
        num_of_sources_state,
    ]
