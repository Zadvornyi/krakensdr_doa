from dash import Input, Output
from maindash import app, web_interface


@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    web_interface.vfo_cfg_inputs,
    prevent_initial_call=True
)
def update_vfo_params(*args):
    print("update_data_recording_params")
    # Get dict of input variables
    input_names = [item.component_id for item in web_interface.vfo_cfg_inputs]
    kwargs_dict = dict(zip(input_names, args))

    web_interface.module_signal_processor.spectrum_fig_type = kwargs_dict["spectrum_fig_type"]
    web_interface.module_signal_processor.vfo_mode = kwargs_dict["vfo_mode"]
    web_interface.module_signal_processor.vfo_default_demod = kwargs_dict["vfo_default_demod"]
    web_interface.module_signal_processor.vfo_default_iq = kwargs_dict["vfo_default_iq"]
    web_interface.module_signal_processor.max_demod_timeout = int(kwargs_dict["max_demod_timeout"])

    active_vfos = kwargs_dict["active_vfos"]
    # If VFO mode is in the VFO-0 Auto Max mode, we active VFOs to 1 only
    if kwargs_dict["vfo_mode"] == "Auto":
        active_vfos = 1
        app.push_mods({"active_vfos": {"value": 1}})

    web_interface.module_signal_processor.dsp_decimation = max(int(kwargs_dict["dsp_decimation"]), 1)
    web_interface.module_signal_processor.active_vfos = active_vfos
    web_interface.module_signal_processor.output_vfo = kwargs_dict["output_vfo"]

    en_optimize_short_bursts = kwargs_dict["en_optimize_short_bursts"]
    if en_optimize_short_bursts is not None and len(en_optimize_short_bursts):
        web_interface.module_signal_processor.optimize_short_bursts = True
    else:
        web_interface.module_signal_processor.optimize_short_bursts = False

    for i in range(web_interface.module_signal_processor.max_vfos):
        if i < kwargs_dict["active_vfos"]:
            app.push_mods({"vfo" + str(i): {"style": {"display": "block"}}})
        else:
            app.push_mods({"vfo" + str(i): {"style": {"display": "none"}}})

    if web_interface.daq_fs > 0:
        bw = web_interface.daq_fs / web_interface.module_signal_processor.dsp_decimation
        vfo_min = web_interface.daq_center_freq - bw / 2
        vfo_max = web_interface.daq_center_freq + bw / 2

        for i in range(web_interface.module_signal_processor.max_vfos):
            web_interface.module_signal_processor.vfo_bw[i] = int(
                min(kwargs_dict["vfo_" + str(i) + "_bw"], bw * 10 ** 6)
            )
            web_interface.module_signal_processor.vfo_fir_order_factor[i] = int(
                kwargs_dict["vfo_" + str(i) + "_fir_order_factor"]
            )
            web_interface.module_signal_processor.vfo_freq[i] = int(
                max(min(kwargs_dict["vfo_" + str(i) + "_freq"], vfo_max), vfo_min) * 10 ** 6
            )
            web_interface.module_signal_processor.vfo_squelch[i] = int(kwargs_dict["vfo_" + str(i) + "_squelch"])
            web_interface.module_signal_processor.vfo_demod[i] = kwargs_dict[f"vfo_{i}_demod"]
            web_interface.module_signal_processor.vfo_iq[i] = kwargs_dict[f"vfo_{i}_iq"]
