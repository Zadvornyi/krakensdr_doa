from dash_extensions.enrich import DashProxy
from kraken_web_doa import init_plot_doa
from kraken_web_interface import WebInterface
from kraken_web_spectrum import init_spectrum_fig
from variables import doa_fig, fig_layout, trace_colors
from waterfall import init_waterfall


app = DashProxy(__name__, compress=True, prevent_initial_callbacks=True, suppress_callback_exceptions=True)
app.title = "KrakenSDR DoA"
app.config.suppress_callback_exceptions = True


#############################################
#          Prepare Dash application         #
############################################
web_interface = WebInterface()

#############################################
#       Prepare component dependencies      #
#############################################
spectrum_fig = init_spectrum_fig(web_interface, fig_layout, trace_colors)
waterfall_fig = init_waterfall(web_interface)
doa_fig = init_plot_doa(web_interface, doa_fig)
