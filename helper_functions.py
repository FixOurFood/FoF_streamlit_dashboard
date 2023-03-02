import streamlit as st
import numpy as np
from agrifoodpy.food.food_supply import scale_food, scale_element

# Helper Functions

# Updates the value of the sliders by settging the session state
def update_slider(keys, values):
    for key, value in zip(keys, values):
        st.session_state[key] = value

# Initialize session state with sliders in initial positions to recover later
for key in ["d1", "d2", "l1", "l2"]:
    if key not in st.session_state:
        st.session_state[key] = 0

if 'd3' not in st.session_state:
        st.session_state['d3'] = []

# return a logistic function between the input ranges with given k, x0
def logistic(k, x0, xmin, xmax):
    return 1 / (1 + np.exp(-k*(np.arange(xmax-xmin) - x0)))

# Function to scale an element and then add the difference to another element
def scale_add(food, element_in, element_out, scale, items=None):

    out = scale_element(food, element_in, scale, items)
    dif = food[element_in].fillna(0) - out[element_in].fillna(0)
    out[element_out] += dif

    return out
