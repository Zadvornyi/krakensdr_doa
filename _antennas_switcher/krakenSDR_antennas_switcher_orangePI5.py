import bisect
import wiringpi
from wiringpi import GPIO
class AntennasSwitcher:
    # switching frequency.
    setting = {
        "thresholds": [
            250,
            611,
            3000
        ],
        "inputsOrderByBand": [
            0,
            1,
            2,
            3
        ]
    }
    # Set default pins for antenna switch control inputs.
    gpio_sw_a = 6
    gpio_sw_b = 10

    def __init__(self, daq_center_freq):
        # Init GPIOs.
        print('init antennas switcher.')

        wiringpi.wiringPiSetup()
        wiringpi.pinMode(self.gpio_sw_a, GPIO.OUTPUT)
        wiringpi.pinMode(self.gpio_sw_b, GPIO.OUTPUT)

        # Init center freq
        self.changeAntennas(daq_center_freq)

    def changeAntennas(self, frequency):
        # Validate data in ws message.
        if type(frequency) in (int, float):
            # Obtain switch control state.
            ab = list(self.setting.get('inputsOrderByBand'))[
                bisect.bisect_left(
                    sorted(list(self.setting.get('thresholds'))),
                    frequency)
            ]
            # Switching.
            wiringpi.digitalWrite(self.gpio_sw_a, ab & 0x01)
            wiringpi.digitalWrite(self.gpio_sw_b, ab & 0x02)
            # Send info response.
            print(frequency, 'frequency')
            print(f'AB state: {ab}')
        else:
            print('Wrong antennas switcher frequency configuration.')


AntennasSwitcher(659)