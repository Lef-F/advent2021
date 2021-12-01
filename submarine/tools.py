from typing import List, Union

import pandas as pd


class Tools:
    """Submarine basics"""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: str = None,
    ) -> None:
        """Connect your submarine tools to an input signal

        Args:
            input (str): Path to input file
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

    def _step_template(
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

    def _diff(self, df: pd.DataFrame) -> dict:
        diff = {}
        for col in df.columns:
            step_decrements = (df[col].dropna().diff() < 0).sum()
            step_increments = (df[col].dropna().diff() > 0).sum()
            step_other = df.shape[0] - step_decrements - step_increments
            diff.update(
                self._step_template(
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
        return self._diff(self.input_df)

    def get_windowed_radar_step_directions(self, window: int) -> dict:
        return self._diff(self._rolling_sum(window=window))


if __name__ == "__main__":
    raise NotImplementedError()
