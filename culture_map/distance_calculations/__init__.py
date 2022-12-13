import typing

import pandas as pd
from scipy.spatial import distance
import streamlit as st

from culture_map.country_data import types

HOFSTEDE_DIMENSIONS = ['pdi', 'idv', 'mas', 'uai', 'lto', 'ind', 'ivr']
AVAILABLE_DISTANCES = {
    "Euclidean": distance.euclidean,
    "Cosine": distance.cosine,
    "Manhattan": distance.cityblock,
    "Correlation": distance.correlation

}
TO_PERCENT = 100.0
SQUARE = 2
PandasDataFrame = typing.TypeVar('pandas.core.frame.DataFrame')


def compute_dimensions(countries: types.Countries) -> PandasDataFrame:
    index = [country.title for country in countries]
    dimensions = {}
    for dimension in HOFSTEDE_DIMENSIONS:
        row = []
        for country in countries:
            row.append(getattr(country, dimension))
        dimensions[dimension] = row
    return pd.DataFrame(dimensions, index=index)


def compute_distance(country_from: types.CountryInfo, country_to: types.CountryInfo, distance_metric: str) -> float:
    from_array = [max(getattr(country_from, dimension, 0), 0) for dimension in HOFSTEDE_DIMENSIONS]
    to_array = [max(getattr(country_to, dimension, 0), 0) for dimension in HOFSTEDE_DIMENSIONS]
    return AVAILABLE_DISTANCES[distance_metric](from_array, to_array)


@st.cache
def compute_distances(countries: types.Countries, distance_metric: str) -> tuple[PandasDataFrame, float]:
    index = [country.title for country in countries]
    distances = {}
    max_distance = 0
    for country_from in countries:
        row = []
        for country_to in countries:
            distance = compute_distance(country_from, country_to, distance_metric)
            max_distance = max(max_distance, distance)
            row.append(distance)
        distances[country_from.title] = row
    return pd.DataFrame(distances, index=index), max_distance


@st.cache
def normalise_distance_matrix(distances: PandasDataFrame, max_distance: float) -> PandasDataFrame:
    return distances.applymap(lambda x: x / max_distance * TO_PERCENT)

