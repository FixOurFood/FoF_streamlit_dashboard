# FAIR wrapper, needed for caching
import streamlit as st
import numpy as np

# Helper Functions

# Updates the value of the sliders by setting the session state
def update_slider(keys, values):
    if np.isscalar(values):
        for key in keys:
            st.session_state[key] = values
    else:
        for key, value in zip(keys, values):
            st.session_state[key] = value

default_widget_values = {
    # Consumer demand sliders and widgets
    "consumer_bar": 0,
    "d1": 0,
    "d2": 0,
    "d3": 0,
    "d4": 0,
    "d5": 0,
    "d6": 0,
    "d7": 0,

    # Land use sliders and widgets
    "land_bar": 0,
    "l1": 0,
    "l2": 0,
    "l3": 0,
    "l4": 0,
    "l5": 0,

    # Technology and innovation sliders and widgets
    "innovation_bar": 0,
    "i1": 0,
    "i2": 0,
    "i3": 0,
    "i4": 0,
    "i5": 0,
    "i6": 0,

    # Livestock farming sliders and widgets
    "livestock_bar": 0,
    "lf1": 0,
    "lf2": 0,
    "lf3": 0,
    "lf4": 0,
    "lf5": 0,

    # Arable farming sliders and widgets
    "arable_bar": 0,
    "a1": 0,
    "a2": 0,

    # Advanced settings sliders and widgets
    "labmeat_slider": 25,
    "rda_slider": 2250,
    "timescale_slider": 20,
    "max_ghg_animal": 30,
    "max_ghg_plant": 30,
    "bdleaf_conif_ratio": 50,
    "bdleaf_seq_ha_yr": 12.5,
    "conif_seq_ha_yr": 23.5,
    "nutrient_constant": "kCal/cap/day",
    "domestic_use_source": "production"
}

def reset_sliders(keys=None):
    if keys is None:
        for key in default_widget_values.keys():
            update_slider(keys=[key], values=[default_widget_values[key]])
    else:
        keys = np.hstack(keys)
        update_slider(keys=keys, values=[default_widget_values[key] for key in keys])

# function to return the coordinate index of the maximum value along a dimension
def map_max(map, dim):

    length_dim = len(map[dim].values)
    map_fixed = map.assign_coords({dim:np.arange(length_dim)})

    return map_fixed.idxmax(dim=dim, skipna=True)

def item_name_code(arr):
    if np.array_equal([2949],arr):
        return "Egg"
    elif np.array_equal([2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769], arr):
        return "Fish/Seafood"
    elif np.array_equal([2740, 2743, 2948], arr):
        return "Dairy"
    elif np.array_equal([2734], arr):
        return "Poultry"
    elif np.array_equal([2733], arr):
        return "Pigmeat"
    
def update_progress(bar_values, bar_key):
    session_vals = [st.session_state[val] for val in bar_values]
    st.session_state[bar_key] = 4 * sum(session_vals) / 100 / len(session_vals)

def capitalize_first_character(s):
    if len(s) == 0:
        return s  # Return the empty string if input is empty
    return s[0].upper() + s[1:]