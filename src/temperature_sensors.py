import os
import configparser
from base_logger import logger

class TemperatureSensors:
    def __init__(self, file):
        if not os.path.isfile(file):
            raise FileExistsError(f"Sensor file `{file}` does not exist!")

        self.sensors = {}
        self.sensor_file = file
        self.cfgParser = configparser.ConfigParser()
        self.cfgParser.read(self.sensor_file)
        self.read_temperature()

    def read_temperature(self):
        self.cfgParser.read(self.sensor_file)
        self._parse()

    def _parse(self):
        for section in self.cfgParser.sections():
            temp = self.cfgParser[section].get('temp', '"-1"').replace('\"', '')
            sensor = section.replace('\"', '')
            logger.debug(f"Sensor `{sensor}` temperature is `{temp}°C`")
            self.sensors[sensor] = temp

    def list_sensors(self):
        return self.sensors

    def get_single_sensor(self, sensorID):
        temp = self.sensors.get(sensorID, None)
        if temp is None:
            logger.error(f"Could not find sensor!. (`{sensorID}`)")
            return -1

        if temp == '*':
            return 0
        return int(temp)

    def get_sensors(self, sensor_list):
        if isinstance(sensor_list, list):
            temperature_list = []
            for sensor in sensor_list:
                temp = self.get_single_sensor(sensor)
                temperature_list.append(temp)
            return temperature_list

        if isinstance(sensor_list, str):
            return [ self.get_single_sensor(sensor_list) ]

        raise TypeError(f"Unsupported sensor type! Function expects either `list` or `str` but `{type(sensor_list)}` was given.")
