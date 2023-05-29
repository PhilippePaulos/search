# Restaurant Search Tool

## Overview

This Python project efficiently calculates and displays distances from a given point to nearby restaurants using a KDTree.
The main functionality is provided by the `SearchProcess` class, which handles data loading, preprocessing, and distance calculations.

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
poetry run python runner.py latitude=48.8588443 longitude=2.2943506 radius=1000
```