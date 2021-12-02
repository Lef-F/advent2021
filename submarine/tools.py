from typing import List, Union

import pandas as pd


class InputSignal:
    """Submarine basic toolset from IKEA"""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: List[str] = None,
    ) -> None:
        """Connect your submarine tools to an input signal

        Args:
            input (str): The path to the csv file with the input signal
            header_location (int, optional): The row on which the csv header appears. Defaults to None.
            column_names (List[str], optional): The name for the columns in the csv file, if they don't exist in it. Defaults to None.
        """
        self.input = input
        self.header_location = header_location
        self.input_df = self._input_loader(
            header_location=header_location,
            column_names=column_names,
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


if __name__ == "__main__":
    raise NotImplementedError()
