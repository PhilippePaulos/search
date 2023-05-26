import json
import os
import pickle
from typing import Union, List

import numpy as np
import pandas as pd
from haversine import Unit, haversine_vector
from scipy.spatial import KDTree

from search.logging.logs import logging_setup, log_process_time
from search.utils.common import display_dataframe
from search.utils.fs import get_resources_file


class SearchProcess:
    def __init__(self, latitude: float, longitude: float, radius: int) -> None:
        super().__init__()
        self.log = logging_setup()
        self.centroid_array = np.array([latitude, longitude])
        self.radius = radius

    @log_process_time
    def process(self) -> None:
        """
        Main method that handles data loading, preprocessing and calculation of restaurant distances.

        This method performs the following steps:
        1. Load cleaned restaurant data from a JSON file if it exists. If not, load the original data, cleanse it, and save it back as JSON.
        2. Load a pre-built KDTree from a pickle file if it exists. If not, build the KDTree from the loaded data and save it.
        3. Compute and display the distances from the centroid to the restaurants using the KDTree.
        """

        cleansed_path = get_resources_file('restaurants_paris_cleansed.json')
        tree_path = get_resources_file('kdtree.pkl')

        # Load or create cleansed data
        if os.path.exists(cleansed_path):
            restaurants_df = self._load_data_cleaned(cleansed_path, load_as_df=True)
        else:
            restaurants_df = self._load_data(cleansed_path, load_as_df=True)
            restaurants_df.to_json(cleansed_path, orient='records')

        # Load or create KDTree
        if os.path.exists(tree_path):
            kdtree = self._load_tree()
        else:
            kdtree = self._save_tree(restaurants_df, tree_path)

        # Compute and display distances using KDTree
        display_dataframe(self.compute_distances_tree(restaurants_df, kdtree))

    @log_process_time
    def _load_data(self, file_path: str, load_as_df=False) -> Union[pd.DataFrame, List[dict]]:
        """
        Load restaurant data from a geojson file.

        :param file_path: Path to the geojson file.
        :type file_path: str
        :param load_as_df: Determines if data is returned as pandas DataFrame. Default is False.
        :type load_as_df: bool
        :return: Restaurant data as DataFrame or list of dictionaries.
        :rtype: Union[pd.DataFrame, List[dict]]
        """
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)["features"]
        data_list = [
            {
                "name": d["properties"]["name"],
                "longitude": d["geometry"]["coordinates"][1],
                "latitude": d["geometry"]["coordinates"][0],
            }
            for d in data
            if d["geometry"]["type"] == "Point"
        ]
        if load_as_df:
            return pd.DataFrame(data_list)
        return data_list

    @log_process_time
    def _save_tree(self, df: pd.DataFrame, path: str) -> KDTree:
        """
        Save a KDTree built from the latitude and longitude columns of the DataFrame.

        :param df: DataFrame containing latitude and longitude columns.
        :type df: pd.DataFrame
        :param path: File path to save the KDTree.
        :type path: str
        :return: The KDTree object.
        :rtype: KDTree
        """
        coordinates = df[['latitude', 'longitude']].values
        kdtree = KDTree(coordinates)
        with open(path, 'wb') as f:
            pickle.dump(kdtree, f)
        return kdtree

    @log_process_time
    def _load_tree(self) -> KDTree:
        """
        Load a KDTree from a saved file.

        :return: The loaded KDTree object.
        :rtype: KDTree
        """
        with open('resources/kdtree.pkl', 'rb') as f:
            kdtree = pickle.load(f)
        return kdtree

    @log_process_time
    def _load_data_cleaned(self, file_path, load_as_df=False) -> Union[pd.DataFrame, List[dict]]:
        """
        Load cleaned data from a JSON file.

        :param file_path: Path to the JSON file to be loaded.
        :type file_path: str
        :param load_as_df: If True, loads data as a DataFrame. If False, returns a list of dictionaries. Default is False.
        :type load_as_df: bool
        :return: Loaded data in the format of a DataFrame or a list of dictionaries.
        :rtype: Union[pd.DataFrame, List[dict]]
        """
        df = pd.read_json(file_path)
        if load_as_df:
            return df
        return df.to_dict('records')

    @log_process_time
    def compute_distances(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute the haversine distances between the centroid and the coordinates in the DataFrame.

        :param df: DataFrame containing latitude and longitude columns.
        :type df: pd.DataFrame

        :return: DataFrame with added 'distance' column, filtered based on the given radius.
        :rtype: pd.DataFrame
        """
        # Extract coordinates and compute haversine distances
        coordinates = df[['longitude', 'latitude']].values
        distances = haversine_vector(self.centroid_array, coordinates,
                                     unit=Unit.METERS,
                                     comb=True)

        # Round distances to 2 decimal places and add to DataFrame
        df = df.assign(distance=np.round(distances, 2))

        # Filter rows where distance is less than or equal to radius
        df = df.loc[df['distance'] <= self.radius]
        return df

    @log_process_time
    def compute_distances_tree(self, df: pd.DataFrame, kdtree: KDTree) -> pd.DataFrame:
        """
        Compute distances using a KDTree data structure and filter out restaurants based on the search radius.

        :param df: DataFrame containing latitude and longitude columns.
        :type df: pd.DataFrame
        :param kdtree: KDTree data structure for nearest-neighbor queries.
        :type kdtree: KDTree

        :return: DataFrame with added 'distance' column, filtered based on the given radius.
        :rtype: pd.DataFrame
        """
        point = np.array([self.centroid_array[1], self.centroid_array[0]])

        # Convert the radius from meters to degrees and add buffer space
        radius_in_degrees = self.radius / 110574 + 0.01

        # Use KDTree to find points within radius
        indices = kdtree.query_ball_point(point, radius_in_degrees)
        restaurants_near_centroid = df.iloc[indices].copy()

        coordinates = restaurants_near_centroid[['longitude', 'latitude']].values
        distances = haversine_vector(self.centroid_array, coordinates,
                                     unit=Unit.METERS,
                                     comb=True)

        # Round distances to 2 decimal places
        distances = np.round(distances, 2)

        # Filter restaurants based on actual search radius
        mask = distances <= self.radius
        return restaurants_near_centroid[mask].assign(distance=distances[mask])
