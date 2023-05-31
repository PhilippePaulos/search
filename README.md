# Restaurant Search Tool

## Overview

This Python project efficiently calculates and displays distances from a given point to nearby restaurants using a KDTree.
The main functionality is provided by the [`SearchProcess`](https://github.com/PhilippePaulos/search/blob/main/search/processes/search_process.py) class, which handles data loading, preprocessing, and distance calculations.

## Performance Choices

In order to optimize performance and enhance the speed of distance calculations, a few strategic choices have been made:

- **KDTree**: Utilizing a KDTree for indexing significantly improves the performance. The KDTree structure allows for efficient spatial queries and accelerates the calculation of distances between coordinates.

- **Data Preprocessing**: The restaurant data, which is stored in a geojson file, is preprocessed to optimize loading and handling within the tool. This preprocessing step ensures that the data is in a suitable format for the KDTree and streamlines subsequent operations.

- **Loading & Saving of Tree**: To avoid the overhead of rebuilding the KDTree every time, the tree structure is saved to a pickle file after being built. This allows for rapid loading of the pre-constructed tree in subsequent runs, further boosting the tool's performance.


## Potential Enhancements
For real-world applications where restaurant data is dynamic, frequent updates to the preprocessed data and the KDTree would be beneficial. This ensures accuracy and optimal performance of the tool in ever-changing environments.

## Installation

Install Poetry for dependency management, if not already done. Instructions can be found  [here](https://python-poetry.org/docs/#installation).

To set up this project:

1. Clone or download this repository.
2. In the project directory, execute poetry install.

Python 3.6 or higher is required.

## Usage

Once the installation is done, you can use the Restaurant Search Tool from the command line. Make sure you're in the directory containing runner.py and use the following command format:

```bash
poetry run python -m runner latitude=<value> longitude=<value> radius=<value>
```

Replace `<value>` with the appropriate numbers for latitude, longitude, and radius. For example:

```bash
$ poetry run python -m runner latitude=48.8319929 longitude=2.3245488 radius=100
[INFO] 2023-05-30 11:16:36,862 - logs - logs.py : Starting process()
[INFO] 2023-05-30 11:16:36,862 - search_process - search_process.py : Loading precomputed data ...
[INFO] 2023-05-30 11:16:36,862 - logs - logs.py : Starting _load_precomputed_data()
[INFO] 2023-05-30 11:16:36,886 - logs - logs.py : Process _load_precomputed_data() done. Execution time: 24.35 milliseconds
[INFO] 2023-05-30 11:16:36,886 - search_process - search_process.py : Computing distances ...
[INFO] 2023-05-30 11:16:36,886 - logs - logs.py : Starting compute_distances()
[INFO] 2023-05-30 11:16:36,888 - logs - logs.py : Process compute_distances() done. Execution time: 1.00 milliseconds
[INFO] 2023-05-30 11:16:36,890 - logs - logs.py : Process process() done. Execution time: 28.32 milliseconds
name: Le Severo, latitude: 48.8319929, longitude: 2.3245488, type: Point, distance: 0.0
name: Sushi House, latitude: 48.8319258, longitude: 2.3247528, type: Point, distance: 16.69
name: Mikopüy, latitude: 48.8318918, longitude: 2.3247313, type: Point, distance: 17.46
name: Chez Toni, latitude: 48.8321391, longitude: 2.3246523, type: Point, distance: 17.94
name: Au P'tit Zinc, latitude: 48.8323129, longitude: 2.3247495, type: Point, distance: 38.5
name: Félicie, latitude: 48.832418, longitude: 2.3247172, type: Point, distance: 48.85
name: Le Saut du Crapaud, latitude: 48.8315833, longitude: 2.3242762, type: Point, distance: 49.72
name: Lida, latitude: 48.8313102, longitude: 2.324098, type: Point, distance: 82.77
```
