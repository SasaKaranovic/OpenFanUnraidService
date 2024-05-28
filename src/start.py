import sys
import signal
import time
import click
from base_logger import logger, set_logger_level
from temperature_sensors import TemperatureSensors
from openfan_client import OpenFanClient
from fan_configuration import FanConfiguration

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
        self.update_period = update_period

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

        temperature = self.sensors.get_sensor(profile['TempSource'])

        if profile is None:
            logger.error("Invalid profile data!")
            return False

        if temperature is None:
            logger.error("Invalid temp data!")
            return False

        fan_value = self.calculate_new_fan_value(profile, temperature)
        if profile.get('UsePWM', False):
            return self.openfan_client.set_fan_pwm(fanData['Identifier'], fan_value)
        return self.openfan_client.set_fan_rpm(fanData['Identifier'], fan_value)

    def calculate_new_fan_value(self, profile, temperature):
        new_value = 0

        for point in profile['Points']:
            p = point.split(',', 1)
            if temperature >= int(p[0]):
                new_value = int(p[1])
        return new_value

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
@click.option('-p', '--profile', envvar='OPENFAN_PROFILE', required=True, help="Path to fan profile (default: `/mnt/OpenFanService/data/fan_profiles.json`)")
@click.option('-l', '--livereload', envvar='OPENFAN_RELOAD', required=True, help="Reload fan profiles before every update cycle")
def main(host, port, sensors, profile, livereload):
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    set_logger_level('debug')

    if livereload.lower() in ['true', '1', 'yes', 'y', 'on']:
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
    main(None, None, None)
