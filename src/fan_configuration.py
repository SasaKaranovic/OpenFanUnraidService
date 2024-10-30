import sys
import os
import json
from ruamel.yaml import YAML
from base_logger import logger

class FanConfiguration:
    def __init__(self, profile_file):
        if not os.path.isfile(profile_file):
            raise FileExistsError(f"Fan Profile file `{profile_file}` does not exist!")

        self.file = profile_file
        self.profile_data = {}
        self.fan_profiles = {}
        self.fan_controls = {}
        self.reload()

    def reload(self):
        self._readProfileFile()
        self._parse_profile_data()

    def _readProfileFile(self):
        if self.file.endswith('.yaml'):
            self._load_yaml()
        elif self.file.endswith('.json'):
            self._load_json()
        else:
            raise FileExistsError("Unsupported profile file type!")

    def _load_json(self):
        logger.info("--- Note: YAML file-type is supported:")
        logger.info("We recommend switching your fan profile format from JSON to YAML.")
        logger.info("As per user request, we have added .yaml support to improve readability of fan profiles.")
        logger.info("If you wish to convert your .json file to .yaml, you can use online JSON-to-YAML converters.")
        try:
            with open(self.file, "r", encoding='utf-8') as read_file:
                self.profile_data = json.load(read_file)

        except json.decoder.JSONDecodeError as e:
            logger.error("Error parsing profile file")
            logger.error(f"Error: {e}")
            sys.exit(-1)

    def _load_yaml(self):
        try:
            yaml = YAML(typ="safe")
            with open(self.file, "r", encoding='utf-8') as read_file:
                self.profile_data = yaml.load(read_file)

        except Exception as e:
            logger.error("Error parsing profile file")
            logger.error(f"Error: {e}")
            sys.exit(-1)

    def _parse_profile_data(self):
        profiles = self.profile_data.get('FanProfiles', None)
        controls = self.profile_data.get('FanControls', None)

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
            profilePoints = data.get('Points', [])
            points = {}

            for point in sorted(profilePoints):
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

    def get_fan_profile(self, identifier):
        if identifier == "":
            return None

        profile = self.fan_profiles.get(identifier, None)
        if profile is None:
            logger.error(f"Requested profile `{identifier}` which does not exist!")
        return profile

    def get_fan_controls(self):
        return self.fan_controls
