import streamlit as st
from helper_functions import update_slider

keys = ["d1", "d5", "i1", "i2", "i3","i4","l3","l4","l5"]

scenarios_dict={
    "Business as Usual" : [0,0,0,0,0,0,0,0,0],
    "Green Alliance - Balance Food, Nature and Climate priorities":[45,50,27,0,0,5,33,60,60],
    "Green Alliance - Business as Usual + Engineered gas removal":[0,0,33,67,0,5,0,0,0],
    "Green Alliance - Agroecological farming on all land":[50,0,33,40,0,5,0,100,100],
    "Green Alliance - Self-sufficiency":[60,10,33,48,12,5,0,0,0],
    "Green Alliance - Avoid engineered greenhouse gas removal":[70,20,0,0,0,0,50,33,33],
}

def call_scenarios():
    # get scenario state
    scenario = st.session_state["scenario"]
    update_slider(keys, scenarios_dict[scenario])