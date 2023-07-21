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

    # get scenario state
def call_scenarios():
    scenario = st.session_state["scenario"]
    if scenario == "Custom":
        return
    update_slider(keys, values_dict[scenario])

def change_meatfree():
    value_meatfree = st.session_state["d2"]
    land_factor = 65
    if "Egg" in st.session_state["d3"]:
        land_factor += 5
    if "Dairy" in st.session_state["d3"]:
        land_factor += 30

    new_value_forestry = int(value_meatfree*(land_factor)/100)

    st.session_state["l3"] = new_value_forestry
    value_silvo = st.session_state["l4"]

    if (value_silvo + new_value_forestry) > 100:
        st.session_state["l4"] = 100 - new_value_forestry


def change_land():
    value_forestry = st.session_state["l3"]
    value_silvo = st.session_state["l4"]
    st.session_state["d2"] = value_forestry
    st.session_state["d3"] = ["Egg", "Dairy"]

    if (value_silvo + value_forestry) > 100:
        st.session_state["l4"] = 100 - value_forestry


def change_silvo():
    value_forestry = st.session_state["l3"]
    value_silvo = st.session_state["l4"]

    if (value_silvo + value_forestry) > 100:
        st.session_state["l3"] = 100 - value_silvo

    change_land()

        