import streamlit as st

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import colors, cm

import altair as alt
import numpy as np
import xarray as xr
from millify import millify
import pandas as pd
import copy

from agrifoodpy.food.food import FoodBalanceSheet
from agrifoodpy.land.land import LandDataArray
from pipeline import Pipeline

import custom_widgets as cw
from glossary import *
from altair_plots import *
from helper_functions import *
from scenarios import call_scenarios, scenarios_dict


from datablock_setup import *
from model import *

if "datablock_baseline" not in st.session_state:
    st.session_state["datablock_baseline"] = datablock

# ------------------------
# Help and tooltip strings
# ------------------------
help = pd.read_csv(st.secrets["tooltips_url"], dtype='string')

# GUI
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with st.sidebar:

# ------------------------
#        Sidebar
# ------------------------

    # st.image("images/fof_logo.png")
    st.markdown("# AgriFood Calculator")

    col1, col2 = st.columns([7.5,2.5])
    with col1:
        st.selectbox("Scenario", scenarios_dict.keys(),
                     help=help["sidebar_consumer"][8],
                     on_change=call_scenarios, key="scenario")

    with col2:
        st.button("Reset \n sliders", on_click=reset_all_sliders,
                  key='reset_all')

    # Consumer demand interventions
    with st.expander("**:spaghetti: Consumer demand**", expanded=True):

        # ruminant = cw.label_plus_slider('Reduce ruminant meat consumption', ratio=(6,4),
        ruminant = st.slider('Reduce ruminant meat consumption',
                                        min_value=0, max_value=100, step=25,
                                        key="d1", help=help["sidebar_consumer"][1])
        
        # meatfree = cw.label_plus_slider('Number of meat free days a week', ratio=(6,4),
        meatfree = st.slider('Number of meat free days a week',
                                        min_value=0, max_value=7, step=1,
                                        key="d2", help=help["sidebar_consumer"][2])

        meatfree_extra_items = cw.label_plus_multiselect('Also exclude from meat free days',
                                        options=[[2949],
                                                 [2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769],
                                                 [2740, 2743, 2948]],
                                        format_func=item_name_code,
                                        key='d3', help=help["sidebar_consumer"][3])
        
        if len(meatfree_extra_items) > 0:
            meatfree_extra_items = np.hstack(meatfree_extra_items)


        # waste = cw.label_plus_slider('Food waste and over-eating reduction', ratio=(6,4),
        waste = st.slider('Food waste and over-eating reduction',
                                        min_value=0, max_value=100, step=25,
                                        key="d4", help=help["sidebar_consumer"][4])

        # labmeat = cw.label_plus_slider('Increase labmeat uptake', ratio=(6,4),
        labmeat = st.slider('Increase cultured meat uptake',
                                        min_value=0, max_value=100, step=25,
                                        key="d5", help=help["sidebar_consumer"][6])
       

        extra_items_cultured = cw.label_plus_multiselect('Also replace with cultured meat',
                                        options=[[2733], [2734]],
                                        format_func=item_name_code,
                                        key='d6', help=help["sidebar_consumer"][7])
        
        if len(extra_items_cultured) > 0:
            extra_items_cultured = np.hstack(extra_items_cultured)


        st.button("Reset", on_click=update_slider, key='reset_d',
                  kwargs={"values": [0, 0, [], 0, 0, []],
                          "keys": ['d1', 'd2', 'd3', 'd4', 'd5', 'd6']},)

    # Land management interventions
    with st.expander("**:earth_africa: Land management**"):

        pasture_sparing = st.slider('Spared ALC 4 & 5 pasture land fraction',
                                                min_value=0, max_value=100, step=25,
                                                key='l1', help=help["sidebar_land"][0])

        arable_sparing = st.slider('Spared ALC 4 & 5 arable land fraction',
                                                min_value=0, max_value=100, step=25,
                                                key='l2', help=help["sidebar_land"][1])

        foresting_spared = st.slider('Forested spared land fraction',
                                                min_value=0, max_value=100, step=25,
                                                key='l3', help=help["sidebar_land"][2])

        
        silvopasture = st.slider('Farmland % converted to silvopasture',
                                                min_value=0, max_value=100, step=25,
                                                key='l4', help=help["sidebar_land"][3])
        

        agroforestry = st.slider('Farmland % converted to agroforestry',
                                                min_value=0, max_value=100, step=25,
                                                key='l5', help=help["sidebar_land"][4])
       
       
        # biofuel_spared = cw.label_plus_slider('Biofuel crops spared land fraction',ratio=(6,4),
        # biofuel_spared = st.slider('Biofuel crops spared land fraction',
        #                                         min_value=0, max_value=100, step=25,
        #                                         key='l4', help=help["sidebar_land"][3])
       
        # CCS_spared = cw.label_plus_slider('Carbon capture and storage spared land fraction',ratio=(6,4),
        # CCS_spared = st.slider('Carbon capture and storage spared land fraction',
        #                                         min_value=0, max_value=100, step=25,
        #                                         key='l5', help=help["sidebar_land"][4])


        # biofuel_spared = cw.label_plus_slider('Biofuel crops spared land fraction',ratio=(6,4),
        # biofuel_spared = st.slider('Biofuel crops spared land fraction',
        #                                         min_value=0, max_value=100, step=25,
        #                                         key='l4', help=help["sidebar_land"][3])
       
        # CCS_spared = cw.label_plus_slider('Carbon capture and storage spared land fraction',ratio=(6,4),
        # CCS_spared = st.slider('Carbon capture and storage spared land fraction',
        #                                         min_value=0, max_value=100, step=25,
        #                                         key='l5', help=help["sidebar_land"][4])

        st.button("Reset", on_click=update_slider, kwargs={"values": [0,0,0,0,0,0], "keys": ['l1', 'l2', 'l3', 'l4', 'l5']}, key='reset_l')

    # Technology and innovation
    with st.expander("**:gear: Technology and innovation**"):

        waste_BECCS = st.slider('BECCS sequestration from waste \n [Mt CO2e / yr]',
                                                min_value=0, max_value=100, step=1,
                                                key='i1', help=help["sidebar_innovation"][0])


        overseas_BECCS = st.slider('BECCS sequestration from overseas biomass \n [Mt CO2e / yr]',
                                                min_value=0, max_value=100, step=1,
                                                key='i2', help=help["sidebar_innovation"][1])


        land_BECCS = st.slider('Percentage of farmland used for BECCS crops',
                                                min_value=0, max_value=20, step=1,
                                                key='i3', help=help["sidebar_innovation"][2])


        DACCS = st.slider('DACCS sequestration \n [Mt CO2e / yr]',
                                                min_value=0, max_value=20, step=1,
                                                key='i4', help=help["sidebar_innovation"][3])

        incr_GHGE_innovation_crop = st.slider('Plant production GHGE innovation',
                                                min_value=0, max_value=4, step=1,
                                                key='i5', help=help["sidebar_innovation"][4])

        incr_GHGE_innovation_meat = st.slider('Animal production GHGE innovation',
                                                min_value=0, max_value=4, step=1,
                                                key='i6', help=help["sidebar_innovation"][5])

        st.button("Reset", on_click=update_slider, kwargs={"values": [0,0,0,0,0,0], "keys": ['i1', 'i2', 'i3', 'i4', 'i5', 'i6']}, key='reset_i')

    # Policy interventions
    #with st.expander("**:office: Policy interventions**"):
    #    st.write('Policy intervention sliders to be shown here')

    with st.expander("Advanced settings"):

        labmeat_co2e = st.slider('Cultured meat GHG emissions [g CO2e / g]', min_value=1., max_value=120., value=25., key='labmeat_slider')
        rda_kcal = st.slider('Recommended daily energy intake [kCal]', min_value=2000, max_value=2500, value=2250)
        n_scale = st.slider('Adoption timescale [years]', min_value=0, max_value=50, value=20, step=5)
        max_ghge_animal = st.slider('Maximum animal production GHGE reduction due to innovation [%]', min_value=0, max_value=100, value=30, step=10, key = "max_ghg_animal", help = help["advanced_options"][3])
        max_ghge_plant = st.slider('Maximum plant production GHGE reduction due to innovation [%]', min_value=0, max_value=100, value=30, step=10, key = "max_ghg_plant", help = help["advanced_options"][4])
        bdleaf_conif_ratio = st.slider('Ratio of coniferous to broadleaved reforestation', min_value=0, max_value=100, value=50, step=10, key = "bdleaf_conif_ratio", help = help["advanced_options"][5])
        bdleaf_seq_ha_yr = st.slider('Broadleaved forest CO2 sequestration [t CO2 / ha / year]', min_value=7., max_value=15., value=12.5, step=0.5, key = "bdleaf_seq_ha_yr", help = help["advanced_options"][6])
        conif_seq_ha_yr = st.slider('Coniferous forest CO2 sequestration [t CO2 / ha / year]', min_value=15., max_value=30., value=23.5, step=0.5, key = "conif_seq_ha_yr", help = help["advanced_options"][7])

        scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                                    ('Weight', 'Proteins', 'Fat', 'Energy'),
                                    horizontal=True,
                                    index=3,
                                    help=help["sidebar_consumer"][0],
                                    key='a7')
        
        st.button("Reset", on_click=update_slider,
                  kwargs={"values": [25,2250,2,12.47,30,30, "Energy"],
                          "keys": ['labmeat_slider', 'a2', 'a3', 'a4', 'max_ghg_animal', 'max_ghg_plant', 'a7']},
                  key='reset_a')



    st.markdown('''--- Developed with funding from [FixOurFood](https://fixourfood.org/).''')
    
    st.markdown('''--- We would be grateful for your feedback, via
                [this form](https://docs.google.com/forms/d/e/1FAIpQLSdnBp2Rmr-1fFYRQvEVcLLKchdlXZG4GakTBK5yy6jozUt8NQ/viewform?usp=sf_link).''')
    
    st.markdown('''--- For a list of references to the datasets used, please
                visit our [reference document](https://docs.google.com/spreadsheets/d/1XkOELCFKHTAywUGoJU6Mb0TjXESOv5BbR67j9UCMEgw/edit?usp=sharing).''')

col1, col2 = st.columns((7,3))

with col1:
    # ----------------------------------------
    #                  Main
    # ----------------------------------------

    datablock = copy.deepcopy(st.session_state["datablock_baseline"])
    food_system = Pipeline(datablock)

    # Global parameters
    food_system.datablock_write(["global_parameters", "timescale"], n_scale)

    # Consumer demand
    food_system.add_step(project_future,
                         {"scale":proj_pop})
    
    food_system.add_step(ruminant_consumption_model,
                         {"ruminant_scale":ruminant,
                          "items":[2731, 2732]})
    
    food_system.add_step(meat_consumption_model,
                         {"meat_scale":meatfree,
                          "extra_items":meatfree_extra_items})
    
    food_system.add_step(food_waste_model,
                         {"waste_scale":waste,
                          "kcal_rda":rda_kcal})

    food_system.add_step(cultured_meat_model,
                         {"cultured_scale":labmeat/100,
                          "labmeat_co2e":labmeat_co2e,
                          "extra_items":extra_items_cultured})
    
    # Land management
    food_system.add_step(spare_alc_model,
                         {"spare_fraction":pasture_sparing/100,
                          "land_type":["Improved grassland", "Semi-natural grassland"],
                          "alc_grades":[4,5],
                          "items":"Animal Products"})
    
    food_system.add_step(spare_alc_model,
                         {"spare_fraction":arable_sparing/100,
                          "land_type":["Arable"],
                          "alc_grades":[4,5],
                          "items":"Vegetal Products"})
    
    food_system.add_step(foresting_spared_model,
                         {"forest_fraction":foresting_spared/100,
                          "bdleaf_conif_ratio":bdleaf_conif_ratio/100})
    
    # Technology & Innovation
    food_system.add_step(BECCS_farm_land,
                         {"farm_percentage":land_BECCS/100})
    
    food_system.add_step(ccs_model,
                         {"waste_BECCS":waste_BECCS*1e6,
                          "overseas_BECCS":overseas_BECCS*1e6,
                          "DACCS":DACCS*1e6})
    
    food_system.add_step(scale_impact,
                         {"item_origin":"Vegetal Products",
                          "scale_factor":1 - max_ghge_plant*incr_GHGE_innovation_crop/400})
    
    food_system.add_step(scale_impact,
                         {"item_origin":"Animal Products",
                         "scale_factor":1 - max_ghge_animal*incr_GHGE_innovation_meat/400})
    
    # Compute emissions and sequestration
    food_system.add_step(forest_sequestration_model,
                         {"seq_broadleaf_ha_yr":bdleaf_seq_ha_yr,
                          "seq_coniferous_ha_yr":conif_seq_ha_yr})

    food_system.add_step(compute_emissions)

    food_system.run()

    datablock = food_system.datablock

    # -------------------
    # Execute plots block
    # -------------------
    from plots import plots
    metric_yr = plots(datablock)
   
with col2:
    # ---------------------
    # Execute Metrics block
    # ---------------------
    from metrics import metrics
    metrics(datablock, metric_yr)
