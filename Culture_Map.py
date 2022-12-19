import random

import streamlit as st

from culture_map import country_data
from culture_map import distance_calculations
from culture_map import visualisation

DEFAULT_COUNTRY_NUMBER = 10

all_countries = country_data.get_country_dict()
all_countries_names = list(all_countries.keys())
if "default_countries" not in st.session_state:
    st.session_state["default_countries"] = random.sample(all_countries_names, DEFAULT_COUNTRY_NUMBER)

st.title("🌎 Culture map app")

st.header("The 6-D model of national culture 🗺️")

st.markdown(open('intro.md').read())

selected_countries_names = st.multiselect(
    'Choose countries you want to compare:',
    all_countries_names,
    st.session_state["default_countries"])

selected_countries = [country for country in all_countries.values() if country.title in selected_countries_names]

def country_group_callback():
    chosen_group = [
        group_name for group_name, selected in st.session_state.items() if
        selected and group_name in country_data.COUNTRY_GROUPS][0]
    countries = country_data.GROUPS_TO_COUNTRIES[chosen_group]
    st.session_state["default_countries"] = countries


st.write("Or choose from predefined country group:")
columns = st.columns(len(country_data.COUNTRY_GROUPS))
for idx, column in enumerate(columns):
    with column:
        group = country_data.COUNTRY_GROUPS[idx]
        st.button(group, key=group, on_click=country_group_callback)

raw_data = st.expander("See raw data about selected countries")

dimensions = distance_calculations.compute_dimensions(selected_countries)
raw_data.write('Dimensions:')
raw_data.write(dimensions)

dimension_tabs = st.tabs([dim.upper() for dim in distance_calculations.HOFSTEDE_DIMENSIONS[:-1]])
for idx, tab in enumerate(dimension_tabs):
    with tab:
        dimension = distance_calculations.HOFSTEDE_DIMENSIONS[idx]
        st.header(dimension.upper())
        choropleth = visualisation.generate_choropleth(dimensions, dimension)
        st.plotly_chart(choropleth)

radar = visualisation.generate_radar_plot(dimensions)
st.write("Let's see each selected country on a radar plot to explore each of the 6 dimensions:")
st.pyplot(radar)

st.write("Now let's create a single number as a distance between countries:")
distance_metric = st.selectbox('What distance metric would you like to use?',
                               list(distance_calculations.AVAILABLE_DISTANCES.keys()))

raw_calculations = st.expander("See raw calculations")

distances, max_distance = distance_calculations.compute_distances(selected_countries, distance_metric)
raw_calculations.write('Country distances before normalisation:')
raw_calculations.write(distances)

normalised_distances = distance_calculations.normalise_distance_matrix(distances, max_distance)
raw_calculations.write('Country distances after normalisation:')
raw_calculations.write(normalised_distances)

col1, col2 = st.columns(2)
with col1:
    show_clusters = st.checkbox('Show clusters', value=True)
with col2:
    apply_normalisation = st.checkbox('Apply normalisation', value=True)

heatmap = visualisation.generate_heatmap(normalised_distances if apply_normalisation else distances, show_clusters)
st.pyplot(heatmap)

st.write("And now let's apply dimensionality reduction and plot countries in 2D by their cultural distance")
algo = st.selectbox('Select dimensionality reduction algorithm', list(distance_calculations.AVAILABLE_DECOMPOSITION.keys()))
coords = distance_calculations.generate_2d_coords(dimensions, algo)

raw_coordinates = st.expander("See raw data")
raw_coordinates.write(coords)

scatterplot = visualisation.generate_scatterplot(coords)
st.bokeh_chart(scatterplot)
