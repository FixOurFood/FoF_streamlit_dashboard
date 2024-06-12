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

if "datablock_baseline" not in st.session_state:
    st.session_state["datablock_baseline"] = datablock

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

    st.markdown("# AgriFood Calculator")
    st.markdown('''<div style="text-align: justify;">
            Move the ambition level sliders to explore the outcomes of
            different interventions on key metrics of the food system,
            including GHG emissions, sequestration and land uses.
            </div>''', unsafe_allow_html=True)
    st.write("")

    col1, col2 = st.columns([7.5,2.5])
    with col1:
        st.selectbox("Scenario", scenarios_dict.keys(),
                     help=help["sidebar_consumer"][8],
                     on_change=call_scenarios, key="scenario")

    with col2:
        st.button("Reset \n sliders", on_click=reset_sliders,
                  key='reset_all')

    # Consumer demand interventions

    # st.slider("Consumer demand interventions", min_value=0., max_value=4., step=1.,
    #           value=0., key="consumer_bar", label_visibility="collapsed", format="%.1f")
    # consumer_progress_dict = {"bar_key":"consumer_bar",
    #                           "bar_values":consumer_slider_keys}

    with st.expander("**:spaghetti: Consumer demand**", expanded=False):

        consumer_slider_keys = ["d1", "d2", "d3", "d4", "d5", "d6", "d7"]

        ruminant = st.slider('Reduce ruminant meat consumption',
                        min_value=0, max_value=100, step=25,
                        key="d1", help=help["sidebar_consumer"][1])
        
        dairy = st.slider('[Reduce dairy consumption](https://docs.google.com/document/d/1A2J4BYIuXMgrj9tuLtIon8oJTuR1puK91bbUYCI8kHY/edit#heading=h.z0gjphyzstcl)',
                        min_value=0, max_value=100, step=25,
                        key="d2", help=help["sidebar_consumer"][2])
        
        pig_poultry_eggs = st.slider('Reduce pig, poultry and eggs consumption',
                        min_value=0, max_value=100, step=25,
                        key="d3", help=help["sidebar_consumer"][3])
        
        fruit_veg = st.slider('Increase fruit and vegetable consumption',
                        min_value=0, max_value=100, step=25,
                        key="d4", help=help["sidebar_consumer"][4])
        
        cereals = st.slider('Increase cereal consumption',
                        min_value=0, max_value=100, step=25,
                        key="d5", help=help["sidebar_consumer"][5])

        waste = st.slider('Food waste and over-eating reduction',
                        min_value=0, max_value=100, step=25,
                        key="d6", help=help["sidebar_consumer"][6])

        labmeat = st.slider('Increase cultured meat uptake',
                        min_value=0, max_value=100, step=25,
                        key="d7", help=help["sidebar_consumer"][7])       

        st.button("Reset", on_click=reset_sliders, key='reset_consumer',
                  kwargs={"keys": [consumer_slider_keys, "consumer_bar"]})

    # Land use change

    # st.slider("Consumer demand interventions", min_value=0., max_value=4., step=1.,
    #           value=0., key="land_bar", label_visibility="collapsed", format="%.1f")
    # land_progress_dict = {"bar_key":"land_bar",
    #                         "bar_values":land_slider_keys}

    with st.expander("**:earth_africa: Land use change**"):

        land_slider_keys = ["l1", "l2", "l3", "i3"]

        pasture_sparing = st.slider('Spared ALC 4 & 5 pasture land fraction',
                        min_value=0, max_value=100, step=25,
                        key='l1', help=help["sidebar_land"][0])        

        land_BECCS = st.slider('Percentage of farmland used for BECCS crops',
                        min_value=0, max_value=20, step=1,
                        key='i3', help=help["sidebar_innovation"][2])

        arable_sparing = st.slider('Spared ALC 4 & 5 arable land fraction',
                        min_value=0, max_value=100, step=25,
                        key='l2', help=help["sidebar_land"][1])

        foresting_spared = st.slider('Forested spared land fraction',
                        min_value=0, max_value=100, step=25,
                        key='l3', help=help["sidebar_land"][2])
        
        st.button("Reset", on_click=reset_sliders, key='reset_land',
                  kwargs={"keys":[land_slider_keys, "land_bar"]})
        
    # Livestock farming practices

    # st.slider("Livestock farming practices", min_value=0., max_value=4., step=1.,
    #           value=0., key="livestock_bar", label_visibility="collapsed", format="%.1f")
    # livestock_progress_dict = {"bar_key":"livestock_bar",
    #                             "bar_values":livestock_slider_keys}
    
    with st.expander("**:cow: Livestock farming practices**"):

        livestock_slider_keys = ["l4", "lf1", "lf2", "lf3", "lf4", "lf5"]
        
        silvopasture = st.slider('Pasture land % converted to silvopasture',
                        min_value=0, max_value=100, step=25,
                        key='l4', help=help["sidebar_land"][3])        
        
        methane_inhibitor = st.slider('Methane inhibitor use in livestock feed',
                        min_value=0, max_value=100, step=25,
                        key='lf1', help=help["sidebar_livestock"][0])
        
        manure_management = st.slider('Manure management in livestock farming',
                        min_value=0, max_value=100, step=25,
                        key='lf2', help=help["sidebar_livestock"][1])
        
        animal_breeding = st.slider('Livestock breeding',
                        min_value=0, max_value=100, step=25,
                        key='lf3', help=help["sidebar_livestock"][2])
        
        soil_carbon_management = st.slider('Soil and carbon management',
                        min_value=0, max_value=100, step=25,
                        key='lf4', help=help["sidebar_livestock"][3])
        
        fossil_livestock = st.slider('Fossil fuel use for heating, machinery',
                        min_value=0, max_value=100, step=25,
                        key='lf5', help=help["sidebar_livestock"][4])        
        

        st.button("Reset", on_click=reset_sliders, key='reset_livestock',
            kwargs={"keys": [livestock_slider_keys, "livestock_bar"]})

    # Arable farming practices

    # st.slider("Arable farming practices", min_value=0., max_value=4., step=1.,
    #           value=0., key="arable_bar", label_visibility="collapsed", format="%.1f")        
    # arable_progress_dict = {"bar_key":"arable_bar",
    #                             "bar_values":arable_slider_keys}

    with st.expander("**:ear_of_rice: Arable farming practices**"):

        arable_slider_keys = ["l5", "a1", "a2"]
        
        agroforestry = st.slider('Arable land % converted to agroforestry',
                        min_value=0, max_value=100, step=1,
                        key='l5', help=help["sidebar_land"][4])

        tillage = st.slider('Soil tillage reduction',
                        min_value=0, max_value=100, step=25,
                        key='a1', help=help["sidebar_arable"][0])
        
        fossil_arable = st.slider('Fossil fuel use for machinery',
                        min_value=0, max_value=100, step=25,
                        key='a2', help=help["sidebar_arable"][1])    
                        
        st.button("Reset", on_click=reset_sliders, key='reset_arable',
            kwargs={"keys": [arable_slider_keys, "arable_bar"]})        

    # Technology and innovation

    # st.slider("Consumer demand interventions", min_value=0., max_value=4., step=1.,
    #           value=0., key="innovation_bar", label_visibility="collapsed", format="%.1f")
    # technology_progress_dict = {"bar_key":"innovation_bar",
    #                             "bar_values":technology_slider_keys}
    
    with st.expander("**:gear: Technology and innovation**"):
        
        technology_slider_keys = ["i1", "i2", "i4"]

        waste_BECCS = st.slider('BECCS sequestration from waste \n [Mt CO2e / yr]',
                        min_value=0, max_value=100, step=1,
                        key='i1', help=help["sidebar_innovation"][0])

        overseas_BECCS = st.slider('BECCS sequestration from overseas biomass \n [Mt CO2e / yr]',
                        min_value=0, max_value=100, step=1,
                        key='i2', help=help["sidebar_innovation"][1])

        DACCS = st.slider('DACCS sequestration \n [Mt CO2e / yr]',
                        min_value=0, max_value=20, step=1,
                        key='i4', help=help["sidebar_innovation"][3])

        st.button("Reset", on_click=reset_sliders, key='reset_technology',
                  kwargs={"keys": [technology_slider_keys, "innovation_bar"]})
        
    # Advanced settings

    with st.expander("Advanced settings"):

        password = st.text_input("Enter the advanced settings password", type="password")
        if password == st.secrets["advanced_options_password"]:

            labmeat_co2e = st.slider('Cultured meat GHG emissions [g CO2e / g]', min_value=1., max_value=120., value=25., key='labmeat_slider')
            rda_kcal = st.slider('Recommended daily energy intake [kCal]', min_value=2000, max_value=2500, value=2250, key='rda_slider')
            n_scale = st.slider('Adoption timescale [years]', min_value=0, max_value=50, value=20, step=5, key='timescale_slider')
            max_ghge_animal = st.slider('Maximum animal production GHGE reduction due to innovation [%]', min_value=0, max_value=100, value=30, step=10, key = "max_ghg_animal", help = help["advanced_options"][3])
            max_ghge_plant = st.slider('Maximum plant production GHGE reduction due to innovation [%]', min_value=0, max_value=100, value=30, step=10, key = "max_ghg_plant", help = help["advanced_options"][4])
            bdleaf_conif_ratio = st.slider('Ratio of coniferous to broadleaved reforestation', min_value=0, max_value=100, value=50, step=10, key = "bdleaf_conif_ratio", help = help["advanced_options"][5])
            bdleaf_seq_ha_yr = st.slider('Broadleaved forest CO2 sequestration [t CO2 / ha / year]', min_value=7., max_value=15., value=12.5, step=0.5, key = "bdleaf_seq_ha_yr", help = help["advanced_options"][6])
            conif_seq_ha_yr = st.slider('Coniferous forest CO2 sequestration [t CO2 / ha / year]', min_value=15., max_value=30., value=23.5, step=0.5, key = "conif_seq_ha_yr", help = help["advanced_options"][7])
            elasticity = st.slider("Production / Imports elasticity ratio", min_value=0., max_value=1., value=1., step=0.1, key="elasticity", help = help["advanced_options"][9])
            agroecology_tree_coverage = st.slider("Tree coverage in agroecology", min_value=0., max_value=1., value=0.1, step=0.1, key="tree_coverage")
            
            tillage_prod_factor = st.slider("Soil tillage production reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="tillage_prod")
            tillage_ghg_factor = st.slider("Soil tillage GHG reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="tillage_ghg")

            manure_prod_factor = st.slider("Manure production reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="manure_prod")
            manure_ghg_factor = st.slider("Manure GHG reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="manure_ghg")

            breeding_prod_factor = st.slider("Breeding production reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="breeding_prod")
            breeding_ghg_factor = st.slider("Breeding GHG reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="breeding_ghg")

            methane_prod_factor = st.slider("Methane inhibitors production reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="methane_prod")
            methane_ghg_factor = st.slider("Methane inhibitors GHG reduction", min_value=0., max_value=1., value=0.3, step=0.1, key="methane_ghg")

            soil_management_ghg_factor = st.slider("Soil and carbon management GHG reduction", min_value=0., max_value=.2, value=0.05, step=0.01, key="soil_management_ghg")

            fossil_livestick_ghg_factor = st.slider("Livestock fossil fuel GHG reduction", min_value=0., max_value=.2, value=0.05, step=0.01, key="fossil_livestick_ghg")
            fossil_arable_ghg_factor = st.slider("Arable fossil fuel GHG reduction", min_value=0., max_value=.2, value=0.05, step=0.01, key="fossil_arable_ghg")
            
            scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                                        ('g/cap/day', 'g_prot/cap/day', 'g_fat/cap/day', 'kCal/cap/day'),
                                        horizontal=True,
                                        index=3,
                                        help=help["advanced_options"][9],
                                        key='nutrient_constant')
            
            st.button("Reset", on_click=update_slider,
                    kwargs={"values": [25, 2250, 20, 30, 30, 50, 12.5, 23.5, 0.1, "kCal/cap/day"],
                            "keys": ['labmeat_slider',
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

            labmeat_co2e = value=25
            rda_kcal = 2250
            n_scale = 20
            max_ghge_animal = 30
            max_ghge_plant = 30
            bdleaf_conif_ratio = 50
            bdleaf_seq_ha_yr = 12.5
            conif_seq_ha_yr = 23.5

            elasticity = 1
            agroecology_tree_coverage = 0.1

            tillage_prod_factor = 0.3
            tillage_ghg_factor = 0.3

            manure_prod_factor = 0.3
            manure_ghg_factor = 0.3

            breeding_prod_factor = 0.3
            breeding_ghg_factor = 0.3

            methane_prod_factor = 0.3
            methane_ghg_factor = 0.3

            soil_management_ghg_factor = 0.05

            fossil_livestick_ghg_factor = 0.05
            fossil_arable_ghg_factor = 0.05
            
            scaling_nutrient = 'kCal/cap/day'            

    st.markdown('''--- Developed with funding from [FixOurFood](https://fixourfood.org/).''')
    
    st.markdown('''--- We would be grateful for your feedback, via
                [this form](https://docs.google.com/forms/d/e/1FAIpQLSdnBp2Rmr-1fFYRQvEVcLLKchdlXZG4GakTBK5yy6jozUt8NQ/viewform?usp=sf_link).''')
    
    st.markdown('''--- For a list of references to the datasets used, please
                visit our [reference document](https://docs.google.com/spreadsheets/d/1XkOELCFKHTAywUGoJU6Mb0TjXESOv5BbR67j9UCMEgw/edit?usp=sharing).''')

col1, = st.columns(1)

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
    
    food_system.add_step(item_scaling,
                         {"scale":1-ruminant/100,
                          "items":[2731, 2732],
                          "source":["production", "imports"],
                          "elasticity":[elasticity, 1-elasticity],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(item_scaling,
                         {"scale":1-pig_poultry_eggs/100,
                          "items":[2733, 2734, 2949],
                          "source":["production", "imports"],
                          "elasticity":[elasticity, 1-elasticity],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(item_scaling,
                         {"scale":1-dairy/100,
                          "items":[2740, 2743, 2948],
                          "source":["production", "imports"],
                          "elasticity":[elasticity, 1-elasticity],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(item_scaling,
                         {"scale":1+fruit_veg/100,
                          "item_group":["Vegetables", "Fruits - Excluding Wine"],
                          "source":["production", "imports"],
                          "elasticity":[elasticity, 1-elasticity],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(item_scaling,
                         {"scale":1+cereals/100,
                          "item_group":["Cereals - Excluding Beer"],
                          "source":["production", "imports"],
                          "elasticity":[elasticity, 1-elasticity],
                          "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(food_waste_model,
                         {"waste_scale":waste,
                          "kcal_rda":rda_kcal,
                          "source":"imports"})

    food_system.add_step(cultured_meat_model,
                         {"cultured_scale":labmeat/100,
                          "labmeat_co2e":labmeat_co2e,
                          "source":"production"})
    
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
                         {"items":[2731],
                          "scale_factor":1 - methane_ghg_factor*methane_inhibitor/100})
    
    food_system.add_step(item_scaling,
                        {"scale":1-methane_prod_factor*methane_inhibitor/100,
                        "items":[2731],
                        "source":["production", "imports"],
                        "elasticity":[elasticity, 1-elasticity],
                        "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(scale_impact,
                         {"items":[2731],
                          "scale_factor":1 - manure_ghg_factor*manure_management/100})
    
    food_system.add_step(item_scaling,
                        {"scale":1-manure_prod_factor*manure_management/100,
                        "items":[2731],
                        "source":["production", "imports"],
                        "elasticity":[elasticity, 1-elasticity],
                        "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(scale_impact,
                         {"items":[2731],
                          "scale_factor":1 - breeding_ghg_factor*animal_breeding/100})
    
    food_system.add_step(item_scaling,
                        {"scale":1-breeding_prod_factor*animal_breeding/100,
                        "items":[2731],
                        "source":["production", "imports"],
                        "elasticity":[elasticity, 1-elasticity],
                        "scaling_nutrient":scaling_nutrient})    
    
    food_system.add_step(scale_impact,
                         {"items":[2731],
                          "scale_factor":1 - soil_management_ghg_factor*soil_carbon_management/100})

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
                          "scale_factor":1 - tillage_ghg_factor*tillage/100})
    
    food_system.add_step(item_scaling,
                        {"scale":1-tillage_prod_factor*tillage/100,
                        "item_group":"Vegetal Products",
                        "source":["production", "imports"],
                        "elasticity":[elasticity, 1-elasticity],
                        "scaling_nutrient":scaling_nutrient})
    
    food_system.add_step(scale_impact,
                         {"item_origin":"Vegetal Products",
                          "scale_factor":1 - fossil_arable_ghg_factor*fossil_arable/100})
    
    # Technology & Innovation    
    food_system.add_step(ccs_model,
                         {"waste_BECCS":waste_BECCS*1e6,
                          "overseas_BECCS":overseas_BECCS*1e6,
                          "DACCS":DACCS*1e6})

    
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

    with bottom():
        from bottom import bottom_panel
        bottom_panel(datablock, metric_yr)

# with col2:
#     # ---------------------
#     # Execute Metrics block
#     # ---------------------
#     from metrics import metrics
#     metrics(datablock, metric_yr)
