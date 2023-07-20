import streamlit as st
from helper_functions import update_slider

keys = ["d1", "d5", "i1", "i2", "i3","i4","l3","l4","l5"]

values_dict={
    "Balance Food, Nature and Climate priorities":[45,50,27,0,0,5,33,60,60],
    "Business as Usual":[0,0,33,67,0,5,0,0,0],
    "Agroecological farming on all land":[50,0,33,40,0,5,0,100,100],
    "Self-sufficiency":[60,10,33,48,12,5,0,0,0],
    "Avoid engineered greenhouse gas removal":[70,20,0,0,0,0,50,33,33],
}

def call_scenarios():
    # get scenario state
    scenario = st.session_state["scenario"]
    update_slider(keys, values_dict[scenario])