import streamlit as st
from utils.helper_functions import update_slider, reset_sliders

scenarios_dict={
    "Business as Usual":{        
    },
    "Green Alliance - Balance Food, Nature and Climate priorities":{
        "dairy":            45,
        "pig_poultry_eggs": 45,
        "labmeat":          45,
        "waste_BECCS":      27,
        "DACCS":             5,
        "agroforestry":     60,
        "silvopasture":     60,
        # missing forestation: a third of currently farmed land

    },
    "Green Alliance - Business as Usual + Engineered gas removal":{        
        "waste_BECCS":      33,
        "DACCS":             5,
        "overseas_BECCS":   67,

    },
    "Green Alliance - Agroecological farming on all land":{
        "agroforestry":    100,
        "silvopasture":    100,
        "ruminant":          0,
        "dairy":            50,
        "ruminant":         50,
        "pig_poultry_eggs": 50,
        "waste_BECCS":      33,
        "DACCS":             5,
        "overseas_BECCS":   40,

    },
    "Green Alliance - Self-sufficiency":{
        "land_beccs":       12, # This should result in 48 [Mt CO2e / yr] but is giving 12
        "waste_BECCS":      33,
        "DACCS":             5,
        "ruminant":         60,
        "dairy":            60,
        "pig_poultry_eggs": 60,

    },
    "Green Alliance - Avoid engineered greenhouse gas removal":{
        "ruminant":         70,
        "dairy":            70,
        "pig_poultry_eggs": 70,
        "agroforestry":     33, # of 2050 farmed land
        "silvopasture":     33, # of 2050 farmed land
        # missing forestation: half of currently farmed land



    },
}

def call_scenarios():
    # reset all states
    reset_sliders()
    # get scenario state
    scenario = st.session_state["scenario"]
    update_slider(scenarios_dict[scenario].keys(), scenarios_dict[scenario].values())
