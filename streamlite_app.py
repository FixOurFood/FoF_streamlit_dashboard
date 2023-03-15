import streamlit as st

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import colors

import altair as alt
import numpy as np
import xarray as xr
from millify import millify
import copy

import custom_widgets as cw
from glossary import *
from afp_config import *
from altair_plots import *
from help_text import *

import fair

from agrifoodpy.food.food_supply import scale_food, scale_element, SSR


# FAIR wrapper, needed for caching
@st.cache_data
def FAIR_run(emissions_gtco2e):
    C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
    return C, F, T

# Helper Functions

# Updates the value of the sliders by setting the session state
def update_slider(keys, values):
    for key, value in zip(keys, values):
        st.session_state[key] = value

# Initialize session state with sliders in initial positions to recover later
for key in ["d1", "d2", "l1", "l2", "l3"]:
    if key not in st.session_state:
        st.session_state[key] = 0

if 'd3' not in st.session_state:
        st.session_state['d3'] = []

# return a logistic function between the input ranges with given k, x0
def logistic(k, x0, xmin, xmax):
    return 1 / (1 + np.exp(-k*(np.arange(xmax-xmin) - x0)))

# Function to scale an element and then add the difference to another element
def scale_add(food, element_in, element_out, scale, items=None):

    out = scale_element(food, element_in, scale, items)
    dif = food[element_in].fillna(0) - out[element_in].fillna(0)
    out[element_out] += dif

    return out

# function to return the coordinate index of the maximum value along a dimension
def map_max(map, dim):

    length_dim = len(map[dim].values)
    map_fixed = map.assign_coords({dim:np.arange(length_dim)})

    return map_fixed.idxmax(dim=dim, skipna=True)

# GUI
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

T = None

with st.sidebar:
    # Dietary interventions

    with st.expander("**:spaghetti: Dietary interventions**"):

        scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                            ('Weight', 'Proteins', 'Fat', 'Energy'), horizontal=True, index=3, help="casa")

        ruminant = cw.label_plus_slider('Reduce ruminant meat consumption',
                                        min=0, max=100, step=25,
                                        ratio=(6,4),
                                        key="d1")

        meatfree = cw.label_plus_slider('Number of meat free days a week',
                                        min=0, max=7, step=1,
                                        ratio=(6,4),
                                        key="d2")

        extra_items = cw.label_plus_multiselect('Also exclude from meat free days',
                                        options=['Egg', 'FishSeafood', 'Dairy'],
                                        key='d3')

        st.button("Reset", on_click=update_slider, kwargs={"values": [0, 0, []], "keys": ['d1', 'd2', 'd3']}, key='reset_d')


    # Farming and Prodction interventions
    with st.expander("**:earth_africa: Land use and farming interventions**"):

        # manure = cw.label_plus_slider('Improve manure treatment', 0, 4, 0, ratio=(6,4))
        # breeding = cw.label_plus_slider('Improve breeding', 0, 4, 0, ratio=(6,4))
        # feed_composition = cw.label_plus_slider('Improve stock feed composition', 0, 4, 0, ratio=(6,4))
        # grazing_feedlot = cw.label_plus_slider('Grazing versus feedlot', 0, 4, 0, ratio=(6,4))
        # calves_dairy = cw.label_plus_slider('Use calves from dairy herd', 0, 4, 0, ratio=(6,4))

        pasture_sparing = cw.label_plus_slider('Spared ALC 4 & 5 pasture land fraction',
                                                 min=0, max=100, step=25,
                                                 ratio=(6,4), key='l1')

        arable_sparing = cw.label_plus_slider('Spared ALC 4 & 5 arable land fraction',
                                                min=0, max=100, step=25,
                                                ratio=(6,4), key='l2')

        foresting_spared = cw.label_plus_slider('Forested spared land fraction',
                                                min=0, max=100, step=25,
                                                ratio=(6,4), key='l3')

        st.button("Reset", on_click=update_slider, kwargs={"values": [0,0,0,0,0], "keys": ['l1', 'l2', 'l3']}, key='reset_l')
        # agroforestry = cw.label_plus_slider('Crop + tree replacement', 0, 4, 0, ratio=(6,4))

    # Policy interventions
    with st.expander("**:office: Policy interventions**"):
        st.write('Policy intervention sliders to be shown here')

    with st.expander("Advanced settings"):
        n_scale = st.slider('Adoption timescale [years]', min_value=0, max_value=5, value=2)
        co2_seq = st.slider('Forest CO2 sequestration [t CO2 / ha / year]', min_value=7., max_value=15., value=12.47)

    st.markdown('''--- Created by [FixOurFood](https://github.com/FixOurFood/).''')
    st.markdown('''--- For feedback, please fill [this form](https://docs.google.com/forms/d/e/1FAIpQLSdnBp2Rmr-1fFYRQvEVcLLKchdlXZG4GakTBK5yy6jozUt8NQ/viewform?usp=sf_link).''')


col1, col2 = st.columns((3,7))

with col2:
    # MAIN
    plot_key = st.selectbox("Figure to display", option_list)

    nutrient = baseline[scaling_nutrient]

    # scale food from ruminant slider
    scale_past_ruminant = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future_ruminant = xr.DataArray(data = 1-(ruminant/100)*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020), coords = {"Year":np.arange(2020,2101)})
    scale_ruminant = xr.concat([scale_past_ruminant, scale_future_ruminant], dim="Year")

    aux = scale_food(food=nutrient,
                         scale= scale_ruminant,
                         origin="imports",
                         items=groups["RuminantMeat"],
                         constant=True,
                         fallback="exports")

    # scale food from meatfree slider
    scale_past_meatfree = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future_meatfree = xr.DataArray(data = 1-(meatfree/7)*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020), coords = {"Year":np.arange(2020,2101)})
    scale_meatfree = xr.concat([scale_past_meatfree, scale_future_meatfree], dim="Year")

    # add extra items
    meatfree_items = np.concatenate((groups["RuminantMeat"], groups["OtherMeat"]))

    for item in extra_items:
        meatfree_items = np.concatenate((meatfree_items, groups[item]))

    aux = scale_food(food=aux,
                     scale= scale_meatfree,
                     origin="imports",
                     items=meatfree_items,
                     constant=True,
                     fallback="exports")

    # Compute spared and forested land from land use sliders
    scale_sparing_pasture = pasture_sparing/100*np.sum(crops_by_grade[3:5,1])/total_crops_pasture
    scale_sparing_arable = arable_sparing/100*np.sum(crops_by_grade[3:5,0])/total_crops_arable

    spared_land_area_pasture = np.sum(crops_by_grade[3:5,1])*pasture_sparing/100
    spared_land_area_arable= np.sum(crops_by_grade[3:5,0])*arable_sparing/100

    spared_land_area = spared_land_area_arable + spared_land_area_pasture

    forested_spared_land_area = spared_land_area * foresting_spared / 100

    co2_seq_arable = spared_land_area_arable * foresting_spared / 100 * co2_seq
    co2_seq_pasture = spared_land_area_pasture * foresting_spared / 100 * co2_seq
    co2_seq_total = forested_spared_land_area * co2_seq

    # scale pasture from scale_sparing_pasture slider
    scale_past_pasture = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future_pasture = xr.DataArray(data = 1-(scale_sparing_pasture)*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020), coords = {"Year":np.arange(2020,2101)})
    scale_pasture = xr.concat([scale_past_pasture, scale_future_pasture], dim="Year")

    # scale pasture from scale_sparing_pasture slider
    scale_past_arable = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future_arable = xr.DataArray(data = 1-(scale_sparing_arable)*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020), coords = {"Year":np.arange(2020,2101)})
    scale_arable = xr.concat([scale_past_arable, scale_future_arable], dim="Year")

    aux = scale_add(food=aux,
                    element_in="production",
                    element_out="imports",
                    items=animal_items,
                    scale = scale_pasture)

    aux = scale_add(food=aux,
                    element_in="production",
                    element_out="imports",
                    items=plant_items,
                    scale = scale_arable)

    # compute new scaled values (make sure NaN are set to 1 to avoid issues)
    scaling = aux / nutrient
    scaling = scaling.where(np.isfinite(scaling), other=1.0)

    food_cap_day = food_cap_day_baseline * scaling
    kcal_cap_day = kcal_cap_day_baseline * scaling
    prot_cap_day = prot_cap_day_baseline * scaling
    fats_cap_day = fats_cap_day_baseline * scaling

    co2e_year = co2e_year_baseline * scaling
    co2e_cap_day = co2e_cap_day_baseline * scaling

    scaled_cap_day = {"Weight":food_cap_day,
                      "Emissions":co2e_cap_day,
                      "Energy":kcal_cap_day,
                      "Proteins":prot_cap_day,
                      "Fat":fats_cap_day}
    
    # # Adjust the total emissions by subtracting sequestration

    # seq_scaling = co2_seq_arable

    # co2e_year.loc[{"Item":co2e_year["Item_origin"]=="Vegetal Products"}] *= 

    # Adjust the total areas in each pixel

    scaled_CEH_pasture_arable = CEH_pasture_arable.copy(deep=True)
    scaled_CEH_pasture_arable.loc[{"use":"woodland"}] += CEH_pasture_arable.loc[{"use":"pasture"}] * pasture_sparing/100 * np.isin(ALC.grade, [4,5])
    scaled_CEH_pasture_arable.loc[{"use":"woodland"}] += CEH_pasture_arable.loc[{"use":"arable"}] * arable_sparing/100 * np.isin(ALC.grade, [4,5])
    scaled_CEH_pasture_arable.loc[{"use":"pasture"}] -= CEH_pasture_arable.loc[{"use":"pasture"}] * pasture_sparing/100 * np.isin(ALC.grade, [4,5])
    scaled_CEH_pasture_arable.loc[{"use":"arable"}] -= CEH_pasture_arable.loc[{"use":"arable"}] * arable_sparing/100 * np.isin(ALC.grade, [4,5])
        
    # Plot
    c = None
    f, plot1 = plt.subplots(1, figsize=(5,5))

    total_emissions_gtco2e = (co2e_year["food"]*scaling["food"] * pop_world / pop_uk).sum(dim="Item").to_numpy()/1e15
    # C, F, T = fair.forward.fair_scm(, useMultigas=False)
    C, F, T = FAIR_run(total_emissions_gtco2e)
    
    if plot_key == "CO2e emission per food group":

        # For some reason, xarray does not preserves the coordinates dtypes.
        # Here, we manually assign them to strings again to allow grouping by Non-dimension coordinate strigns
        co2e_year.Item_group.values = np.array(co2e_year.Item_group.values, dtype=str)
        co2e_year_groups = co2e_year.groupby("Item_group").sum().rename({"Item_group":"Item"})
        c_groups = plot_years_altair(co2e_year_groups["food"]/1e6, show="Item")
        c_baseline = plot_years_total(co2e_year_baseline["food"]/1e6)
        c = c_groups + c_baseline

    elif plot_key == "CO2e emission per food item":

        option_key = st.selectbox("Plot options", group_names)
        # Can't index by alternative coordinate name, use xr.where instead and squeeze
        co2e_year_item = co2e_year.sel(Item=co2e_year["Item_group"] == option_key).squeeze()
        c_items = plot_years_altair(co2e_year_item["food"]/1e6, show="Item_name")

        co2e_year_item_baseline = co2e_year_baseline.sel(Item=co2e_year_baseline["Item_group"] == option_key).squeeze()
        c_baseline = plot_years_total(co2e_year_item_baseline["food"]/1e6)
        c=c_items + c_baseline

    # elif plot_key == "CO2e concentration":
    #
    #     # Compute emissions using FAIR
    #     plot1.plot(co2e_year.Year.values, C_base, c = 'r')
    #     plot1.plot(co2e_year.Year.values, C, c = 'k')
    #     plot1.set_ylabel(r"$CO_2$ concentrations (PPM)")
    #
    #     col2_1, col2_2, col2_3 = st.columns((2,6,2))
    #     with col2_2:
    #         st.pyplot(fig=f)
    #
    # elif plot_key == "Radiative forcing":
    #
    #     # Compute emissions using FAIR
    #     plot1.plot(co2e_year.Year.values, F_base, c = 'r')
    #     plot1.plot(co2e_year.Year.values, F, c = 'k')
    #     plot1.set_ylabel(r"Total Radiative Forcing $(W/m^2)$")
    #
    #     col2_1, col2_2, col2_3 = st.columns((2,6,2))
    #     with col2_2:
    #         st.pyplot(fig=f)

    elif plot_key == "Temperature anomaly":

        # Compute emissions using FAIR
        plot1.plot(co2e_year.Year.values, T_base, c = 'r')
        plot1.plot(co2e_year.Year.values, T, c = 'k')
        plot1.set_ylabel(r"Temperature anomaly (K)")

        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            st.pyplot(fig=f)

    elif plot_key == "Per capita daily values":
        option_key = st.selectbox("Plot options", list(baseline.keys()))

        bar_plot_array = scaled_cap_day[option_key]
        bar_plot_array.Item_origin.values = np.array(bar_plot_array.Item_origin.values, dtype=str)
        bar_plot_array_groups = bar_plot_array.groupby("Item_origin").sum().rename({"Item_origin":"Item"})

        c = plot_bars_altair(bar_plot_array_groups.sel(Year=2100), show="Item", xlimit = bar_plot_limits[option_key], x_axis_title = x_axis_title[option_key])

    elif plot_key == "Self-sufficiency ratio":

        SSR_scaled = SSR(food_cap_day) 

        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            plot1.plot(SSR_scaled)
            plot1.set_ylim(0,1)
            st.pyplot(fig=f)
        

    elif plot_key == "Land Use":
        col_opt1, col_opt2 = st.columns((1,1))

        with col_opt1:
            option_key = st.selectbox("Plot options", land_options)

        if option_key == "Agricultural Land Classification":
            plot1.imshow(ALC_ag_only.grade.T,
                         interpolation="none",
                         origin="lower",
                         cmap = "RdYlGn_r")

        elif option_key == "Land use":
            map_toplot = map_max(scaled_CEH_pasture_arable.area, dim="use")
            # assign 3 to urban areas
            map_toplot = map_toplot.where(ALC.grade!=7, other=3)

            #             arable   pasture  woodland   urban    
            color_list = ['yellow', 'orange', 'green', 'black']
            labels = ["arable", "pasture", "woodland", "urban"]
            cmap = colors.ListedColormap(color_list)
            patches = [ mpatches.Patch(color=color_list[l], label=labels[l] ) for l in range(4) ]
            plot1.imshow(map_toplot.T, interpolation='none', origin='lower', cmap=cmap)
            # get the colors of the values, according to the 
            # create a patch (proxy artist) for every color 
            # put those patched as legend-handles into the legend
            plot1.legend(handles=patches, bbox_to_anchor=(0.8, 0.9), loc=2, borderaxespad=0.)

        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            plot1.axis("off")
            st.pyplot(fig=f)

        # c = plot_land_altair(ALC)

    if c is not None:
        st.altair_chart(altair_chart=c, use_container_width=True)

with col1:
    # MAIN
    st.metric(label="**:thermometer: Temperature rise by 2100 caused by food consumed in the UK**",
              value="{:.2f} °C".format(T[-1]),
              delta="{:.2f} °C - Compared to BAU".format(T[-1]-T_base[-1]), delta_color="inverse",
              help=temperature_rise_help)

    st.metric(label="**:sunrise_over_mountains: Total area of spared land**",
              value=f"{millify(spared_land_area, precision=2)} ha",
              help=spared_land_help)

    st.metric(label="**:deciduous_tree: Total area of forested land**",
              value=f"{millify(forested_spared_land_area, precision=2)} ha",
              help=forested_land_help)

    st.metric(label="**:chart_with_downwards_trend: Total carbon sequestration by forested land**",
              value=f"{millify(co2_seq_total, precision=2)} t CO2/yr",
              help=sequestered_carbon_help)
