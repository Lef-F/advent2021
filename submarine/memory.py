class PowerConsumptionData:
    def __init__(self) -> None:
        self.power_consumption_stats = {
            "bits_per_line": 0,
            "bits_per_position": {"0": {}, "1": {}},
            "most_common_bits": [],
            "least_common_bits": [],
            "gamma_rate": 0,
            "epsilon_rate": 0,
            "power_consumption": 0,
        }


class NavigationData:
    def __init__(self) -> None:
        self.navigation_trace = {
            "depth": [],
            "horizontal": [],
            "aim": [],
        }

    def _reset_trace(self) -> None:
        for k in self.navigation_trace.keys():
            self.navigation_trace[k] = []


class RadarData:
    def _radar_stats(
        self,
        col: str,
        step_increments: str,
        step_decrements: str,
        step_other: str,
    ) -> dict:
        return {
            col: {
                "increments": step_increments,
                "decrements": step_decrements,
                "other": step_other,
            }
        }
