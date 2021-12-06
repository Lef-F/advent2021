from typing import List, Union

import pandas as pd


class InputSignal:
    """Submarine basic toolset from IKEA"""

    def __init__(
        self,
        input,
        header_location: int = None,
        column_names: List[str] = None,
        data_type: type = None,
        squeeze: bool = False,
    ) -> None:
        """Connect your submarine tools to an input signal

        Args:
            input (str): The path to the csv file with the input signal
            header_location (int, optional): The row on which the csv header appears. Defaults to None.
            column_names (List[str], optional): The name for the columns in the csv file, if they don't exist in it. Defaults to None.
            data_type (type, optional): The data type (if known) of the input data. Defaults to None.
                Read more at https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
            squeeze (bool, optional): Attempt to return a pandas Series if the input has only one column.
        """
        self.input = input
        self.input_df = self._input_loader(
            header_location=header_location,
            column_names=column_names,
            data_type=data_type,
            squeeze=squeeze,
        )
        self.input_shape = self.input_df.shape

    def _input_loader(
        self,
        header_location: int,
        column_names: List[str],
        data_type: type,
        squeeze: bool = False,
    ) -> Union[pd.Series, pd.DataFrame]:
        return pd.read_csv(
            self.input,
            header=header_location,
            names=column_names,
            dtype=data_type,
            squeeze=squeeze,
        )
