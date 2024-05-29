import time
import requests
from base_logger import logger

class OpenFanClient:
    def __init__(self, host, port=3000):
        self.host = host
        self.port = port
        self.api_url = f"http://{self.host}:{self.port}/api/v0"
        self.next_api_fetch = 0
        self.api_fetch_period = 1
        self.fan_data = {}

    def _fetch_api_data(self):
        if time.time() >= self.next_api_fetch:
            try:
                r = requests.get(f'{self.api_url}/fan/status', verify=False, timeout=(0.5, 1))
            except requests.exceptions.ConnectTimeout as e:
                logger.error("Server timeout...")
                logger.error(e)
                return
            response = r.json()

            if response['status'] == 'ok':
                self.next_api_fetch = time.time() + self.api_fetch_period
                self.fan_data = response['data']
            else:
                # Log error
                pass

    def get_fan_rpm(self):
        self._fetch_api_data()
        return self.fan_data

    def set_fan_pwm(self, fanIdentifier, pwm):
        fan = self._fan_id_to_number(fanIdentifier)

        try:
            r = requests.get(f'{self.api_url}/fan/{fan}/set?value={pwm}', verify=False, timeout=(0.5, 1))
        except requests.exceptions.ConnectTimeout as e:
            logger.error("Server timeout...")
            logger.error(e)
            return False

        response = r.json()

        if response['status'] == 'ok':
            logger.debug(f"Fan `{fan}` set to `{pwm}%` PWM")
            return True
        logger.debug(f"Error trying to set fan `{fan}%` set to `{pwm}` PWM")
        return False

    def set_fan_rpm(self, fanIdentifier, rpm):
        fan = self._fan_id_to_number(fanIdentifier)

        try:
            r = requests.get(f'{self.api_url}/fan/{fan}/rpm?value={rpm}', verify=False, timeout=(0.5, 1))
        except requests.exceptions.ConnectTimeout as e:
            logger.error("Server timeout...")
            logger.error(e)
            return False

        response = r.json()

        if response['status'] == 'ok':
            logger.debug(f"Fan `{fan}` set to `{rpm}` RPM")
            return True
        logger.debug(f"Error trying to set fan `{fan}` set to `{rpm}` RPM")
        return False

    def _fan_id_to_number(self, fanIdentifier):
        return fanIdentifier.replace('OpenFAN/Fan/', '')
