from typing import List

import pandas as pd


def display_dataframe(df: pd.DataFrame, cols_to_show: List[str] = None):
    """
    Displays selected columns of a DataFrame as a string.

    This function iterates over the rows of the DataFrame and for each row
    it formats a string that represents the row with the format 'col1: value, col2: value'.

    :param df: The DataFrame to be displayed.
    :type df: pd.DataFrame
    :param cols_to_show: The list of columns to be displayed.
    :type cols_to_show: List[str]
    """
    # Iterate over the DataFrame rows
    if not cols_to_show:
        cols_to_show = list(df.columns)
    for _, row in df[cols_to_show].iterrows():
        # Format each row's output
        row_str = ', '.join(f'{col}: {row[col]}' for col in cols_to_show)
        print(row_str)
