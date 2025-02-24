import streamlit as st
from streamlit_extras.bottom_container import bottom

import pandas as pd
import copy

from utils.pipeline import Pipeline
import utils.custom_widgets as cw
from utils.altair_plots import *
from utils.helper_functions import *

from glossary import *
from scenarios import call_scenarios, scenarios_dict

from datablock_setup import *
from model import *

from agrifoodpy.land import land

@st.experimental_dialog("This is an outdated version of the Agrifood Calculator")
def first_run_dialog(width="large"):
    st.write("""Please visit the new version at https://fixourfood.org/calculator""")
    if st.button("OK", type="primary"):
        st.rerun()

if "datablock_baseline" not in st.session_state:
    st.session_state["datablock_baseline"] = datablock

if "first_run" not in st.session_state:
    st.session_state["first_run"] = True

# ------------------------
# Help and tooltip strings
# ------------------------
help = pd.read_csv(st.secrets["tooltips_url"], dtype='string')

# GUI
st.set_page_config(layout='wide',
                   initial_sidebar_state='expanded',
                   page_title="Agrifood Calculator",
                   page_icon="images/fof_icon.png")

with open('utils/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if st.session_state.first_run:
    st.session_state.first_run = False
    first_run_dialog()

with st.sidebar:

# ------------------------
#        Sidebar
# ------------------------

    col1, col2 = st.columns([7.5,2.5])
    with col1:
        st.selectbox("Scenario", scenarios_dict.keys(),
                     help=help_str(help, "sidebar_consumer", 8),
                     on_change=call_scenarios, key="scenario")

    with col2:
        st.button("Reset \n sliders", on_click=reset_sliders, key='reset_all')

    # Consumer demand interventions

    with st.expander("**:spaghetti: Consumer demand**", expanded=False):

        consumer_slider_keys = ["ruminant", "dairy", "pig_poultry_eggs", "fruit_veg", "cereals", "waste", "labmeat"]

        ruminant = st.slider('Reduce ruminant meat consumption',
                        min_value=0, max_value=100, step=25,
                        key="ruminant", help=help_str(help, "sidebar_consumer", 1, "pjtbcox0lw1k"))
        
        dairy = st.slider('Reduce dairy consumption',
                        min_value=0, max_value=100, step=25,
                        key="dairy", help=help["sidebar_consumer"][2])
        
        pig_poultry_eggs = st.slider('Reduce pig, poultry and eggs consumption',
                        min_value=0, max_value=100, step=25,
                        key="pig_poultry_eggs", help=help["sidebar_consumer"][3])
        
        fruit_veg = st.slider('Increase fruit and vegetable consumption',
                        min_value=0, max_value=100, step=25,
                        key="fruit_veg", help=help["sidebar_consumer"][4])
        
        cereals = st.slider('Increase cereal consumption',
                        min_value=0, max_value=100, step=25,
                        key="cereals", help=help["sidebar_consumer"][5])

        waste = st.slider('Food waste and over-eating reduction',
                        min_value=0, max_value=100, step=25,
                        key="waste", help=help["sidebar_consumer"][6])

        labmeat = st.slider('Increase cultured meat uptake',
                        min_value=0, max_value=100, step=25,
                        key="labmeat", help=help["sidebar_consumer"][7])       

        st.button("Reset", on_click=reset_sliders, key='reset_consumer',
                  kwargs={"keys": [consumer_slider_keys, "consumer_bar"]})

    # Land use change

    with st.expander("**:earth_africa: Land use change**"):

        land_slider_keys = ["pasture_sparing", "land_beccs", "arable_sparing", "foresting_spared"]

        pasture_sparing = st.slider('Spared pasture land fraction',
                        min_value=0, max_value=100, step=25,
                        key="pasture_sparing", help=help["sidebar_land"][0])        

        arable_sparing = st.slider('Spared arable land fraction',
                        min_value=0, max_value=100, step=25,
                        key="arable_sparing", help=help["sidebar_land"][1])

        land_BECCS = st.slider('Percentage of farmland used for BECCS crops',
                        min_value=0, max_value=20, step=5,
                        key="land_beccs", help=help["sidebar_innovation"][2])

        foresting_spared = st.slider('Forested spared land fraction',
                        min_value=0, max_value=100, step=25,
                        key="foresting_spared", help=help["sidebar_land"][2])
        
        st.button("Reset", on_click=reset_sliders, key='reset_land',
                  kwargs={"keys":[land_slider_keys, "land_bar"]})
        
    # Livestock farming practices

    with st.expander("**:cow: Livestock farming practices**"):

        livestock_slider_keys = ["silvopasture",
                                 "methane_inhibitor",
                                 "manure_management",
                                 "animal_breeding",
                                 "fossil_livestock"]
        
        silvopasture = st.slider('Pasture land % converted to silvopasture',
                        min_value=0, max_value=100, step=25,
                        key='silvopasture', help=help["sidebar_land"][3])        
        
        methane_inhibitor = st.slider('Methane inhibitor use in livestock feed',
                        min_value=0, max_value=100, step=25,
                        key='methane_inhibitor', help=help["sidebar_livestock"][0])
        
        manure_management = st.slider('Manure management in livestock farming',
                        min_value=0, max_value=100, step=25,
                        key='manure_management', help=help["sidebar_livestock"][1])
        
        animal_breeding = st.slider('Livestock breeding',
                        min_value=0, max_value=100, step=25,
                        key='animal_breeding', help=help["sidebar_livestock"][2])
        
        fossil_livestock = st.slider('Fossil fuel use for heating, machinery',
                        min_value=0, max_value=100, step=25,
                        key='fossil_livestock', help=help["sidebar_livestock"][4])
        

        st.button("Reset", on_click=reset_sliders, key='reset_livestock',
            kwargs={"keys": [livestock_slider_keys, "livestock_bar"]})

    # Arable farming practices

    with st.expander("**:ear_of_rice: Arable farming practices**"):

        arable_slider_keys = ["agroforestry", "fossil_arable"]
        
        agroforestry = st.slider('Arable land % converted to agroforestry',
                        min_value=0, max_value=100, step=25,
                        key='agroforestry', help=help["sidebar_land"][4])

        fossil_arable = st.slider('Fossil fuel use for machinery',
                        min_value=0, max_value=100, step=25,
                        key='fossil_arable', help=help["sidebar_arable"][1])
                        
        st.button("Reset", on_click=reset_sliders, key='reset_arable',
            kwargs={"keys": [arable_slider_keys, "arable_bar"]})        

    # Technology and innovation

    with st.expander("**:gear: Technology and innovation**"):
        
        technology_slider_keys = ["waste_BECCS", "overseas_BECCS", "DACCS"]

        waste_BECCS = st.slider('BECCS sequestration from waste \n [Mt CO2e / yr]',
                        min_value=0, max_value=100, step=25,
                        key='waste_BECCS', help=help["sidebar_innovation"][0])

        overseas_BECCS = st.slider('BECCS sequestration from overseas biomass \n [Mt CO2e / yr]',
                        min_value=0, max_value=100, step=25,
                        key='overseas_BECCS', help=help["sidebar_innovation"][1])

        DACCS = st.slider('DACCS sequestration \n [Mt CO2e / yr]',
                        min_value=0, max_value=20, step=5,
                        key='DACCS', help=help["sidebar_innovation"][3])

        st.button("Reset", on_click=reset_sliders, key='reset_technology',
                  kwargs={"keys": [technology_slider_keys, "innovation_bar"]})
        
    # Advanced settings

    with st.expander("Advanced settings"):
        from advanced_settings import advanced_settings as advs
        
        password = st.text_input("Enter the advanced settings password", type="password")
        if password == st.secrets["advanced_options_password"]:

            for label, params in  advs.items():
                advs[label]["value"] = st.slider(params["label"],
                                                 min_value=params["min_value"],
                                                 max_value=params["max_value"],
                                                 value=params["value"],
                                                 step=params["step"],
                                                 key=params["key"])

            scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                                        ('g/cap/day', 'g_prot/cap/day', 'g_fat/cap/day', 'kCal/cap/day'),
                                        horizontal=True,
                                        index=3,
                                        help=help["advanced_options"][9],
                                        key='nutrient_constant')
            
            st.button("Reset", on_click=update_slider,
                    kwargs={"values": [25.0, 2250, 20, 30, 30, 50., 12.5, 23.5, 0.1, "kCal/cap/day"],
                            "keys": ['labmeat_slider', 'rda_slider',
                                     'timescale_slider', 'max_ghg_animal',
                                     'max_ghg_plant', 'bdleaf_conif_ratio',
                                     'bdleaf_seq_ha_yr', 'conif_seq_ha_yr',
                                     'tree_coverage', 'nutrient_constant']},
                    key='reset_a')

        else:
            if password != "":
                st.error("Incorrect password")

            for label, params in advs.items():
                advs[label]['value'] = params["value"]

            scaling_nutrient = 'kCal/cap/day'            

    st.caption('''--- Developed with funding from [FixOurFood](https://fixourfood.org/).''')
    
    st.caption('''--- We would be grateful for your feedback, via
                [this form](https://docs.google.com/forms/d/e/1FAIpQLSdnBp2Rmr-1fFYRQvEVcLLKchdlXZG4GakTBK5yy6jozUt8NQ/viewform?usp=sf_link).''')
    
    st.caption('''--- For a list of references to the datasets used, please
                visit our [reference document](https://docs.google.com/spreadsheets/d/1XkOELCFKHTAywUGoJU6Mb0TjXESOv5BbR67j9UCMEgw/edit?usp=sharing).''')

col1, = st.columns(1)

with col1:
    # ----------------------------------------
    #                  Main
    # ----------------------------------------

    datablock = copy.deepcopy(st.session_state["datablock_baseline"])
    food_system = Pipeline(datablock)

    # Global parameters
    food_system.datablock_write(["global_parameters", "timescale"], advs["n_scale"]["value"])

    # Consumer demand
    food_system.add_step(project_future,
                         {"scale":proj_pop})
    
    food_system.add_step(item_scaling,
                         {"scale":1-ruminant/100,
                          "items":[2731, 2732],
                          "source":["production", "imports"],
                          "elasticity":[advs["elasticity"]["value"], 1-advs["elasticity"]["value"]],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(item_scaling,
                         {"scale":1-pig_poultry_eggs/100,
                          "items":[2733, 2734, 2949],
                          "source":["production", "imports"],
                          "elasticity":[advs["elasticity"]["value"], 1-advs["elasticity"]["value"]],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(item_scaling,
                         {"scale":1-dairy/100,
                          "items":[2740, 2743, 2948],
                          "source":["production", "imports"],
                          "elasticity":[advs["elasticity"]["value"], 1-advs["elasticity"]["value"]],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(item_scaling,
                         {"scale":1+fruit_veg/100,
                          "item_group":["Vegetables", "Fruits - Excluding Wine"],
                          "source":["production", "imports"],
                          "elasticity":[advs["elasticity"]["value"], 1-advs["elasticity"]["value"]],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(item_scaling,
                         {"scale":1+cereals/100,
                          "item_group":["Cereals - Excluding Beer"],
                          "source":["production", "imports"],
                          "elasticity":[advs["elasticity"]["value"], 1-advs["elasticity"]["value"]],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(food_waste_model,
                         {"waste_scale":waste,
                          "kcal_rda":advs["rda_kcal"]["value"],
                          "source":"imports"})

    food_system.add_step(cultured_meat_model,
                         {"cultured_scale":labmeat/100,
                          "labmeat_co2e":advs["labmeat_co2e"]["value"],
                          "source":"production"})
    
    # Land management
    food_system.add_step(spare_alc_model,
                         {"spare_fraction":pasture_sparing/100,
                          "land_type":["Improved grassland", "Semi-natural grassland"],
                          "items":"Animal Products"})
    
    food_system.add_step(spare_alc_model,
                         {"spare_fraction":arable_sparing/100,
                          "land_type":["Arable"],
                          "items":"Vegetal Products"})
    
    food_system.add_step(foresting_spared_model,
                         {"forest_fraction":foresting_spared/100,
                          "bdleaf_conif_ratio":advs["bdleaf_conif_ratio"]["value"]/100})
    
    food_system.add_step(BECCS_farm_land,
                         {"farm_percentage":land_BECCS/100})
    
    # Livestock farming practices        
    food_system.add_step(agroecology_model,
                         {"land_percentage":silvopasture/100.,
                          "agroecology_class":"Silvopasture",
                          "land_type":["Improved grassland", "Semi-natural grassland"],
                          "tree_coverage":advs["agroecology_tree_coverage"]["value"],
                          "replaced_items":[2731, 2732],
                          "new_items":2617,
                          "item_yield":1e2})
    
    food_system.add_step(scale_impact,
                         {"items":[2731, 2732],
                          "scale_factor":1 - advs["methane_ghg_factor"]["value"]*methane_inhibitor/100})
    
    food_system.add_step(scale_production,
                         {"scale_factor":1-advs["methane_prod_factor"]["value"]*methane_inhibitor/100,
                          "items":[2731, 2732]})
    
    food_system.add_step(scale_impact,
                         {"items":[2731, 2732],
                          "scale_factor":1 - advs["manure_ghg_factor"]["value"]*manure_management/100})
    
    food_system.add_step(scale_production,
                         {"scale_factor":1-advs["manure_prod_factor"]["value"]*manure_management/100,
                          "items":[2731, 2732]})
    
    food_system.add_step(scale_impact,
                         {"items":[2731, 2732],
                          "scale_factor":1 - advs["breeding_ghg_factor"]["value"]*animal_breeding/100})
    
    food_system.add_step(scale_production,
                         {"scale_factor":1-advs["breeding_prod_factor"]["value"]*animal_breeding/100,
                          "items":[2731, 2732]})

    # Arable farming practices
    food_system.add_step(agroecology_model,
                         {"land_percentage":agroforestry/100.,
                          "agroecology_class":"Agroforestry",
                          "land_type":["Arable"],
                          "tree_coverage":advs["agroecology_tree_coverage"]["value"],
                          "replaced_items":2511,
                          "new_items":2617,
                          "item_yield":1e2})
    
    food_system.add_step(scale_impact,
                         {"item_origin":"Vegetal Products",
                          "scale_factor":1 - advs["fossil_arable_ghg_factor"]["value"]*fossil_arable/100})
    
    food_system.add_step(scale_production,
                         {"scale_factor":1 - advs["fossil_arable_prod_factor"]["value"]*fossil_arable/100,
                          "item_origin":"Vegetal Products"})
    
    # Technology & Innovation    
    food_system.add_step(ccs_model,
                         {"waste_BECCS":waste_BECCS*1e6,
                          "overseas_BECCS":overseas_BECCS*1e6,
                          "DACCS":DACCS*1e6})

    
    # Compute emissions and sequestration
    food_system.add_step(forest_sequestration_model,
                         {"seq_broadleaf_ha_yr":advs["bdleaf_seq_ha_yr"]["value"],
                          "seq_coniferous_ha_yr":advs["conif_seq_ha_yr"]["value"]})

    food_system.add_step(compute_emissions)

    food_system.run()

    datablock = food_system.datablock

    # -------------------
    # Execute plots block
    # -------------------
    from plots import plots
    metric_yr = plots(datablock)
