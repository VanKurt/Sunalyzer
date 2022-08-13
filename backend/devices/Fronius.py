# import json
import requests


# Fronius Symo/Gn24 devices
class Fronius:
    def __init__(self, config):
        # Demo code for config access
        print(f"""Fronius device:
            configured host name is {config['fronius']['host_name']}""")

        self.host_name = config['fronius']['host_name']

        self.url = (f"http://{self.host_name}/",
                    "solar_api/v1/GetPowerFlowRealtimeData.fcgi")

        # Initialize with values
        self.total_energy_produced_kwh = 0.0
        self.total_energy_consumed_kwh = 0.0
        self.total_energy_fed_in_kwh = 0.0
        self.current_power_produced_kw = 0.0
        self.current_power_consumed_kw = 0.0
        self.current_power_fed_in_kw = 0.0

    def copy_data(self, data):
        '''Copies the results from the API request.'''
        # Todo
        self.total_energy_produced_kwh = self.total_energy_produced_kwh + 1
        self.total_energy_consumed_kwh = self.total_energy_consumed_kwh + 1
        self.total_energy_fed_in_kwh = self.total_energy_fed_in_kwh + 1
        self.current_power_produced_kw = self.current_power_produced_kw + 1
        self.current_power_consumed_kw = self.current_power_consumed_kw + 1
        self.current_power_fed_in_kw = self.current_power_fed_in_kw + 1

    def update(self):
        '''Updates all device stats.'''
        try:
            r = requests.get(self.url, timeout=10)
            r.raise_for_status()
            self.copy_data(r.json())
        except requests.exceptions.Timeout:
            print(f"Fronius device: Timeout requesting {self.url}")
        except requests.exceptions.RequestException as e:
            print(f"Fronius device: requests exception {e} for URL {self.url}")
