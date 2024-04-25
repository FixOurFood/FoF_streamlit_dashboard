# FAIR wrapper, needed for caching
import streamlit as st
import fair
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

def reset_all_sliders():
    update_slider(keys=['d1', 'd2', 'd3', 'd4', 'd5'], values=[0, 0, [], 0, 0])
    update_slider(keys=['l1', 'l2', 'l3', 'l4', 'l5'], values=[0, 0, 0, 0, 0])
    update_slider(keys=['i1', 'i2', 'i3', 'i4', 'i5', 'i6'], values=[0, 0, 0, 0, 0, 0])


# return a logistic function between the input ranges with given k, x0
def logistic(n_scale, xmin=0, xmax=81):
    k = [2**(1-n) for n in range(5)]
    k[0] = 100
    x0 = 10*(-0.01+np.arange(5))
    return 1 / (1 + np.exp(-k[n_scale]*(np.arange(xmax-xmin) - x0[n_scale])))

# function to return the coordinate index of the maximum value along a dimension
def map_max(map, dim):

    length_dim = len(map[dim].values)
    map_fixed = map.assign_coords({dim:np.arange(length_dim)})

    return map_fixed.idxmax(dim=dim, skipna=True)

def item_name_code(arr):
    if np.array_equal([2949],arr):
        return "Egg"
    elif np.array_equal([2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769], arr):
        return "Fish & Seafood"
    elif np.array_equal([2740, 2743, 2948], arr):
        return "Dairy"
    elif np.array_equal([2734], arr):
        return "Poultry"
    elif np.array_equal([2733], arr):
        return "Pigmeat"