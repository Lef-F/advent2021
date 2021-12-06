from typing import List, Union

import matplotlib.pyplot as plt
import pandas as pd

from submarine.inputs import InputSignal
from submarine.memory import (
    NavigationData,
    PowerConsumptionData,
    RadarData,
)


class Diagnostics(InputSignal):
    """Submarine's self diagnostics system"""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: List[str] = None,
        data_type: type = str,
        squeeze: bool = True,
    ) -> None:
        InputSignal.__init__(
            self,
            input=input,
            header_location=header_location,
            column_names=column_names,
            data_type=data_type,
            squeeze=squeeze,
        )

    def _binary_str_to_int(self, binary: str) -> int:
        """Convert binary code to integer.
        It treats that input as a binary number (base 2) and converts it to a decimal integer (base 10). It
        returns an integer result.
        Copied from https://stackoverflow.com/a/32834431

        Args:
            binary (str): The binary number to be converted to integer.

        Returns:
            int: The converted integer.
        """
        length = len(binary)
        num = 0
        for i in range(length):
            num = num + int(binary[i])
            num = num * 2
        return int(num / 2)


class PowerConsumption(Diagnostics, PowerConsumptionData):
    """Measure submarine's current power consumption"""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: List[str] = None,
        data_type: type = str,
        squeeze: bool = True,
        verbose: bool = True,
    ) -> None:
        Diagnostics.__init__(
            self,
            input=input,
            header_location=header_location,
            column_names=column_names,
            data_type=data_type,
            squeeze=squeeze,
        )
        PowerConsumptionData.__init__(self)

        # Calculate power consumption stats from input
        self.power_consumption_stats["bits_per_line"] = (
            self.input_df.astype(str).apply(len).max()
        )
        self._count_bits()
        self._calculate_popularity()
        self._calculate_rates()
        self.power_consumption = self._power_consumption()
        if verbose:
            print("Submarine's current power consumption is", self.power_consumption)

    def _count_bits(self):
        """Count the occurrence of 0 and 1 bits per position over all rows of the input."""
        for input in self.input_df:
            for pos, digit in enumerate(str(input)):
                try:
                    self.power_consumption_stats["bits_per_position"][digit][
                        str(pos)
                    ] += 1
                except KeyError:
                    self.power_consumption_stats["bits_per_position"][digit][
                        str(pos)
                    ] = 1

    def _calculate_popularity(self):
        """Measure which bits (0,1) are the most common per position."""
        for pos in range(self.power_consumption_stats["bits_per_line"]):
            if (
                self.power_consumption_stats["bits_per_position"]["0"][str(pos)]
                > self.power_consumption_stats["bits_per_position"]["1"][str(pos)]
            ):
                self.power_consumption_stats["most_common_bits"].append("0")
                self.power_consumption_stats["least_common_bits"].append("1")
            elif (
                self.power_consumption_stats["bits_per_position"]["0"][str(pos)]
                < self.power_consumption_stats["bits_per_position"]["1"][str(pos)]
            ):
                self.power_consumption_stats["most_common_bits"].append("1")
                self.power_consumption_stats["least_common_bits"].append("0")

    def _calculate_rates(self):
        """Calculate the gamma and epsilon rates."""
        self.power_consumption_stats["epsilon_rate"] = "".join(
            self.power_consumption_stats["least_common_bits"]
        )
        self.power_consumption_stats["gamma_rate"] = "".join(
            self.power_consumption_stats["most_common_bits"]
        )

    def _power_consumption(self):
        """Calculate the total power consumption of the submarine reported by the diagnostics."""
        if not self.power_consumption_stats["power_consumption"]:
            epsilon_rate = self._binary_str_to_int(
                self.power_consumption_stats["epsilon_rate"],
            )
            gamma_rate = self._binary_str_to_int(
                self.power_consumption_stats["gamma_rate"],
            )
            self.power_consumption_stats["power_consumption"] = (
                epsilon_rate * gamma_rate
            )

        return self.power_consumption_stats["power_consumption"]


class LifeSupport(Diagnostics):
    """Evaluate the status of the life support systems onboard."""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: List[str] = None,
        data_type: type = str,
        squeeze: bool = True,
        verbose: bool = True,
    ) -> None:
        Diagnostics.__init__(
            self,
            input=input,
            header_location=header_location,
            column_names=column_names,
            data_type=data_type,
            squeeze=squeeze,
        )

        self.most_common = {}
        self.most_common["binary"] = self._search(input=self.input_df, most_common=True)
        self.most_common["int"] = self._binary_str_to_int(self.most_common["binary"])
        self.least_common = {}
        self.least_common["binary"] = self._search(
            input=self.input_df, most_common=False
        )
        self.least_common["int"] = self._binary_str_to_int(self.least_common["binary"])
        self.life_support_rating = self.most_common["int"] * self.least_common["int"]
        if verbose:
            print(
                "Submarine's current life support rating is", self.life_support_rating
            )

    def _bit_stats(self, data: list, bit_pos: int):
        """Find which rows of the data have which bit (0,1) at the given bit position.

        Args:
            data (list): The input data
            bit_pos (int): The bit position to search at

        Returns:
            dict: A dictionary with two lists documenting which row has which bit on the given position.
        """
        bits = {"0": [], "1": []}
        for row, binary in enumerate(data):
            bits[binary[bit_pos]].append(row)
        return bits

    def _search(
        self, input: List[str], bit_pos: int = 0, most_common: bool = True
    ) -> str:
        """A recursive search function to perform comparisons of bits on one position at a time
        in order to determine which binary number fullfills the search requirements.

        Args:
            input (list): A list of binary numbers
            bit_pos (int, optional): The bit position to search at the current recursion level. Defaults to 0.
            most_common (bool, optional): If True, search for the most popular (or 1) bits, otherwise the least popular (or 0).
                Defaults to True.

        Returns:
            str: The binary number that is the result of the search.
        """
        if most_common:
            greater = "1"
            lesser = "0"
        else:
            greater = "0"
            lesser = "1"

        if len(input) == 1:
            return input[0]

        stats = self._bit_stats(input, bit_pos)

        if len(stats[lesser]) < len(stats[greater]):
            result = self._search(
                [input[i] for i in stats["0"]], bit_pos + 1, most_common=most_common
            )
        elif len(stats[lesser]) > len(stats[greater]):
            result = self._search(
                [input[i] for i in stats["1"]], bit_pos + 1, most_common=most_common
            )
        elif len(stats[lesser]) == len(stats[greater]):
            result = self._search(
                [input[i] for i in stats[lesser]], bit_pos + 1, most_common=most_common
            )
        return result


class Radar(InputSignal, RadarData):
    """Submarine's radar"""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: List[str] = None,
    ) -> None:
        InputSignal.__init__(
            self,
            input,
            header_location=header_location,
            column_names=column_names,
        )
        RadarData.__init__(self)

    def _diff(self, df: pd.DataFrame) -> dict:
        diff = {}
        for col in df.columns:
            step_decrements = (df[col].dropna().diff() < 0).sum()
            step_increments = (df[col].dropna().diff() > 0).sum()
            step_other = df.shape[0] - step_decrements - step_increments
            diff.update(
                self._radar_stats(
                    col,
                    step_increments,
                    step_decrements,
                    step_other,
                )
            )
        return diff

    def _rolling_sum(self, window: int) -> dict:
        return self.input_df.rolling(window).sum()

    def get_radar_step_directions(self) -> dict:
        """Radar will crunch the numbers and return the pair of steps that were increments, decrements or other.

        Examples:
            If the signal would look as follows:
            ```
            199, NaN
            200, increased
            208, increased
            210, increased
            200, decreased
            207, increased
            240, increased
            269, increased
            260, decreased
            263, increased
            ```

            Running `get_radar_step_directions` would return:
            {'signal': {'increments': 7, 'decrements': 2, 'other': 1}}

        Returns:
            dict: The step statistics per column
        """
        return self._diff(self.input_df)

    def get_windowed_radar_step_directions(self, window: int) -> dict:
        """Configure the radar to perform a windowed aggregation of the steps that were increments, decrements or other.

        Examples:
            If the signal would look as follows:
            ```
            199
            200
            208
            210
            200
            207
            240
            269
            260
            263
            ```

            Running `get_windowed_radar_step_directions` with `window=3` would process the input signal into:
            ```
            199, NaN, NaN
            200, NaN, NaN
            208, 607, NaN
            210, 618, increments
            200, 618, same
            207, 617, decrements
            240, 647, increments
            269, 716, increments
            260, 769, increments
            263, 792, increments
            ```
            And then return:
            {'signal': {'increments': 6, 'decrements': 1, 'other': 1}}

        Args:
            window (int): The size of the window in rows

        Returns:
            dict: The step statistics per column
        """
        return self._diff(self._rolling_sum(window=window))


class Navigation(InputSignal, NavigationData):
    """The submarine's advanced navigation system."""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: List[str] = None,
    ) -> None:
        InputSignal.__init__(
            self,
            input,
            header_location=header_location,
            column_names=column_names,
        )
        NavigationData.__init__(self)

    def show_plan(self, activate_aim: bool = False) -> None:
        """Display the navigation plan on-screen.

        Args:
            activate_aim (bool, optional): Toggle to accommodate for the aiming functionality. Defaults to False.
        """
        if activate_aim:
            plt.scatter(
                self.navigation_trace["horizontal"],
                [-1 * h for h in self.navigation_trace["aim"]],
                c=self.navigation_trace["depth"],
            )
            ylabel = "Aim"
            cbar = plt.colorbar()
            cbar.set_label("Depth", rotation=270)
        else:
            plt.plot(
                self.navigation_trace["horizontal"],
                [-1 * h for h in self.navigation_trace["depth"]],
            )
            ylabel = "Depth"
        plt.title("Submarine planned route directions")
        plt.ylabel(ylabel)
        plt.xlabel("Horizontal")
        plt.show()

    def calculate_path(
        self, activate_aim: bool = False, plot: bool = True, get: bool = False
    ) -> dict:
        """Calculate the path from the commands provided.

        Args:
            activate_aim (bool, optional): Activate the aiming systems and navigation will accommodate for precise aim.
                Defaults to False because we're not hostile by default.
            plot (bool, optional): Display the navigation route on-screen. Defaults to True.

        Returns:
            dict: The expected measures of depth, horizontal and aim values at each step of the journey.
        """
        self._reset_trace()
        depth = 0
        horizontal = 0
        aim = 0
        for direction in self.input_df.iterrows():
            command = direction[1]["signal"].split()
            if command[0] == "forward":
                horizontal += int(command[1])
                if activate_aim:
                    depth += aim * int(command[1])
            if command[0] == "down":
                if activate_aim:
                    aim += int(command[1])
                else:
                    depth += int(command[1])
            if command[0] == "up":
                if activate_aim:
                    aim -= int(command[1])
                else:
                    depth -= int(command[1])
            self.navigation_trace["depth"].append(depth)
            self.navigation_trace["horizontal"].append(horizontal)
            if activate_aim:
                self.navigation_trace["aim"].append(aim)
        if plot:
            self.show_plan(activate_aim=activate_aim)
        print(
            "The product of `depth` and `horizontal` values at the final destination will be:",
            depth * horizontal,
        )
        if get:
            return self.navigation_trace
