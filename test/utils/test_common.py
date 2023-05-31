import pandas as pd
import pytest

from search.utils.common import display_dataframe


@pytest.fixture
def dataframe():
    return pd.DataFrame({'col1': ['a', 'b'], 'col2': [1, 2], 'col3': [3.1, 4.2]})


def test_display_dataframe(dataframe, capsys):
    expected_output = "col1: a, col2: 1, col3: 3.1\n" \
                      "col1: b, col2: 2, col3: 4.2\n"
    display_dataframe(dataframe)
    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_display_dataframe_selected_columns(dataframe, capsys):
    expected_output = "col1: a, col2: 1\n" \
                      "col1: b, col2: 2\n"
    display_dataframe(dataframe, ['col1', 'col2'])
    captured = capsys.readouterr()
    assert captured.out == expected_output
