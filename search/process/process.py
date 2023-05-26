import json

import pandas as pd
from haversine import haversine, Unit

from search.logging.logs import logging_setup, log_process_time
from utils.common import display_dataframe
from utils.fs import get_resources_file


class SearchProcess:
    def __init__(self, latitude: float, longitude: float, radius: int) -> None:
        super().__init__()
        self.log = logging_setup()
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius

    @log_process_time
    def process(self) -> None:
        data = self._load_data_cleaned(load_as_df=True)
        result_df = self.compute_distances(data)
        display_dataframe(result_df)

    @log_process_time
    def _load_data(self, load_as_df=False):
        file_path = get_resources_file('restaurants_paris.geojson')
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
    def _load_data_cleaned(self, load_as_df=False):
        file_path = get_resources_file('restaurants_paris_clean.json')
        df = pd.read_json(file_path)
        if load_as_df:
            return df
        return df.to_dict('records')

    @log_process_time
    def compute_distances(self, df: pd.DataFrame):
        centroid = (self.latitude, self.longitude)

        # Compute haversine distances
        df["distance"] = df.apply(lambda row: haversine(centroid, (row["longitude"], row["latitude"]),
                                                        unit=Unit.METERS),
                                  axis=1)

        # Round distances to 2 decimal places
        df["distance"] = df["distance"].round(2)

        # Filter rows where distance is less than or equal to radius
        df = df[df["distance"] <= self.radius]

        return df

