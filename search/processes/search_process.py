import json
import os
import pickle
from typing import Tuple

import numpy as np
import pandas as pd
from haversine import Unit, haversine_vector
from scipy.spatial import KDTree

from search.logging.logs import logging_setup, log_process_time
from search.utils.common import display_dataframe
from search.utils.fs import get_resources_file


class SearchProcess:
    def __init__(self, latitude: float, longitude: float, radius: int,
                 original_file_path: str = get_resources_file("restaurants_paris.geojson"),
                 cleansed_data_path: str = get_resources_file("restaurants_paris_cleansed.json"),
                 kdtree_path: str = get_resources_file("kdtree.pkl")) -> None:
        super().__init__()
        self.log = logging_setup()
        self.centroid_array = np.array([latitude, longitude])
        self.radius = radius
        self.original_file_path = original_file_path
        self.cleansed_data_path = cleansed_data_path
        self.kdtree_path = kdtree_path

    @log_process_time
    def process(self) -> None:
        """
        Orchestrates the data loading, preprocessing and calculation of restaurant distances.

        This function executes the following operations:
        1. Checks if preprocessed data (cleaned restaurant data and KDTree) is available. If so, this data is loaded.
        2. If preprocessed data is not available, it loads the raw data, cleanses it, builds a KDTree, and saves these for future use.
        3. Computes the distances from the provided centroid to the restaurants using the KDTree and displays the result.

        Logs the start of each major operation for performance profiling.
        """

        # Load or create precomputed data
        if os.path.exists(self.cleansed_data_path) and os.path.exists(self.kdtree_path):
            self.log.info("Loading precomputed data ...")
            restaurants_df, kdtree = self._load_precomputed_data(self.cleansed_data_path, self.kdtree_path)
        else:
            restaurants_df, kdtree,  = self._prepare_data()

        self.log.info("Computing distances ...")
        # Compute and display distances using KDTree
        display_dataframe(self.compute_distances(restaurants_df, kdtree))

    @log_process_time
    def _prepare_data(self) -> Tuple[pd.DataFrame, KDTree]:
        """
        Prepares data for processing.

        This function performs the following steps:
        1. Loads raw data from the original file path.
        2. Cleanses the loaded data (e.g., filters for "Point" geometry types).
        3. Saves the cleansed data as a JSON file.
        4. Constructs a KDTree from the cleansed data and saves it to a specified path.

        :return: The constructed KDTree and the cleansed data as a pandas DataFrame.
        :rtype: Tuple[KDTree, pd.DataFrame]
        """
        self.log.info("Precomputed data not found. Loading original data...")
        raw_data = self._load_raw_data(self.original_file_path)
        restaurants_df = self._cleanse_data(raw_data)
        self._save_data(restaurants_df, self.cleansed_data_path)
        kdtree = self._save_tree(restaurants_df, self.kdtree_path)
        return restaurants_df, kdtree

    @log_process_time
    def _load_raw_data(self, file_path: str) -> pd.DataFrame:
        """
        Loads restaurant data from a geojson file into a pandas DataFrame.

        :param file_path: Path to the geojson file.
        :type file_path: str
        :return: The loaded raw data as a pandas DataFrame.
        :rtype: pd.DataFrame
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)["features"]
        # coordinates are in opposite order
        data_list = [
            {
                "name": d["properties"]["name"],
                "latitude": d["geometry"]["coordinates"][1],
                "longitude": d["geometry"]["coordinates"][0],
                "type": d["geometry"]["type"]
            }
            for d in data
        ]
        return pd.DataFrame(data_list)

    def _cleanse_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleanses restaurant data, filtering for "Point" geometry types.

        :param df: DataFrame to cleanse.
        :type df: pd.DataFrame
        :return: The cleansed data as a pandas DataFrame.
        :rtype: pd.DataFrame
        """
        return df[df["type"] == "Point"].copy()

    def _save_data(self, df: pd.DataFrame, path: str) -> None:
        """
        Saves a DataFrame to a JSON file at the specified path.

        :param df: DataFrame to save.
        :type df: pd.DataFrame
        :param path: Path to the JSON file where the DataFrame will be saved.
        :type path: str
        """
        df.to_json(path, orient="records")

    @log_process_time
    def _save_tree(self, df: pd.DataFrame, path: str) -> KDTree:
        """
        Constructs a KDTree from the latitude and longitude columns of the provided DataFrame. The resulting KDTree
        is saved to a file at the provided path.

        :param df: DataFrame containing "latitude" and "longitude" columns.
        :type df: pd.DataFrame
        :param path: Path at which to save the KDTree.
        :type path: str
        :return: The constructed KDTree.
        :rtype: KDTree
        """
        coordinates = df[["latitude", "longitude"]].values
        kdtree = KDTree(coordinates)
        with open(path, "wb") as f:
            pickle.dump(kdtree, f)
        return kdtree

    @log_process_time
    def _load_precomputed_data(self, cleansed_path, tree_path) -> Tuple[pd.DataFrame, KDTree]:
        """
        Loads cleansed restaurant data and a pre-built KDTree from given file paths.

        :param cleansed_path: Path to cleansed restaurant data JSON file.
        :type cleansed_path: str
        :param tree_path: Path to pre-built KDTree pickle file.
        :type tree_path: str
        :return: Loaded data as a DataFrame and the KDTree.
        :rtype: Tuple[pd.DataFrame, KDTree]
        """
        restaurants_df = pd.read_json(cleansed_path)

        with open(tree_path, "rb") as f:
            kdtree = pickle.load(f)
        return restaurants_df, kdtree

    @log_process_time
    def compute_distances(self, df: pd.DataFrame, kdtree: KDTree) -> pd.DataFrame:
        """
        Compute distances using a KDTree data structure and filter out restaurants based on the search radius.

        :param df: DataFrame containing latitude and longitude columns.
        :type df: pd.DataFrame
        :param kdtree: KDTree data structure for nearest-neighbor queries.
        :type kdtree: KDTree

        :return: DataFrame with added "distance" column, filtered based on the given radius.
        :rtype: pd.DataFrame
        """
        point = np.array([self.centroid_array[0], self.centroid_array[1]])

        # Convert the radius from meters to degrees and add buffer space
        radius_in_degrees = self.radius / 110574 + 0.01

        # Use KDTree to find points within radius
        indices = kdtree.query_ball_point(point, radius_in_degrees)
        restaurants_near_centroid = df.iloc[indices].copy()

        coordinates = restaurants_near_centroid[["latitude", "longitude"]].values
        distances = haversine_vector(self.centroid_array, coordinates,
                                     unit=Unit.METERS,
                                     comb=True)

        # Round distances to 2 decimal places
        distances = np.round(distances, 2)

        # Filter restaurants based on actual search radius
        mask = distances <= self.radius
        return restaurants_near_centroid[mask].assign(distance=distances[mask])
