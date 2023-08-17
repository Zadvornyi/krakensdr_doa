import os

current_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.join("krakensdr_doa/", os.path.dirname(current_path))
shared_path = os.path.join(root_path, "_share")

# Import Kraken SDR modules
receiver_path = os.path.join(root_path, "_receiver")

AUTO_GAIN_VALUE = -100.0
