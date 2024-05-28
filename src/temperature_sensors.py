import os
import configparser


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
            self.sensors[sensor] = temp

    def list_sensors(self):
        return self.sensors

    def get_sensor(self, sensorID):
        temp = self.sensors.get(sensorID, None)
        if temp == '*':
            return 0
        return temp
