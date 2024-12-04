import streamlit as st
from streamlit_extras.bottom_container import bottom

import pandas as pd
import copy

from utils.pipeline import Pipeline
import utils.custom_widgets as cw
from utils.altair_plots import *
from utils.helper_functions import *

from glossary import *
# from scenarios import call_scenarios, scenarios_dict
from consultation_utils import get_pathways, call_scenarios

from datablock_setup import *
from model import *

from agrifoodpy.land import land

if "datablock_baseline" not in st.session_state:
    st.session_state["datablock_baseline"] = datablock

if "cereal_scaling" not in st.session_state:
    st.session_state["cereal_scaling"] = True

if "cereals" not in st.session_state:
    st.session_state["cereals"] = 0

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

with st.sidebar:

# ------------------------
#        Sidebar
# ------------------------

    col1, col2 = st.columns([7.5,2.5])
    with col1:
        st.selectbox("Scenario", get_pathways(),
                     help=help_str(help, "sidebar_consumer", 8),
                     on_change=call_scenarios, key="scenario")

    with col2:
        st.button("Reset \n sliders", on_click=reset_sliders, key='reset_all')

    # Consumer demand interventions

    with st.expander("**:spaghetti: Consumer demand**", expanded=False):

        consumer_slider_keys = ["ruminant", "dairy", "pig_poultry_eggs", "fruit_veg", "cereals", "waste", "labmeat", "dairy_alt"]

        ruminant = st.slider('Reduce ruminant meat consumption',
                        min_value=-100, max_value=100, step=1, value=0,
                        key="ruminant", help=help_str(help, "sidebar_consumer", 1, "pjtbcox0lw1k"))
        
        dairy = st.slider('Reduce dairy consumption',
                        min_value=-100, max_value=100, step=1, value=0,
                        key="dairy", help=help["sidebar_consumer"][2])
        
        pig_poultry_eggs = st.slider('Reduce pig, poultry and eggs consumption',
                        min_value=-100, max_value=100, step=1, value=0,
                        key="pig_poultry_eggs", help=help["sidebar_consumer"][3])
        
        fruit_veg = st.slider('Increase fruit and vegetable consumption',
                        min_value=-100, max_value=100, step=1, value=0,
                        key="fruit_veg", help=help["sidebar_consumer"][4])
        
        if not st.session_state["cereal_scaling"]:
            cereals = st.slider('Increase cereal consumption',
                            min_value=-100, max_value=100, step=1, value=0,
                            key="cereals", help=help["sidebar_consumer"][5],
                            disabled=st.session_state["cereal_scaling"])

        meat_alternatives = st.slider('Increase meat alternatives uptake',
                        min_value=-100, max_value=100, step=1, value=0,
                        key="labmeat", help=help["sidebar_consumer"][7])     
        
        dairy_alternatives = st.slider('Increase dairy alternatives uptake',
                        min_value=-100, max_value=100, step=1, value=0,
                        key="dairy_alt", help=help["sidebar_consumer"][7])
        
        waste = st.slider('Food waste and over-eating reduction',
                        min_value=-100, max_value=100, step=1, value=0,
                        key="waste", help=help["sidebar_consumer"][6])  

        st.button("Reset", on_click=reset_sliders, key='reset_consumer',
                  kwargs={"keys": [consumer_slider_keys, "consumer_bar"]})

    # Land use change

    with st.expander("**:earth_africa: Land use change**"):

        land_slider_keys = ["foresting_pasture", "land_beccs"]

        foresting_pasture = st.slider('Forested pasture land fraction',
                        min_value=0, max_value=100, step=1,
                        key="foresting_pasture", help=help["sidebar_land"][0])        

        # arable_sparing = st.slider('Spared arable land fraction',
        #                 min_value=0, max_value=100, step=1,
        #                 key="arable_sparing", help=help["sidebar_land"][1])

        land_BECCS = st.slider('Percentage of farmland used for BECCS crops',
                        min_value=0, max_value=20, step=1,
                        key="land_beccs", help=help["sidebar_innovation"][2])

        # foresting_spared = st.slider('Forested spared land fraction',
        #                 min_value=0, max_value=100, step=1,
        #                 key="foresting_spared", help=help["sidebar_land"][2])
        
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
                        min_value=0, max_value=100, step=1,
                        key='silvopasture', help=help["sidebar_land"][3])        
        
        methane_inhibitor = st.slider('Methane inhibitor use in livestock feed',
                        min_value=0, max_value=100, step=1,
                        key='methane_inhibitor', help=help["sidebar_livestock"][0])
        
        manure_management = st.slider('Manure management in livestock farming',
                        min_value=0, max_value=100, step=1,
                        key='manure_management', help=help["sidebar_livestock"][1])
        
        animal_breeding = st.slider('Livestock breeding',
                        min_value=0, max_value=100, step=1,
                        key='animal_breeding', help=help["sidebar_livestock"][2])
        
        fossil_livestock = st.slider('Fossil fuel use for heating, machinery',
                        min_value=0, max_value=100, step=1,
                        key='fossil_livestock', help=help["sidebar_livestock"][4])
        

        st.button("Reset", on_click=reset_sliders, key='reset_livestock',
            kwargs={"keys": [livestock_slider_keys, "livestock_bar"]})

    # Arable farming practices

    with st.expander("**:ear_of_rice: Arable farming practices**"):

        arable_slider_keys = ["agroforestry", "fossil_arable"]
        
        agroforestry = st.slider('Arable land % converted to agroforestry',
                        min_value=0, max_value=100, step=1,
                        key='agroforestry', help=help["sidebar_land"][4])

        fossil_arable = st.slider('Fossil fuel use for machinery',
                        min_value=0, max_value=100, step=1,
                        key='fossil_arable', help=help["sidebar_arable"][1])
                        
        st.button("Reset", on_click=reset_sliders, key='reset_arable',
            kwargs={"keys": [arable_slider_keys, "arable_bar"]})        

    # Technology and innovation

    with st.expander("**:gear: Technology and innovation**"):
        
        technology_slider_keys = ["waste_BECCS", "overseas_BECCS", "DACCS"]

        waste_BECCS = st.slider('BECCS sequestration from waste \n [Mt CO2e / yr]',
                        min_value=0, max_value=100, step=1,
                        key='waste_BECCS', help=help["sidebar_innovation"][0])

        overseas_BECCS = st.slider('BECCS sequestration from overseas biomass \n [Mt CO2e / yr]',
                        min_value=0, max_value=100, step=1,
                        key='overseas_BECCS', help=help["sidebar_innovation"][1])

        DACCS = st.slider('DACCS sequestration \n [Mt CO2e / yr]',
                        min_value=0, max_value=20, step=1,
                        key='DACCS', help=help["sidebar_innovation"][3])

        st.button("Reset", on_click=reset_sliders, key='reset_technology',
                  kwargs={"keys": [technology_slider_keys, "innovation_bar"]})
        
    # Advanced settings

    with st.expander("Advanced settings"):
        
        password = st.text_input("Enter the advanced settings password", type="password")
        if password == st.secrets["advanced_options_password"]:

            check_ID = st.checkbox('Check ID for submission', value=True, key='check_ID')
            emission_factors = st.selectbox('Emission factors', options=["NDC 2020", "PN18"], key='emission_factors')
            cereal_scaling = st.checkbox('Scale cereal production to meet nutrient demands', value=True, key='cereal_scaling')

            cc_production_decline = st.checkbox('Production decline caused by climate change', value=False, key='cc_production_decline')

            labmeat_co2e = st.slider('Cultured meat GHG emissions [g CO2e / g]', min_value=1., max_value=120., value=6.5, key='labmeat_slider')
            dairy_alternatives_co2e = st.slider('Dairy alternatives GHG emissions [g CO2e / g]', min_value=0.10, max_value=0.27, value=0.14, key='dairy_alternatives_slider')
            
            rda_kcal = st.slider('Recommended daily energy intake [kCal]', min_value=2000, max_value=2500, value=2250, key='rda_slider')
            n_scale = st.slider('Adoption timescale [years]', min_value=0, max_value=50, value=20, step=5, key='timescale_slider')
            max_ghge_animal = st.slider('Maximum animal production GHGE reduction due to innovation [%]', min_value=0, max_value=100, value=30, step=10, key = "max_ghg_animal", help = help["advanced_options"][3])
            max_ghge_plant = st.slider('Maximum plant production GHGE reduction due to innovation [%]', min_value=0, max_value=100, value=30, step=10, key = "max_ghg_plant", help = help["advanced_options"][4])
            bdleaf_conif_ratio = st.slider('Ratio of coniferous to broadleaved reforestation', min_value=0, max_value=100, value=75, step=10, key = "bdleaf_conif_ratio", help = help["advanced_options"][5])
            bdleaf_seq_ha_yr = st.slider('Broadleaved forest CO2 sequestration [t CO2 / ha / year]', min_value=1., max_value=15., value=3.5, step=0.5, key = "bdleaf_seq_ha_yr", help = help["advanced_options"][6])
            conif_seq_ha_yr = st.slider('Coniferous forest CO2 sequestration [t CO2 / ha / year]', min_value=1., max_value=30., value=6.5, step=0.5, key = "conif_seq_ha_yr", help = help["advanced_options"][7])
            elasticity = st.slider("Production / Imports elasticity ratio", min_value=0., max_value=1., value=0.5, step=0.1, key="elasticity", help = help["advanced_options"][9])
            agroecology_tree_coverage = st.slider("Tree coverage in agroecology", min_value=0., max_value=1., value=0.1, step=0.1, key="tree_coverage")
            
            # tillage_prod_factor = st.slider("Soil tillage production reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="tillage_prod")
            # tillage_ghg_factor = st.slider("Soil tillage GHG reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="tillage_ghg")

            manure_prod_factor = st.slider("Manure production reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="manure_prod")
            manure_ghg_factor = st.slider("Manure GHG reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="manure_ghg")

            breeding_prod_factor = st.slider("Breeding production reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="breeding_prod")
            breeding_ghg_factor = st.slider("Breeding GHG reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="breeding_ghg")

            methane_prod_factor = st.slider("Methane inhibitors production reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="methane_prod")
            methane_ghg_factor = st.slider("Methane inhibitors GHG reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="methane_ghg")

            # soil_management_ghg_factor = st.slider("Soil and carbon management GHG reduction", min_value=0., max_value=.2, value=0.05, step=0.01, key="soil_management_ghg")

            fossil_livestock_ghg_factor = st.slider("Livestock fossil fuel GHG reduction", min_value=0., max_value=.2, value=0.05, step=0.01, key="fossil_livestock_ghg")
            fossil_arable_ghg_factor = st.slider("Arable fossil fuel GHG reduction", min_value=0., max_value=.2, value=0.05, step=0.01, key="fossil_arable_ghg")

            fossil_livestock_prod_factor = st.slider("Livestock fossil fuel production reduction", min_value=0., max_value=1., value=0.05, step=0.01, key="fossil_livestock_prod")
            fossil_arable_prod_factor = st.slider("Arable fossil fuel production reduction", min_value=0., max_value=1., value=0.05, step=0.01, key="fossil_arable_prod")
            
            scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                                        ('g/cap/day', 'g_prot/cap/day', 'g_fat/cap/day', 'kCal/cap/day'),
                                        horizontal=True,
                                        index=3,
                                        help=help["advanced_options"][9],
                                        key='nutrient_constant')
            
            st.button("Reset", on_click=update_slider,
                    kwargs={"values": [6.5, 0.14, 2250, 20, 30, 30, 50, 3.5, 6.5, 0.1, "kCal/cap/day"],
                            "keys": ['labmeat_slider',
                                     'dairy_alternatives_slider',
                                     'rda_slider',
                                     'timescale_slider',
                                     'max_ghg_animal',
                                     'max_ghg_plant',
                                     'bdleaf_conif_ratio',
                                     'bdleaf_seq_ha_yr',
                                     'conif_seq_ha_yr',
                                     'tree_coverage',
                                     'nutrient_constant']},
                    key='reset_a')

        else:
            if password != "":
                st.error("Incorrect password")

            st.session_state.cereal_scaling = True
            st.session_state.check_ID = True
            st.session_state.emission_factors = "NDC 2020"

            cc_production_decline = False

            labmeat_co2e = 6.5
            dairy_alternatives_co2e = 0.14
            rda_kcal = 2250
            n_scale = 20
            max_ghge_animal = 30
            max_ghge_plant = 30

            st.session_state.bdleaf_conif_ratio = 75
            st.session_state.bdleaf_seq_ha_yr = 3.5
            st.session_state.conif_seq_ha_yr = 6.5

            st.session_state.elasticity = 0.5
            agroecology_tree_coverage = 0.1

            # tillage_prod_factor = 0.3
            # tillage_ghg_factor = 0.3

            manure_prod_factor = 0.3
            manure_ghg_factor = 0.3

            breeding_prod_factor = 0.3
            breeding_ghg_factor = 0.3

            methane_prod_factor = 0.3
            methane_ghg_factor = 0.3

            # soil_management_ghg_factor = 0.05

            fossil_livestock_ghg_factor = 0.05
            fossil_livestock_prod_factor = 0.05

            fossil_arable_ghg_factor = 0.05
            fossil_arable_prod_factor = 0.05
            
            scaling_nutrient = 'kCal/cap/day'              

    st.caption('''--- Developed with funding from [FixOurFood](https://fixourfood.org/).''')
    
    st.caption('''--- We would be grateful for your feedback, via
                [this form](https://docs.google.com/forms/d/e/1FAIpQLSdnBp2Rmr-1fFYRQvEVcLLKchdlXZG4GakTBK5yy6jozUt8NQ/viewform?usp=sf_link).''')
    
    st.caption('''--- For a list of references to the datasets used, please
                visit our [reference document](https://docs.google.com/spreadsheets/d/1XkOELCFKHTAywUGoJU6Mb0TjXESOv5BbR67j9UCMEgw/edit?usp=sharing).''')

# ----------------------------------------
#                  Main
# ----------------------------------------

datablock = copy.deepcopy(st.session_state["datablock_baseline"])

# Change to NDC factors if needed
if st.session_state['emission_factors'] == "NDC 2020":
    scale_ones = xr.DataArray(data = np.ones_like(food_uk.Year.values),
                        coords = {"Year":food_uk.Year.values})

    NDC_emissions = PN18_FAOSTAT["GHG Emissions (IPCC 2013)"]

    NDC_emissions.loc[{}] = 0

    NDC_emissions.loc[{"Item":2731}] = 16.94 
    NDC_emissions.loc[{"Item":2617}] = 0.13
    NDC_emissions.loc[{"Item":2513}] = 1.06
    NDC_emissions.loc[{"Item":2656}] = 0.21
    NDC_emissions.loc[{"Item":2658}] = 0.54
    NDC_emissions.loc[{"Item":2520}] = 0.00
    NDC_emissions.loc[{"Item":2740}] = 0.00
    NDC_emissions.loc[{"Item":2614}] = 0.10
    NDC_emissions.loc[{"Item":2743}] = 0.27 
    NDC_emissions.loc[{"Item":2625}] = 0.10 
    NDC_emissions.loc[{"Item":2620}] = 0.16
    NDC_emissions.loc[{"Item":2582}] = 1.63
    NDC_emissions.loc[{"Item":2735}] = 2.74
    NDC_emissions.loc[{"Item":2948}] = 0.27
    NDC_emissions.loc[{"Item":2732}] = 11.32
    NDC_emissions.loc[{"Item":2516}] = 1.06
    NDC_emissions.loc[{"Item":2586}] = 1.63
    NDC_emissions.loc[{"Item":2570}] = 1.63
    NDC_emissions.loc[{"Item":2602}] = 0.05
    NDC_emissions.loc[{"Item":2547}] = 1.66
    NDC_emissions.loc[{"Item":2733}] = 0.97
    NDC_emissions.loc[{"Item":2531}] = 0.29
    NDC_emissions.loc[{"Item":2734}] = 0.15
    NDC_emissions.loc[{"Item":2549}] = 0.91
    NDC_emissions.loc[{"Item":2574}] = 1.63
    NDC_emissions.loc[{"Item":2558}] = 1.63
    NDC_emissions.loc[{"Item":2515}] = 1.06
    NDC_emissions.loc[{"Item":2571}] = 2.05
    NDC_emissions.loc[{"Item":2542}] = 0.52
    NDC_emissions.loc[{"Item":2537}] = 0.36
    NDC_emissions.loc[{"Item":2601}] = 0.03
    NDC_emissions.loc[{"Item":2605}] = 0.23
    NDC_emissions.loc[{"Item":2511}] = 0.80
    NDC_emissions.loc[{"Item":2655}] = 0.54

    extended_impact = NDC_emissions.drop_vars(["Item_name", "Item_group", "Item_origin"]) * scale_ones

    datablock["impact"]["gco2e/gfood"] = extended_impact

food_system = Pipeline(datablock)

# Global parameters
food_system.datablock_write(["global_parameters", "timescale"], n_scale)


# Consumer demand
food_system.add_step(project_future,
                        {"scale":proj_pop,
                         "cc_decline":cc_production_decline})

food_system.add_step(item_scaling,
                        {"scale":1-ruminant/100,
                        "items":[2731, 2732],
                        "source":["production", "imports"],
                        "elasticity":[st.session_state.elasticity, 1-st.session_state.elasticity],
                        "scaling_nutrient":scaling_nutrient,
                        "constant":st.session_state.cereal_scaling,
                        "non_sel_items":cereal_items})

food_system.add_step(item_scaling,
                        {"scale":1-pig_poultry_eggs/100,
                        "items":[2733, 2734, 2949],
                        "source":["production", "imports"],
                        "elasticity":[st.session_state.elasticity, 1-st.session_state.elasticity],
                        "scaling_nutrient":scaling_nutrient,
                        "constant":st.session_state.cereal_scaling,
                        "non_sel_items":cereal_items})

food_system.add_step(item_scaling,
                        {"scale":1-dairy/100,
                        "items":[2740, 2743, 2948],
                        "source":["production", "imports"],
                        "elasticity":[st.session_state.elasticity, 1-st.session_state.elasticity],
                        "scaling_nutrient":scaling_nutrient,
                        "constant":st.session_state.cereal_scaling,
                        "non_sel_items":cereal_items})

food_system.add_step(item_scaling,
                        {"scale":1+fruit_veg/100,
                        "item_group":["Vegetables", "Fruits - Excluding Wine"],
                        "source":["production", "imports"],
                        "elasticity":[st.session_state.elasticity, 1-st.session_state.elasticity],
                        "scaling_nutrient":scaling_nutrient,
                        "constant":st.session_state.cereal_scaling,
                        "non_sel_items":cereal_items})

if not st.session_state.cereal_scaling:
    food_system.add_step(item_scaling,
                        {"scale":1+cereals/100,
                        "item_group":["Cereals - Excluding Beer"],
                        "source":["production", "imports"],
                        "elasticity":[st.session_state.elasticity, 1-st.session_state.elasticity],
                        "scaling_nutrient":scaling_nutrient})

food_system.add_step(cultured_meat_model,
                        {"cultured_scale":meat_alternatives/100,
                        "labmeat_co2e":labmeat_co2e,
                        "items":[2731, 2732],
                        "copy_from":2731,
                        "new_items":5000,
                        "new_item_name":"Alternative meat",
                        "source":"production"})

food_system.add_step(cultured_meat_model,
                        {"cultured_scale":dairy_alternatives/100,
                        "labmeat_co2e":dairy_alternatives_co2e,
                        "items":[2948],
                        "copy_from":2948,
                        "new_items":5001,
                        "new_item_name":"Alternative dairy",
                        "source":"production"})    

food_system.add_step(food_waste_model,
                        {"waste_scale":waste,
                        "kcal_rda":rda_kcal,
                        "source":["production", "imports"],
                        "elasticity":[st.session_state.elasticity, 1-st.session_state.elasticity]})


# Land management
food_system.add_step(spare_alc_model,
                        {"spare_fraction":foresting_pasture/100,
                        "land_type":["Improved grassland", "Semi-natural grassland"],
                        "items":"Animal Products"})

# food_system.add_step(spare_alc_model,
#                         {"spare_fraction":arable_sparing/100,
#                         "land_type":["Arable"],
#                         "items":"Vegetal Products"})

food_system.add_step(foresting_spared_model,
                        {"forest_fraction":1,
                        "bdleaf_conif_ratio":st.session_state.bdleaf_conif_ratio/100})

food_system.add_step(BECCS_farm_land,
                        {"farm_percentage":land_BECCS/100})

# Livestock farming practices        
food_system.add_step(agroecology_model,
                        {"land_percentage":silvopasture/100.,
                        "agroecology_class":"Silvopasture",
                        "land_type":["Improved grassland", "Semi-natural grassland"],
                        "tree_coverage":agroecology_tree_coverage,
                        "replaced_items":[2731, 2732],
                        "new_items":2617,
                        "item_yield":1e2})

food_system.add_step(scale_impact,
                        {"items":[2731, 2732],
                        "scale_factor":1 - methane_ghg_factor*methane_inhibitor/100})

food_system.add_step(scale_production,
                        {"scale_factor":1-methane_prod_factor*methane_inhibitor/100,
                        "items":[2731, 2732]})

food_system.add_step(scale_impact,
                        {"items":[2731, 2732],
                        "scale_factor":1 - manure_ghg_factor*manure_management/100})

food_system.add_step(scale_production,
                        {"scale_factor":1-manure_prod_factor*manure_management/100,
                        "items":[2731, 2732]})

food_system.add_step(scale_impact,
                        {"items":[2731, 2732],
                        "scale_factor":1 - breeding_ghg_factor*animal_breeding/100})

food_system.add_step(scale_production,
                        {"scale_factor":1-breeding_prod_factor*animal_breeding/100,
                        "items":[2731, 2732]})

# Arable farming practices
food_system.add_step(agroecology_model,
                        {"land_percentage":agroforestry/100.,
                        "agroecology_class":"Agroforestry",
                        "land_type":["Arable"],
                        "tree_coverage":agroecology_tree_coverage,
                        "replaced_items":2511,
                        "new_items":2617,
                        "item_yield":1e2})

food_system.add_step(scale_impact,
                        {"item_origin":"Vegetal Products",
                        "scale_factor":1 - fossil_arable_ghg_factor*fossil_arable/100})

food_system.add_step(scale_production,
                        {"scale_factor":1 - fossil_arable_prod_factor*fossil_arable/100,
                        "item_origin":"Vegetal Products"})

# Technology & Innovation    
food_system.add_step(ccs_model,
                        {"waste_BECCS":waste_BECCS*1e6,
                        "overseas_BECCS":overseas_BECCS*1e6,
                        "DACCS":DACCS*1e6})


# Compute emissions and sequestration
food_system.add_step(forest_sequestration_model,
                        {"seq_broadleaf_ha_yr":st.session_state.bdleaf_seq_ha_yr,
                        "seq_coniferous_ha_yr":st.session_state.conif_seq_ha_yr})

food_system.add_step(compute_emissions)

food_system.run()

datablock = food_system.datablock

# -------------------
# Execute plots block
# -------------------
from plots import plots
metric_yr = plots(datablock)
