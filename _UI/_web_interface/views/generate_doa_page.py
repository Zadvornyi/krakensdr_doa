from dash import dcc, html
from variables import doa_fig
# isort: off
from maindash import web_interface


# isort: on
def get_doa_max_str():
    doa_max_str = "deg"
    if web_interface.doa_thetas is not None and web_interface.doa_results[0].size > 0:
        doa_max_str = str(web_interface.doas[0]) + "°"

        if web_interface._doa_fig_type == "Compass" :
            doa_max_str = (360 - web_interface.doas[0] + web_interface.compass_offset) % 360

    return doa_max_str


layout = html.Div(
    [
        html.Div(
            [
                html.Div("MAX DOA Angle:", id="label_doa_max", className="field-label"),
                html.Div(get_doa_max_str(), id="body_doa_max", className="field-body"),
            ],
            className="field",
        ),
        # html.Div([
        dcc.Graph(
            style={"height": "inherit"},
            id="doa-graph",
            figure=doa_fig,  # fig_dummy #doa_fig #fig_dummy
        ),
    ],
    style={"width": "100%", "height": "80vh"},
)
