# KrakenSDR Signal Processor
#
# Copyright (C) 2018-2023  Carl Laufer, Tamás Pető, Mykola Dvornik, Andrii Zadvornyi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# - coding: utf-8 -*-

# isort: off
from maindash import app

# isort: on

from views import main
from threading import Timer
app.layout = main.layout

# It is workaround for splitting callbacks in separate files (run callbacks after layout)
from callbacks import (  # noqa: F401; daq_reconfiguration,
    display_page,
    doa_configuration,
    gps_configuration,
    main,
    spectrum_page,
    subprocess,
    toggle_beta_features,
    update_daq_params,
    update_vfo_params,
)

def test_print():
    print('TEST PRINT')

if __name__ == "__main__":
    t = Timer(0.2, test_print)
    t.start()
    from threading import Timer
    # Debug mode does not work when the data interface is set to shared-memory
    # "shmem"!
    app.run_server(debug=False, host="0.0.0.0", port=8080)
