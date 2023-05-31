import json
import os
import pickle
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from scipy.spatial import KDTree

from search.processes.search_process import SearchProcess


@pytest.fixture
def search_process():
    return SearchProcess(48.8566, 2.3522, 1000)


@pytest.mark.parametrize("geojson_data, df", [
    (
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [2.3522, 48.8566]
                        },
                        "properties": {
                            "name": "Restaurant1",
                        }
                    },
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [2.3387, 48.8582]
                        },
                        "properties": {
                            "name": "Restaurant2",
                        }
                    }
                ]
            },
            pd.DataFrame({
                "name": ["Restaurant1", "Restaurant2"],
                "latitude": [48.8566, 48.8582],
                "longitude": [2.3522, 2.3387],
                "type": ["Point", "Point"]
            }),
    ),
])
def test__load_raw_data(search_process, geojson_data, df, tmpdir):
    # Write geojson data to a temporary file
    file_path = tmpdir.join("test.geojson")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f)

    # Load data from the file using the function under test
    loaded_data = search_process._load_raw_data(file_path)

    # Check that loaded data matches the expected DataFrame
    pd.testing.assert_frame_equal(df, loaded_data)


@pytest.mark.parametrize("raw_data", [
    pd.DataFrame({
        "name": ["Restaurant1", "Restaurant2", "Restaurant3"],
        "longitude": [2.35, 2.36, 2.35],
        "latitude": [48.85, 48.86, 48.85],
        "type": ["Point", "Polygon", "Point"]
    }),
])
def test__cleanse_data(search_process, raw_data):
    cleansed_data = search_process._cleanse_data(raw_data)

    # Assert that the cleansed data only contains "Point" types
    assert cleansed_data["type"].eq("Point").all()
    # Assert that the cleansed data isn"t empty
    assert not cleansed_data.empty


@pytest.mark.parametrize("df, file_name", [
    (pd.DataFrame({
        "name": ["Restaurant1", "Restaurant2", "Restaurant3"],
        "longitude": [2.35, 2.36, 2.35],
        "latitude": [48.85, 48.86, 48.85],
        "type": ["Point", "Point", "Point"]
    }), "test.json"),
])
def test__save_data(search_process, df, file_name, tmpdir):
    target_path = tmpdir.join(file_name)
    search_process._save_data(df, target_path)

    # Assert that the file exists
    assert os.path.exists(target_path)

    # Read the file back and compare it with the original DataFrame
    df_read_back = pd.read_json(target_path, orient="records")
    assert df.equals(df_read_back)


@pytest.mark.parametrize("df, file_name", [
    (pd.DataFrame({
        "name": ["Restaurant1", "Restaurant2", "Restaurant3"],
        "longitude": [2.35, 2.36, 2.35],
        "latitude": [48.85, 48.86, 48.85],
        "type": ["Point", "Point", "Point"]
    }), "test.pkl"),
])
def test__save_tree(search_process, df, file_name, tmpdir):
    target_path = tmpdir.join(file_name)
    result_tree = search_process._save_tree(df, target_path)

    # Assert that the file exists
    assert os.path.exists(target_path)

    # Read the KDTree back and compare it with the original
    with open(target_path, "rb") as f:
        loaded_tree = pickle.load(f)

    assert isinstance(loaded_tree, KDTree)
    # Here we check that the data of both trees are identical
    assert np.array_equal(loaded_tree.data, result_tree.data)


@pytest.mark.parametrize("df, tree, df_file_name, tree_file_name", [
    (
            pd.DataFrame({
                "name": ["Restaurant1", "Restaurant2", "Restaurant3"],
                "longitude": [2.35, 2.36, 2.35],
                "latitude": [48.85, 48.86, 48.85],
                "type": ["Point", "Point", "Point"]
            }),
            KDTree(np.array([[48.85, 2.35], [48.86, 2.36], [48.85, 2.35]])),
            "test.json",
            "test.pkl"
    ),
])
def test__load_precomputed_data(search_process, df, tree, df_file_name, tree_file_name, tmpdir):
    df_file_path = tmpdir.join(df_file_name)
    tree_file_path = tmpdir.join(tree_file_name)

    # Save DataFrame and KDTree to files
    df.to_json(df_file_path, orient="records")
    with open(tree_file_path, "wb") as f:
        pickle.dump(tree, f)

    # Load DataFrame and KDTree using the function under test
    loaded_df, loaded_tree = search_process._load_precomputed_data(df_file_path, tree_file_path)

    # Check that loaded DataFrame matches the original
    assert df.equals(loaded_df)

    # Check that loaded KDTree matches the original
    assert np.array_equal(tree.data, loaded_tree.data)


@pytest.mark.parametrize("df, kdtree, centroid, radius, expected", [
    (
        pd.DataFrame({
            "name": ["Restaurant1", "Restaurant2", "Restaurant3"],
            "latitude": [48.85, 48.86, 548.85],
            "longitude": [2.35, 2.36, 2.35],
            "type": ["Point", "Point", "Point"]
        }),
        KDTree(np.array([[48.85, 2.35], [48.86, 2.36], [548.85, 2.35]])),  # Use coordinates as (latitude, longitude)
        np.array([48.8566, 2.3522]),  # Centroid as (latitude, longitude)
        5000,  # radius
        2  # expected number of restaurants within radius
    ),
])
def test_compute_distances(search_process, df, kdtree, centroid, radius, expected):
    search_process.centroid_array = centroid
    search_process.radius = radius
    result = search_process.compute_distances(df, kdtree)
    assert len(result) == expected
    assert "distance" in result.columns


# Parameters for process testing
params = [
    # data_exists, latitude, longitude, radius
    (True, 48.8566, 2.3522, 500),  # Case when preprocessed data exists
    (False, 48.8566, 2.3522, 500),  # Case when preprocessed data doesn't exist
]


@pytest.mark.parametrize("data_exists,latitude,longitude,radius", params)
def test__process(data_exists, latitude, longitude, radius):
    mock_computed_dataframe = pd.DataFrame({
        "name": ["Restaurant 1", "Restaurant 2"],
        "latitude": [48.8566, 48.8560],
        "longitude": [2.3522, 2.3520],
        "distance": [30, 31]
    })
    with patch("os.path.exists", return_value=data_exists) as mock_exists, \
            patch.object(SearchProcess, "_load_precomputed_data",
                         return_value=("mock_dataframe", "mock_kdtree")) as mock_load, \
            patch.object(SearchProcess, "_prepare_data",
                         return_value=("mock_dataframe", "mock_kdtree")) as mock_prepare, \
            patch.object(SearchProcess, "compute_distances", return_value=mock_computed_dataframe) as mock_compute, \
            patch("search.processes.search_process.display_dataframe") as mock_display:

        search_process = SearchProcess(latitude, longitude, radius)

        search_process.process()

        mock_exists.assert_called()
        if data_exists:
            mock_load.assert_called_once()
            mock_prepare.assert_not_called()
        else:
            mock_load.assert_not_called()
            mock_prepare.assert_called_once()

        mock_compute.assert_called_once_with("mock_dataframe", "mock_kdtree")
        mock_display.assert_called()
