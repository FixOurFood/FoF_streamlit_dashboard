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
    "ruminant": 0,
    "dairy": 0,
    "pig_poultry_eggs": 0,
    "fruit_veg": 0,
    "cereals": 0,
    "waste": 0,
    "labmeat": 0,
    "dairy_alt":0,

    # Land use sliders and widgets
    "land_bar": 0,
    "pasture_sparing": 0,
    "land_beccs": 0,
    "arable_sparing": 0,
    "foresting_spared": 0,

    # Technology and innovation sliders and widgets
    "innovation_bar": 0,
    "waste_BECCS": 0,
    "overseas_BECCS": 0,
    "DACCS": 0,

    # Livestock farming sliders and widgets
    "livestock_bar": 0,
    "silvopasture": 0,
    "methane_inhibitor": 0,
    "manure_management": 0,
    "animal_breeding": 0,
    "soil_carbon_management": 0,
    "fossil_livestock": 0,

    # Arable farming sliders and widgets
    "arable_bar": 0,
    "agroforestry": 0,
    "tillage": 0,
    "fossil_arable": 0,

    # Advanced settings sliders and widgets
    "labmeat_slider": 25,
    "rda_slider": 2250,
    "timescale_slider": 20,
    "max_ghg_animal": 30,
    "max_ghg_plant": 30,
    "bdleaf_conif_ratio": 75,
    "bdleaf_seq_ha_yr": 3.5,
    "conif_seq_ha_yr": 6.5,
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


def help_str(help, sidebar_key, row_index, heading_key=None):
    doc_str = "https://docs.google.com/document/d/1A2J4BYIuXMgrj9tuLtIon8oJTuR1puK91bbUYCI8kHY/edit#heading=h."
    help_string = help[sidebar_key][row_index]

    if heading_key is not None:
        help_string = f"[{help_string}]({doc_str}{heading_key})"

    return help_string
