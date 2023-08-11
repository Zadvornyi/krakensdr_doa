import numpy as np
import plotly.graph_objects as go
from variables import figure_font_size, x, y


def init_plot_doa(web_interface, doa_fig):
    doa_fig.data = []
    # Just generate with junk data initially, as the spectrum array may not
    # be ready yet if we have sqeulching active etc.
    # --- Linear plot ---
    if web_interface._doa_fig_type == "Linear":
        # Plot traces
        doa_fig.add_trace(
            go.Scattergl(
                x=x,  # web_interface.doa_thetas,
                y=y,
            )
        )

        doa_fig.update_xaxes(
            title_text="Incident angle [deg]",
            color="rgba(255,255,255,1)",
            title_font_size=20,
            tickfont_size=figure_font_size,
            mirror=True,
            ticks="outside",
            showline=True,
        )
        doa_fig.update_yaxes(
            title_text="Amplitude [dB]",
            color="rgba(255,255,255,1)",
            title_font_size=20,
            tickfont_size=figure_font_size,
            # range=[-5, 5],
            mirror=True,
            ticks="outside",
            showline=True,
        )
    # --- Polar plot ---
    elif web_interface._doa_fig_type == "Polar":
        label = "DOA Angle"  # web_interface.doa_labels[i]
        doa_fig.add_trace(
            go.Scatterpolargl(
                theta=x,  # web_interface.doa_thetas,
                r=y,  # doa_result,
                name=label,
                fill="toself",
            )
        )

        doa_fig.update_layout(
            polar=dict(
                radialaxis_tickfont_size=figure_font_size,
                angularaxis=dict(rotation=90, tickfont_size=figure_font_size),
            )
        )

    # --- Compass  ---
    elif web_interface._doa_fig_type == "Compass":
        doa_fig.update_layout(
            polar=dict(
                radialaxis_tickfont_size=figure_font_size,
                angularaxis=dict(
                    rotation=90 + web_interface.compass_offset,
                    direction="clockwise",
                    tickfont_size=figure_font_size,
                ),
            )
        )

        label = "DOA Angle"

        doa_fig.add_trace(
            go.Scatterpolargl(
                theta=x,  # (360-web_interface.doa_thetas+web_interface.compass_offset)%360,
                r=y,  # doa_result,
                name=label,
                fill="toself",
            )
        )

def plot_doa(web_interface):
    update_data = []
    if web_interface.doa_thetas is not None and web_interface.doa_results[0].size > 0:
        thetas = web_interface.doa_thetas
        result = web_interface.doa_results[0]

        update_data = dict(x=[thetas], y=[result])

        if web_interface._doa_fig_type == "Polar":
            thetas = np.append(web_interface.doa_thetas, web_interface.doa_thetas[0])
            result = np.append(web_interface.doa_results[0], web_interface.doa_results[0][0])
            update_data = dict(theta=[thetas], r=[result])
        elif web_interface._doa_fig_type == "Compass":
            thetas = np.append(web_interface.doa_thetas, web_interface.doa_thetas[0])
            result = np.append(web_interface.doa_results[0], web_interface.doa_results[0][0])
            update_data = dict(theta=[(360 - thetas + web_interface.compass_offset) % 360], r=[result])

    return [update_data, [0], len(thetas)]