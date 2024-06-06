import sys
import os
import json
from base_logger import logger


class FanConfiguration:
    def __init__(self, profile_file):
        if not os.path.isfile(profile_file):
            raise FileExistsError(f"Fan Profile config file `{profile_file}` does not exist!")

        self.file = profile_file
        self.fan_profiles = {}
        self.fan_controls = {}
        self._readProfileFile()

    def _readProfileFile(self):
        try:
            with open(self.file, "r", encoding='utf-8') as read_file:
                data = json.load(read_file)
                self._parse_config_data(data)
        except json.decoder.JSONDecodeError as e:
            logger.error("Error parsing json file")
            logger.error(f"Error: {e}")
            sys.exit(-1)

    def reload(self):
        self._readProfileFile()


    def _parse_config_data(self, jsonData):
        profiles = jsonData.get('FanProfiles', None)
        controls = jsonData.get('FanControls', None)

        if profiles is None and controls is None:
            logger.error("Failed to load profiles and controls!")
            logger.error(f"Please double-check your `{self.file}` data file")
            return

        for p in profiles:
            self.create_fan_profile(p)

        for c in controls:
            self.create_fan_control(c)

    def create_fan_profile(self, data):
        try:
            name = data.get('Name', None)
            sensor = data.get('TempSource', "")
            usePWM = data.get('UsePWM', False)
            curveType = data.get('CurveType', 'threshold').lower()
            jsonPoints = data.get('Points', [])
            points = {}

            for point in sorted(jsonPoints):
                p = point.split(',', 1)
                points[int(p[0])] = int(p[1])

            if len(points) <= 0:
                logger.error(f"Profile `{name}` has no points!")
                raise KeyError(f"Profile `{name}` has no pints!")

            if curveType not in ['threshold', 'linear']:
                logger.error(f"Unsupported curve type `{curveType}`. Falling back to threshold.")
                curveType = 'threshold'

            self.fan_profiles[name] = {'Name': name, 'TempSource': sensor, 'UsePWM': usePWM, 'CurveType': curveType, 'Points': points, }
            logger.debug(f"Created profile {name}")
            logger.debug(f"-- Temp Source: `{sensor}` CurveType: `{curveType}` Points: {points}")
        except KeyError as e:
            logger.error("Invalid fan profile data:")
            logger.error(f"Error: {e}")
            logger.error(data)
            logger.error("---")
            return

    def create_fan_control(self, data):
        try:
            identifier = data.get('Identifier', None)
            self.fan_controls[identifier] = data
            logger.debug(f"Created fan control {identifier}")
            logger.debug(f"-- Assigned Profile: `{data['AssignedProfile']}`")
        except KeyError as e:
            logger.error("Invalid fan control data:")
            logger.error(f"Error: {e}")
            logger.error(data)
            logger.error("---")
            return

    def get_fan_profile(self, identifier):
        if identifier == "":
            return None

        profile = self.fan_profiles.get(identifier, None)
        if profile is None:
            logger.error(f"Requested profile `{identifier}` which does not exist!")
        return profile

    def get_fan_controls(self):
        return self.fan_controls
