from dash import Input, Output, State
from maindash import app, web_interface


@app.callback(
    Output("beta_features_container", "style"),
    [Input("en_beta_features", "value")],
    prevent_initial_call=True,
)
def toggle_beta_features(toggle_value):
    print('toggle_beta_features')
    web_interface.en_beta_features = toggle_value

    # Toggle VFO default configuration settings
    if toggle_value:
        return {"display": "block"}
    else:
        return {"display": "none"}


vfos_beta_freq_outputs = []
for i in range(web_interface.module_signal_processor.max_vfos):
    vfos_beta_freq_outputs.append(Output(f"beta_features_container-{str(i)}", "style"))


@app.callback(
    vfos_beta_freq_outputs,
    [Input("en_beta_features", "value")],
    prevent_initial_call=True,
)
def toggle_beta_vfos_features(toggle_value):
    toggle_output = []

    # Toggle individual VFO card settings
    for i in range(web_interface.module_signal_processor.max_vfos):
        if toggle_value:
            toggle_output.append({"display": "block"})
        else:
            toggle_output.append({"display": "none"})
    return toggle_output
