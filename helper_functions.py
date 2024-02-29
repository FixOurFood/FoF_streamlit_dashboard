# FAIR wrapper, needed for caching
import streamlit as st
import fair
import pandas as pd
from agrifoodpy.food.food_supply import scale_element
import numpy as np

# Helper Functions

@st.cache_data
def FAIR_run(emissions_gtco2e):
    C, F, T = fair.forward.fair_scm(emissions_gtco2e, useMultigas=False)
    return C, F, T

# Updates the value of the sliders by setting the session state
def update_slider(keys, values):
    for key, value in zip(keys, values):
        st.session_state[key] = value

# # Initialize session state with sliders in initial positions to recover later
# for key in ["d1", "d2", "d4", "d5", "l1", "l2", "l3", "l5", "l5", "i1", "i2", "i3", "i4", "i5"]:
#     if key not in st.session_state:
#         st.session_state[key] = 0

# if 'd3' not in st.session_state:
#         st.session_state['d3'] = []

default_widget_values = {
    # Consumer demand sliders and widgets
    "d1": 0,
    "d2": 0,
    "d3": [],
    "d4": 0,
    "d5": 0,
    "d6": [],

    # Land use sliders and widgets
    "l1": 0,
    "l2": 0,
    "l3": 0,
    "l4": 0,
    "l5": 0,

    # Technology and innovation sliders and widgets
    "i1": 0,
    "i2": 0,
    "i3": 0,
    "i4": 0,
    "i5": 0,
    "i6": 0,

    # Advanced settings sliders and widgets
    "labmeat_slider": 25,
    "a2": 2250,
    "a3": 2,
    "a4": 12.47,
    "max_ghg_animal": 30,
    "max_ghg_plant": 30,
    "a7": "Energy",    
}

def reset_all_sliders():
    for key in default_widget_values.keys():
        update_slider(keys=[key], values=[default_widget_values[key]])

# return a logistic function between the input ranges with given k, x0
def logistic(n_scale, xmin=0, xmax=81):
    k = [2**(1-n) for n in range(5)]
    k[0] = 100
    x0 = 10*(-0.01+np.arange(5))
    return 1 / (1 + np.exp(-k[n_scale]*(np.arange(xmax-xmin) - x0[n_scale])))

# Function to scale an element and then add the difference to another element
def scale_add(food, element_in, element_out, scale, items=None):

    out = scale_element(food, element_in, scale, items)
    dif = food[element_in].fillna(0) - out[element_in].fillna(0)
    out[element_out] += dif

    return out

# function to return the coordinate index of the maximum value along a dimension
def map_max(map, dim):

    length_dim = len(map[dim].values)
    map_fixed = map.assign_coords({dim:np.arange(length_dim)})

    return map_fixed.idxmax(dim=dim, skipna=True)