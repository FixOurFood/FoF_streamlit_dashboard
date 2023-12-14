import streamlit as st
from streamlit_modal import Modal

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import colors, cm

import altair as alt
import numpy as np
import xarray as xr
from millify import millify
import pandas as pd

import custom_widgets as cw
from glossary import *
from afp_config import *
from altair_plots import *
from fair_config import set_fair_base

from helper_functions import *
from model import *
from scenarios import call_scenarios, scenarios_dict

from agrifoodpy.food.food_supply import scale_food, scale_element, SSR

def change_labmeat_co2e():
    co2e_g.loc[{"Item":5000}] = st.session_state.labmeat_slider

# ------------------------
# Help and tooltip strings
# ------------------------
help = pd.read_csv(st.secrets["tooltips_url"], dtype='string')

# GUI
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

T = None

with st.sidebar:

    # st.image("images/fof_logo.png")
    st.markdown("# AgriFood Calculator")

    col1, col2 = st.columns([7.5,2.5])
    with col1:
        st.selectbox("Scenario", scenarios_dict.keys(), help=help["sidebar_consumer"][8], on_change=call_scenarios, key="scenario")

    with col2:
        st.button("Reset \n sliders", on_click=reset_all_sliders, key='reset_all')

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

        extra_items = cw.label_plus_multiselect('Also exclude from meat free days',
                                        options=['Egg', 'FishSeafood', 'Dairy'],
                                        key='d3', help=help["sidebar_consumer"][3])

        # waste = cw.label_plus_slider('Food waste and over-eating reduction', ratio=(6,4),
        waste = st.slider('Food waste and over-eating reduction',
                                        min_value=0, max_value=100, step=25,
                                        key="d4", help=help["sidebar_consumer"][4])

        # labmeat = cw.label_plus_slider('Increase labmeat uptake', ratio=(6,4),
        labmeat = st.slider('Increase cultured meat uptake',
                                        min_value=0, max_value=100, step=25,
                                        key="d5", help=help["sidebar_consumer"][6])
       

        extra_items_cultured_string = cw.label_plus_multiselect('Also replace with cultured meat',
                                        options=['Poultry Meat', 'Pigmeat'],
                                        key='d6', help=help["sidebar_consumer"][7])


        st.button("Reset", on_click=update_slider, kwargs={"values": [0, 0, [], 0, 0], "keys": ['d1', 'd2', 'd3', 'd4', 'd5']}, key='reset_d')

    # Land management interventions
    with st.expander("**:earth_africa: Land management**"):

        # manure = cw.label_plus_slider('Improve manure treatment', 0, 4, 0, ratio=(6,4))
        # breeding = cw.label_plus_slider('Improve breeding', 0, 4, 0, ratio=(6,4))
        # feed_composition = cw.label_plus_slider('Improve stock feed composition', 0, 4, 0, ratio=(6,4))
        # grazing_feedlot = cw.label_plus_slider('Grazing versus feedlot', 0, 4, 0, ratio=(6,4))
        # calves_dairy = cw.label_plus_slider('Use calves from dairy herd', 0, 4, 0, ratio=(6,4))

        # pasture_sparing = cw.label_plus_slider('Spared ALC 4 & 5 pasture land fraction',ratio=(6,4),
        pasture_sparing = st.slider('Spared ALC 4 & 5 pasture land fraction',
                                                min_value=0, max_value=100, step=25,
                                                key='l1', help=help["sidebar_land"][0])

        # arable_sparing = cw.label_plus_slider('Spared ALC 4 & 5 arable land fraction',ratio=(6,4),
        arable_sparing = st.slider('Spared ALC 4 & 5 arable land fraction',
                                                min_value=0, max_value=100, step=25,
                                                key='l2', help=help["sidebar_land"][1])

        # foresting_spared = cw.label_plus_slider('Forested spared land fraction',ratio=(6,4),
        foresting_spared = st.slider('Forested spared land fraction',
                                                min_value=0, max_value=100, step=25,
                                                key='l3', help=help["sidebar_land"][2])

        
        # foresting_spared = cw.label_plus_slider('Forested spared land fraction',ratio=(6,4),
        silvopasture = st.slider('Farmland % converted to silvopasture',
                                                min_value=0, max_value=100, step=25,
                                                key='l4', help=help["sidebar_land"][3])
        

        # agroforestry_spared = cw.label_plus_slider('Forested spared land fraction',ratio=(6,4),
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

        st.button("Reset", on_click=update_slider, kwargs={"values": [0,0,0,0,0,0], "keys": ['l1', 'l2', 'l3', 'l4', 'l5']}, key='reset_l')
        # agroforestry = cw.label_plus_slider('Crop + tree replacement', 0, 4, 0, ratio=(6,4))

    # Technology and innovation
    with st.expander("**:gear: Technology and innovation**"):

        # waste_BECCS = cw.label_plus_slider('BECCS sequestration from waste', ratio=(6,4),
        waste_BECCS = st.slider('BECCS sequestration from waste \n [Mt CO2e / yr]',
                                                min_value=0, max_value=100, step=1,
                                                key='i1', help=help["sidebar_innovation"][0])


        # overseas_BECCS = cw.label_plus_slider('BECCS sequestration from overseas biomass', ratio=(6,4),
        overseas_BECCS = st.slider('BECCS sequestration from overseas biomass \n [Mt CO2e / yr]',
                                                min_value=0, max_value=100, step=1,
                                                key='i2', help=help["sidebar_innovation"][1])


        # land_BECCS = cw.label_plus_slider('Percentage of farmland for BECCS', ratio=(6,4),
        land_BECCS = st.slider('Percentage of farmland used for BECCS crops',
                                                min_value=0, max_value=20, step=1,
                                                key='i3', help=help["sidebar_innovation"][2])


        # DACCS = cw.label_plus_slider('DACCS sequestration', ratio=(6,4),
        DACCS = st.slider('DACCS sequestration \n [Mt CO2e / yr]',
                                                min_value=0, max_value=20, step=1,
                                                key='i4', help=help["sidebar_innovation"][3])

        # labmeat_innovation = cw.label_plus_slider('Lab meat production innovation', ratio=(6,4),
        # labmeat_innovation = st.slider('Lab meat production innovation',
        #                                         min_value=0, max_value=4, step=1,
        #                                         key='i2', help=help["sidebar_innovation"][1])

        # # agg_innovation = cw.label_plus_slider('Inovation to improve aggricultural yield', ratio=(6,4),
        # agg_innovation = st.slider('Inovation to improve aggricultural yield',
        #                                         min_value=0, max_value=100, step=25,
        #                                         key='i3', help=help["sidebar_innovation"][2])
       
        # incr_GHGE_innovation_crops = cw.label_plus_slider('Incremental crop GHGE innovation', ratio=(6,4),
        incr_GHGE_innovation_crop = st.slider('Plant production GHGE innovation',
                                                min_value=0, max_value=4, step=1,
                                                key='i5', help=help["sidebar_innovation"][4])

        # incr_GHGE_innovation_meat = cw.label_plus_slider('Incremental meat GHGE innovation', ratio=(6,4),
        incr_GHGE_innovation_meat = st.slider('Animal production GHGE innovation',
                                                min_value=0, max_value=4, step=1,
                                                key='i6', help=help["sidebar_innovation"][5])

        # # radc_GHGE_innovation = cw.label_plus_slider('Radical GHGE innovation', ratio=(6,4),
        # radc_GHGE_innovation = st.slider('Radical GHGE innovation',
        #                                         min_value=0, max_value=100, step=25,
        #                                         key='i6', help=help["sidebar_innovation"][5])
       
        st.button("Reset", on_click=update_slider, kwargs={"values": [0,0,0,0,0,0], "keys": ['i1', 'i2', 'i3', 'i4', 'i5', 'i6']}, key='reset_i')

    # Policy interventions
    #with st.expander("**:office: Policy interventions**"):
    #    st.write('Policy intervention sliders to be shown here')

    with st.expander("Advanced settings"):

        labmeat_co2e = st.slider('Cultured meat GHG emissions [g CO2e / g]', min_value=1., max_value=120., value=25., key='labmeat_slider', on_change=change_labmeat_co2e)
        rda_kcal = st.slider('Recommended daily energy intake [kCal]', min_value=2000, max_value=2500, value=2250)
        n_scale = st.slider('Adoption timescale [years]', min_value=0, max_value=4, value=2)
        co2_seq = st.slider('Forest CO2 sequestration [t CO2 / ha / year]', min_value=7., max_value=15., value=12.47)
        max_ghge_animal = st.slider('Maximum animal production GHGE reduction due to innovation [%]', min_value=0, max_value=100, value=30, step=10, key = "max_ghg_animal", help = help["advanced_options"][3])
        max_ghge_plant = st.slider('Maximum plant production GHGE reduction due to innovation [%]', min_value=0, max_value=100, value=30, step=10, key = "max_ghg_plant", help = help["advanced_options"][4])
        scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                                    ('Weight', 'Proteins', 'Fat', 'Energy'), horizontal=True, index=3, help=help["sidebar_consumer"][0])


    st.markdown('''--- Developed with funding from [FixOurFood](https://fixourfood.org/).''')
    st.markdown('''--- We would be grateful for your feedback, via [this form](https://docs.google.com/forms/d/e/1FAIpQLSdnBp2Rmr-1fFYRQvEVcLLKchdlXZG4GakTBK5yy6jozUt8NQ/viewform?usp=sf_link).''')

    modal = Modal(
        "Data sources", 
        key="data_sources",
    
        # Optional
        padding=20,    # default value
        max_width=900  # default value
    )
    open_modal = st.button("View data sources")
    if open_modal:
        modal.open()

col1, col2 = st.columns((7,3))

with col1:
    # MAIN

    if modal.is_open():
        with modal.container():
            st.markdown(
"""The agrifood calculator uses a series of datasets to
construct a baseline food system based on recent trends of
consumption, population, estimates on the impact of food,
land use and agricultural land classification.
This is a list of the datasets currently used in this
calculator, and their origins.
                        
| **Dataset**                 | **Description**                                                                    | **Origin**                                                                                                         |
|-----------------------------|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| FAOSTAT Food balance sheets | Production, imports, exports and detailed domestic use, per region, year and item  | FAOSTAT https://www.fao.org/faostat/en/#data/FBS                                                                   |
| UN Population estimates     | Past estimates and future population projections per region and year               | UN World Population Prospects https://population.un.org/wpp/                                                       |
| Poore and Nemecek LCA data  | Emissions and other impacts of food items                                          | Poore & Nemecek (2018) https://www.science.org/doi/10.1126/science.aaq0216                                         |
| UKCEH Land cover map        | Land classification and land use maps                                              | UK CEH Land cover maps https://www.ceh.ac.uk/data/ukceh-land-cover-maps                                            |
| Natural England ALC         | England agricultural land classification maps                                      | Natural England https://naturalengland-defra.opendata.arcgis.com/ |

For detailed information on how these datasets are used,
please visit our modelling document.
""")

    plot_key = st.selectbox("Figure to display", option_list)

    nutrient = baseline[scaling_nutrient]

    # scale food from ruminant slider
    aux = ruminant_consumption_model(nutrient, ruminant, n_scale)

    # scale food from meatfree slider
    aux = meatfree_consumption_model(aux, meatfree, extra_items, n_scale)

    # LAND USE MODEL 
    scaled_LC_type = LC_type.copy(deep=True)

    # ***sequestered_carbon_model***
    co2_seq_arable_arr, co2_seq_pasture_arr, co2_seq_total_arr, spared_land_area_arr = sequestered_carbon_model(pasture_sparing,
                                                                              arable_sparing,
                                                                              foresting_spared,
                                                                              co2_seq, n_scale)
    
    sequestration_ds = xr.Dataset({"Forested arable land":co2_seq_arable_arr, "Forested pasture land":co2_seq_pasture_arr})
    
    aux, sequestration_ds = engineered_sequestration_model(aux, sequestration_ds, waste_BECCS, overseas_BECCS, land_BECCS, DACCS, n_scale)

    sequestration_ds = xr.concat([sequestration_ds[var] for var in sequestration_ds.data_vars], dim="Item")
    sequestration_ds = sequestration_ds.assign_coords({"Item":["Forested arable land",
                                                               "Forested pasture land",
                                                               "BECCS from waste",
                                                               "BECCS from overseas",
                                                               "DACCS"]})
    sequestration_ds = sequestration_ds * -1
    
    co2_seq_arable = co2_seq_arable_arr.isel(Year=-1)
    co2_seq_pasture = co2_seq_pasture_arr.isel(Year=-1)
    co2_seq_total = co2_seq_total_arr.isel(Year=-1)
    spared_land_area = spared_land_area_arr.isel(Year=-1)

    co2_seq_engineered_total = sequestration_ds.sel(Item="BECCS from waste", Year=2100) + \
                               sequestration_ds.sel(Item="BECCS from overseas", Year=2100) + \
                               sequestration_ds.sel(Item="DACCS", Year=2100)
    

    # Compute spared and forested land from land use sliders
    # scale pasture from scale_sparing_pasture slider
    scale_sparing_pasture = pasture_sparing/100*np.sum(use_by_grade[4:6,1])/total_crops_pasture
    scale_past_pasture = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future_pasture = xr.DataArray(data = 1-(scale_sparing_pasture)*logistic(n_scale), coords = {"Year":np.arange(2020,2101)})
    scale_pasture = xr.concat([scale_past_pasture, scale_future_pasture], dim="Year")
    aux = scale_add(food=aux,
                    element_in="production",
                    element_out="imports",
                    items=animal_items,
                    scale = scale_pasture)

    delta_spared_pasture = LC_type.loc[{"use":"grassland"}] * pasture_sparing/100 * np.isin(ALC.grade, [4,5])
    scaled_LC_type.loc[{"use":"spared"}] += delta_spared_pasture
    scaled_LC_type.loc[{"use":"grassland"}] -= delta_spared_pasture

    # scale arable from scale_sparing_arable slider
    scale_sparing_arable = arable_sparing/100*np.sum(use_by_grade[4:6,0])/total_crops_arable
    scale_past_arable = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future_arable = xr.DataArray(data = 1-(scale_sparing_arable)*logistic(n_scale), coords = {"Year":np.arange(2020,2101)})
    scale_arable = xr.concat([scale_past_arable, scale_future_arable], dim="Year")
    aux = scale_add(food=aux,
                    element_in="production",
                    element_out="imports",
                    items=plant_items,
                    scale = scale_arable)

    # # Adjust the total emissions by subtracting sequestration
    delta_spared_arable = LC_type.loc[{"use":"arable"}] * arable_sparing/100 * np.isin(ALC.grade, [4,5])
    scaled_LC_type.loc[{"use":"spared"}] += delta_spared_arable
    scaled_LC_type.loc[{"use":"arable"}] -= delta_spared_arable

    # ***forestation***
    scaled_LC_type = forested_land_model(scaled_LC_type, foresting_spared, [4,5])

    # ***engineered carbon capture***

    # compute new scaled values (make sure NaN are set to 1 to avoid issues)
    scaling = aux / nutrient
    scaling = scaling.where(np.isfinite(scaling), other=1.0)

    food_cap_day = food_cap_day_baseline * scaling
    kcal_cap_day = kcal_cap_day_baseline * scaling
    prot_cap_day = prot_cap_day_baseline * scaling
    fats_cap_day = fats_cap_day_baseline * scaling

    # Compute new consumption values without waste
    aux = food_waste_model(kcal_cap_day, waste, rda_kcal, n_scale)

    # compute new scaled values (make sure NaN are set to 1 to avoid issues)
    scaling = aux / kcal_cap_day
    scaling = scaling.where(np.isfinite(scaling), other=1.0)

    food_cap_day = food_cap_day * scaling
    kcal_cap_day = kcal_cap_day * scaling
    prot_cap_day = prot_cap_day * scaling
    fats_cap_day = fats_cap_day * scaling

    # Items to replace by cultured meat
    extra_items_cultured_dict = {
        "Pigmeat" : 2733,
        "Poultry Meat" : 2734
    }
    items_replaced_by_cultured = [2731]
    for item in extra_items_cultured_string:
        items_replaced_by_cultured.append(extra_items_cultured_dict[item])

    items_replaced_by_cultured = np.unique(items_replaced_by_cultured)

    food_cap_day = cultured_meat_uptake_model(food_cap_day, labmeat, n_scale, items_replaced_by_cultured)
    kcal_cap_day = cultured_meat_uptake_model(kcal_cap_day, labmeat, n_scale, items_replaced_by_cultured)
    prot_cap_day = cultured_meat_uptake_model(prot_cap_day, labmeat, n_scale, items_replaced_by_cultured)
    fats_cap_day = cultured_meat_uptake_model(fats_cap_day, labmeat, n_scale, items_replaced_by_cultured)

    # production ghge innovation
    co2e_g_scaled = ghge_innovation(co2e_g, max_ghge_plant*incr_GHGE_innovation_crop , plant_items, n_scale)
    co2e_g_scaled = ghge_innovation(co2e_g_scaled, max_ghge_animal*incr_GHGE_innovation_meat , animal_items, n_scale)

    # compute new emissions
    co2e_cap_day = food_cap_day * co2e_g_scaled
    co2e_year = co2e_cap_day * pop_uk * 365.25

    # Dictionary for menu
    scaled_cap_day = {"Weight":food_cap_day,
                      "Emissions":co2e_cap_day,
                      "Energy":kcal_cap_day,
                      "Proteins":prot_cap_day,
                      "Fat":fats_cap_day}
   
    # ----------------------------------------    
    #                  Plots
    # ----------------------------------------    
    
    c = None
    f, plot1 = plt.subplots(1, figsize=(7,7))

    total_emissions_gtco2e = (co2e_year["food"]*scaling["food"] * pop_world / pop_uk).sum(dim="Item").to_numpy()/1e15


    fair_run = set_fair_base()
    fair_run.emissions.loc[{"scenario":"afp", "specie":"CO2", "config":"defaults"}] = total_emissions_gtco2e + sequestration_ds.sum(dim="Item") * pop_world / pop_uk / 1e9
    fair_run.run(progress=False)
    
    T = fair_run.temperature.loc[dict(scenario='afp', layer=0)].values.squeeze()
    F = fair_run.forcing.loc[dict(scenario='afp', specie="CO2")].values.squeeze()
    C = fair_run.concentration.loc[dict(scenario='afp', specie="CO2")].values.squeeze()

    SSR_scaled = SSR(food_cap_day)

    if plot_key == "CO2e emission per food group":

        option_key = st.selectbox("Plot options", ["Food group", "Food origin"])

        # For some reason, xarray does not preserves the coordinates dtypes.
        # Here, we manually assign them to strings again to allow grouping by Non-dimension coordinate strigns
        co2e_year.Item_group.values = np.array(co2e_year.Item_group.values, dtype=str)
        co2e_year.Item_origin.values = np.array(co2e_year.Item_origin.values, dtype=str)
        
        if option_key == "Food group":
            co2e_year_groups = co2e_year.groupby("Item_group").sum().rename({"Item_group":"Item"})

        elif option_key == "Food origin":
            co2e_year_groups = co2e_year.groupby("Item_origin").sum().rename({"Item_origin":"Item"})
        
        c_groups = plot_years_altair(co2e_year_groups["food"]/1e6, show="Item", xlabel='CO2e emissions [t CO2e / year]')
        c_baseline = plot_years_total(co2e_year_baseline["food"]/1e6, xlabel='CO2e emissions [t CO2e / year]', sumdim="Item")
        c_sequestration = plot_years_altair(sequestration_ds, show="Item",xlabel='CO2e emissions [t CO2e / year]')


        line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule().encode(y='y')
        c = c_groups + c_baseline + c_sequestration + line

        c = c.configure_axis(
            labelFontSize=15,
            titleFontSize=15
        )

    elif plot_key == "CO2e emission per food item":

        option_key = st.selectbox("Plot options", group_names)
        # Can't index by alternative coordinate name, use xr.where instead and squeeze
        co2e_year_item = co2e_year.sel(Item=co2e_year["Item_group"] == option_key).squeeze()
        c_items = plot_years_altair(co2e_year_item["food"]/1e6, show="Item_name", xlabel='Consumed food CO2e emissions [t CO2e / year]')

        co2e_year_item_baseline = co2e_year_baseline.sel(Item=co2e_year_baseline["Item_group"] == option_key).squeeze()
        c_baseline = plot_years_total(co2e_year_item_baseline["food"]/1e6, xlabel='Consumed food CO2e emissions [t CO2e / year]', sumdim="Item")
        c=c_items + c_baseline

        c = c.configure_axis(
            labelFontSize=15,
            titleFontSize=15
        )

    elif plot_key == "Temperature anomaly":

        T_base_xr = xr.DataArray(data=T_base-T_base[-80],
                                 dims=["Year"],
                                 coords={"Year":fair_run.timebounds.astype(int)})

        T_xr = xr.DataArray(data=T-T[-80],
                                 dims=["Year"],
                                 coords={"Year":fair_run.timebounds.astype(int)})
        
        
        c = plot_years_total(T_xr, xlabel="Atmosferic temperature warming [ºC]").mark_line(color='black')
        c = c + plot_years_total(T_base_xr, xlabel="Atmosferic temperature warming [ºC]")

        c = c.configure_axis(
            labelFontSize=15,
            titleFontSize=15
            )
        
        rules = alt.Chart(pd.DataFrame({
            'Year': [2020],
            'color': ['grey']
            })).mark_rule().encode(
            x='Year:T',
            color=alt.Color('color:N', scale=None)
        )
        
        c = c+rules


    elif plot_key == "Per capita daily values":
        option_key = st.selectbox("Plot options", list(baseline.keys()))

        bar_plot_array = scaled_cap_day[option_key]
        bar_plot_array.Item_origin.values = np.array(bar_plot_array.Item_origin.values, dtype=str)
        bar_plot_array_groups = bar_plot_array.groupby("Item_origin").sum().rename({"Item_origin":"Item"})

        c = plot_bars_altair(bar_plot_array_groups.sel(Year=2100), show="Item", xlimit = bar_plot_limits[option_key], x_axis_title = x_axis_title[option_key])

        if option_key == "Energy":

            c = c + alt.Chart(pd.DataFrame({
            'Energy': [rda_kcal],
            'color': ['red']
            })).mark_rule().encode(
            x='Energy:Q',
            color=alt.Color('color:N', scale=None)
            )
        
        c = c.configure_axis(
            labelFontSize=20,
            titleFontSize=20
        )

    elif plot_key == "Self-sufficiency ratio":

        c = plot_years_total(SSR_scaled, xlabel="SSR = Production / (Production + Imports - Exports)")
        c = c.configure_axis(
            labelFontSize=15,
            titleFontSize=15
            )

    elif plot_key == "Land Use":
        col_opt1, col_opt2 = st.columns((1,1))

        with col_opt1:
            option_key = st.selectbox("Plot options", land_options)

        if option_key == "Agricultural Land Classification":

            grades = np.unique(ALC_ag_only.grade)
            grades = grades[~np.isnan(grades)]

            cmap = cm.get_cmap('RdYlGn_r')
            norm = colors.Normalize(vmin=1, vmax=5)
            color_list = [cmap(norm(val)) for val in grades]

            plot1.imshow(ALC_ag_only.grade,
                         interpolation="none",
                         origin="lower",
                         cmap = cmap)
                        #  cmap = "RdYlGn_r")
            
            patches = [mpatches.Patch(color=color_list[int(l-1)], label=f"ALC {int(l)}" ) for l in grades]
            # put those patched as legend-handles into the legend
            plot1.legend(handles=patches, loc=2, borderaxespad=0. )

        elif option_key == "Land use":

            map_toplot = map_max(scaled_LC_type, dim="use")
            map_values = np.arange(7)

            map_labels = ["Arable", "Grassland", "Mountain", "Urban", "Water", "Woodland", "Spared"]
            
            plot1.imshow(map_toplot, interpolation='none', origin='lower', cmap=cmap_tar, norm=norm_tar)
            patches = [mpatches.Patch(color=color_list[int(l)], label=map_labels[int(l)] ) for l in map_values]
            plot1.legend(handles=patches, loc=2, borderaxespad=0. )

        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            plot1.axis("off")
            st.pyplot(fig=f)

        # c = plot_land_altair(ALC)

    elif plot_key == "CO2 emissions per sector":

        width = 0.5
        labels = ["Emissions", "Reductions", "Sequestration"]
        plot1.bar(labels, [50, 25, 40] ,width, bottom = [0, 25, -15], color=["r", "g", "b"])
        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            st.pyplot(fig=f)

    if c is not None:
        st.altair_chart(altair_chart=c, use_container_width=True)

with col2:
    # MAIN

    st.write("## Metrics")

    # ----------------------------
    # Environment and biodiversity
    # ----------------------------
    with st.expander("Environment and biodiversity", expanded=True):
        st.metric(label="**:thermometer: Surface temperature warming by 2100**",
                value="{:.2f} °C".format(T[-1] - T[-80]),
                delta="{:.2f} °C - Compared to BAU".format((T[-1] - T[-80])-(T_base[-1] - T_base[-80])), delta_color="inverse",
                help=help["metrics"][0])
        st.metric(label="**:chart_with_downwards_trend: Total carbon sequestration by forested agricultural land**",
                value=f"{millify(co2_seq_total, precision=2)} t CO2/yr",
                help=help["metrics"][4])
        
        st.metric(label="**:chart_with_downwards_trend: Total carbon sequestration by engineered Carbon Capture and Storage**",
                value=f"{millify(-co2_seq_engineered_total, precision=2)} t CO2/yr",
                help=help["metrics"][3])
        
    # --------
    # Land use
    # --------
    with st.expander("Land use", expanded=True):
        st.metric(label="**:sunrise_over_mountains: Total area of agricultural spared land**",
                value=f"{millify(spared_land_area, precision=2)} ha",
                help=help["metrics"][2])

        st.metric(label="**:deciduous_tree: Total area of forested agricultural land**",
                value=f"{millify(co2_seq_total/co2_seq, precision=2)} ha",
                help=help["metrics"][3])

    # --------------
    # Socio-economic
    # --------------
    with st.expander("Socio-economic", expanded=True):
        st.metric(label="**:factory: Public spending on engineered greenhouse gas removal**",
                value="£100 billion",
                help=help["metrics"][5])
        
        st.metric(label="**:farmer: Public spending on farming subsidy**",
                value="£100 billion",
                help=help["metrics"][6])

    # ---------------
    # Food production
    # ---------------
    with st.expander("Food production", expanded=True):

        food_cap_day.Item_origin.values = np.array(food_cap_day.Item_origin.values, dtype=str)
        total_animal = food_cap_day["food"].groupby("Item_origin").sum().sel(Item_origin="Animal Products", Year=2100).to_numpy()

        food_cap_day_baseline.Item_origin.values = np.array(food_cap_day_baseline.Item_origin.values, dtype=str)
        total_animal_baseline = food_cap_day_baseline["food"].groupby("Item_origin").sum().sel(Item_origin="Animal Products", Year=2100).to_numpy()

        st.metric(label="**:factory: Change in animal origin food consumption**",
                value="{:.1f} %".format(100-100*total_animal/total_animal_baseline),
                help=help["metrics"][7])
        
        st.metric(label="**:bar_chart: Food Self-sufficiency ratio**",
                value="{:.2f} %".format(100*SSR_scaled.sel(Year=2050)),
                help=help["metrics"][8])