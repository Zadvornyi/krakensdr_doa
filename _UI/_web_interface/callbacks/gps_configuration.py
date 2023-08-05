# isort: off
from maindash import app, web_interface

# isort: on

from dash import Input, Output, State


# Enable GPS Relevant fields
@app.callback(
    [Output("fixed_heading_div", "style"), Output("gps_status_info", "style")], [Input("loc_src_dropdown", "value")]
)
def toggle_gps_fields(toggle_value):
    if toggle_value == "gpsd":
        return [{"display": "block"}, {"display": "block"}]
    else:
        return [{"display": "none"}, {"display": "none"}]


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


# Set location data
@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [
        Input(component_id="latitude_input", component_property="value"),
        Input(component_id="longitude_input", component_property="value"),
        Input("loc_src_dropdown", "value"),
    ],
    prevent_initial_call=True
)
def set_static_location(lat, lon, toggle_value):
    if toggle_value == "Static":
        web_interface.module_signal_processor.latitude = lat
        web_interface.module_signal_processor.longitude = lon


# Enable Fixed Heading
@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="fixed_heading_check", component_property="value")],
    prevent_initial_call=True
)
def set_fixed_heading(fixed):
    if fixed:
        web_interface.module_signal_processor.fixed_heading = True
    else:
        web_interface.module_signal_processor.fixed_heading = False


# Set minimum speed for trustworthy GPS heading
@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="min_speed_input", component_property="value")],
    prevent_initial_call=True
)
def set_min_speed_for_valid_gps_heading(min_speed):
    web_interface.module_signal_processor.gps_min_speed_for_valid_heading = min_speed


# Set minimum speed duration for trustworthy GPS heading
@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="min_speed_duration_input", component_property="value")],
    prevent_initial_call=True
)
def set_min_speed_duration_for_valid_gps_heading(min_speed_duration):
    web_interface.module_signal_processor.gps_min_duration_for_valid_heading = min_speed_duration


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


# Set heading data
@app.callback(
    Output("dummy_output", "children", allow_duplicate=True),
    [Input(component_id="heading_input", component_property="value")],
    prevent_initial_call=True
)
def set_static_heading(heading):
    web_interface.module_signal_processor.heading = heading
