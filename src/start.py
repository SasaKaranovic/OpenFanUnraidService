import sys
import signal
import time
from math import ceil
from bisect import bisect_left
import click
from base_logger import logger, set_logger_level
from temperature_sensors import TemperatureSensors
from openfan_client import OpenFanClient
from fan_configuration import FanConfiguration

# pylint: disable=too-many-positional-arguments
class FanController:
    def __init__(self,
                 file_sensors,
                 file_profiles,
                 openfan_host='localhost',
                 openfan_port='3000',
                 update_period=10):

        logger.info("Starting OpenFAN - Unraid fan control app")

        logger.info("Loading temperature sensors")
        self.sensors = TemperatureSensors(file=file_sensors)

        logger.info("Loading fan profiles")
        self.config = FanConfiguration(profile_file=file_profiles)

        self.openfan_client = OpenFanClient(openfan_host, openfan_port)
        self.update_period = max(update_period, 2)

    def read_temperature(self):
        self.sensors.read_temperature()

    def update_fan_controls(self):
        fans = self.config.get_fan_controls()
        for _, fan in fans.items():
            self.update_fan(fan)

    def update_fan(self, fanData):
        profile = self.config.get_fan_profile(fanData['AssignedProfile'])
        if profile is None:
            logger.debug(f"Fan `{fanData['Identifier']}` has no assigned profile. Skipping...")
            return False

        curveType = profile.get('CurveType')
        temperature = self.sensors.get_sensor(profile['TempSource'])

        if profile is None:
            logger.error("Invalid profile data!")
            return False

        if temperature is None:
            logger.error("Invalid temp data!")
            return False

        fan_value = self.calculate_new_fan_value(profile, temperature, curveType)
        if profile.get('UsePWM', False):
            logger.debug(f"Setting fan {fanData['Identifier']} to {fan_value}% PWM based on sensor temperature of {temperature}°C")
            return self.openfan_client.set_fan_pwm(fanData['Identifier'], fan_value)
        logger.debug(f"Setting fan {fanData['Identifier']} to {fan_value} RPM based on sensor temperature of {temperature}°C")
        return self.openfan_client.set_fan_rpm(fanData['Identifier'], fan_value)

    def _curve_threshold(self, profile, temperature):
        new_value = 0
        for threshold, value in profile['Points'].items():
            if temperature >= threshold:
                new_value = value
        return new_value

    def _curve_linear(self, profile, temperature):
        points = list(profile['Points'].keys())
        values = list(profile['Points'].values())
        insertion = bisect_left(points, temperature)

        if insertion == 0:
            return values[0]

        if insertion >= len(values):
            return values[-1]

        x1=points[insertion-1]
        y1=values[insertion-1]
        x2=points[insertion]
        y2=values[insertion]
        value = ceil(((y2-y1)/(x2-x1)) * (temperature-x1) + y1)
        return value

    def calculate_new_fan_value(self, profile, temperature, curveType):
        if curveType == 'threshold':
            return self._curve_threshold(profile, temperature)

        if curveType == 'linear':
            return self._curve_linear(profile, temperature)

        logger.error("Unknown curve type ``! Falling back to threshold!")
        return self.calculate_new_fan_value(profile, temperature, 'threshold')

    def run_forever(self, live_reload=False):
        while True:
            if live_reload:
                self.config.reload()
            self.read_temperature()
            self.update_fan_controls()
            time.sleep(self.update_period)

def signal_handler(sigNum, frame):
    logger.info(f"Received `{sigNum}`/`{frame}`. Exiting...")
    print('\r\nYou pressed Ctrl+C!')
    sys.exit(0)

@click.command()
@click.option('--host', envvar='OPENFAN_HOST', required=True, help="IP address of the OpenFAN Controller API service")
@click.option('--port', envvar='OPENFAN_PORT', required=True, help="Port of the OpenFAN Controller API service")
@click.option('-s', '--sensors', envvar='OPENFAN_SENSORS', required=True, help="Path to disk sensors file (`default `/mnt/OpenFanService/sensors/disks.ini`)")
@click.option('-p', '--profile', envvar='OPENFAN_PROFILE', required=True, help="Path to fan profile (default: `/mnt/OpenFanService/data/fan_profiles.yaml`)")
@click.option('-l', '--livereload', envvar='OPENFAN_RELOAD', required=True, help="Reload fan profiles before every update cycle")
def main(host, port, sensors, profile, livereload):
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    set_logger_level('debug')

    if livereload.lower() in ['true', '1', 'yes', 'y', 'on']: # pylint: disable=simplifiable-if-statement
        arg_live_reload = True
    else:
        arg_live_reload = False

    logger.info("---- Starting OpenFAN UnRAID Service ----")
    logger.info(f"-- API Host: `{host}:{port}`")
    logger.info(f"-- Sensors: `{sensors}`")
    logger.info(f"-- Profile: `{profile}`")
    logger.info(f"-- LiveReload: `{arg_live_reload}`")


    OpenFan = FanController(sensors, profile, openfan_host=host, openfan_port=port)
    OpenFan.run_forever(live_reload=arg_live_reload)

if __name__ == "__main__":
    main(None, None, None, None, None)
