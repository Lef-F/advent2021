from typing import List

import matplotlib.pyplot as plt
import pandas as pd


class InputSignal:
    """Submarine basic toolset from IKEA"""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: List[str] = None,
        data_type: type = None,
    ) -> None:
        """Connect your submarine tools to an input signal

        Args:
            input (str): The path to the csv file with the input signal
            header_location (int, optional): The row on which the csv header appears. Defaults to None.
            column_names (List[str], optional): The name for the columns in the csv file, if they don't exist in it. Defaults to None.
            data_type (type, optional): The data type (if known) of the input data. Defaults to None.
                Read more at https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
        """
        self.input = input
        self.header_location = header_location
        self.input_df = self._input_loader(
            header_location=header_location,
            column_names=column_names,
            data_type=data_type,
        )
        self.input_shape = self.input_df.shape

    def _input_loader(self, header_location: int, column_names: List[str]):
        return pd.read_csv(
            self.input,
            header=header_location,
            names=column_names,
        )


class DataTemplates:
    def __init__(self) -> None:
        self.navigation_trace = {
            "depth": [],
            "horizontal": [],
            "aim": [],
        }

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

    def _reset_trace(self) -> None:
        for k in self.navigation_trace.keys():
            self.navigation_trace[k] = []


class Radar(InputSignal, DataTemplates):
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
        DataTemplates.__init__(self)

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


class Navigation(InputSignal, DataTemplates):
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
        DataTemplates.__init__(self)

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
