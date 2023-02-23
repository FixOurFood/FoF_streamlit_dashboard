import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import numpy as np
import xarray as xr

import custom_widgets as cw
from glossary import *
from afp_config import *

import fair
from fair.RCPs import rcp3pd, rcp45, rcp6, rcp85

from agrifoodpy.food.food_supply import FAOSTAT, Nutrients_FAOSTAT, scale_food, scale_element, plot_years, plot_bars
from altair_plots import *


# Helper Functions
def logistic(k, x0, xmax, xmin=0):
    return 1 / (1 + np.exp(-k*(np.arange(xmax-xmin) - x0)))

def scale_add(food, element_in, element_out, scale, items=None):

    out = scale_element(food, element_in, scale, items)
    dif = food[element_in].fillna(0) - out[element_in].fillna(0)
    out[element_out] += dif

    return out

# GUI
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with st.sidebar:
    # Dietary interventions
    # progress_dietary = st.progress(0)
    with st.expander("**Dietary interventions** :spaghetti:"):
        scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                            ('Weight', 'Proteins', 'Fat', 'Energy'), horizontal=True)

        ruminant = cw.label_plus_slider('Reduce ruminant meat consumption', 0, 100, 0, 25, ratio=(6,4)) / 25
        meatfree = cw.label_plus_slider('Number of meatfree days a week', 0, 7, 0, ratio=(6,4))
        extra_items = cw.label_plus_multiselect('Also exclude from meatfree days', ['Egg', 'FishSeafood', 'Dairy'])

        # progress_dietary.progress(ruminant + meatfree)

    # Farming and Prodction interventions
    # progress_farming = st.progress(0)
    with st.expander("**Land use and farming interventions** :earth_africa:"):

        # manure = cw.label_plus_slider('Improve manure treatment', 0, 4, 0, ratio=(6,4))
        # breeding = cw.label_plus_slider('Improve breeding', 0, 4, 0, ratio=(6,4))
        # feed_composition = cw.label_plus_slider('Improve stock feed composition', 0, 4, 0, ratio=(6,4))
        # grazing_feedlot = cw.label_plus_slider('Grazing versus feedlot', 0, 4, 0, ratio=(6,4))
        # calves_dairy = cw.label_plus_slider('Use calves from dairy herd', 0, 4, 0, ratio=(6,4))

        # progress_farming.progress(manure + breeding + feed_composition + grazing_feedlot + calves_dairy)

        pasture_sparing_4 = cw.label_plus_slider('Spared pasture ALC 4 land fraction', 0, 100, 0, 25, ratio=(6,4))
        pasture_sparing_5 = cw.label_plus_slider('Spared pasture ALC 5 land fraction', 0, 100, 0, 25, ratio=(6,4))
        arable_sparing_4 = cw.label_plus_slider('Spared arable ALC 4 land fraction', 0, 100, 0, 25, ratio=(6,4))
        arable_sparing_5 = cw.label_plus_slider('Spared arable ALC 5 land fraction', 0, 100, 0, 25, ratio=(6,4))

        # foresting_spared = cw.label_plus_slider('Forested spared land fraction', 0, 100, 0, 25, ratio=(6,4))
        # agroforestry = cw.label_plus_slider('Crop + tree replacement', 0, 4, 0, ratio=(6,4))

        # progress_farming.progress((land_sparing + silvopasture + agroforestry))

    # Policy interventions
    # progress_policy = st.progress(0)
    with st.expander("**Policy interventions** :office:"):
        st.write('Policy intervention sliders to be shown here')
        # progress_policy.progress(10)

    st.markdown('''--- Created by [FixOurFood](https://github.com/FoxOurFood/).''')

    with st.expander("Advanced settings"):
        k = st.slider('Adoption timescale', 1, 10, 1)


col1, col2 = st.columns((1,9))

with col2:
    # MAIN
    plot_key = st.selectbox("Figure to display", option_list)

    nutrient = baseline[scaling_nutrient]

    # scale food by ruminant slider
    scale_ruminant = xr.DataArray(data = 1-(ruminant/4)*logistic(k, 70, 2101-1961), coords = {"Year":years})

    aux = scale_food(food=nutrient,
                         scale= scale_ruminant,
                         origin="imports",
                         items=groups["RuminantMeat"],
                         constant=True,
                         fallback="exports")

    # scale food by meatfree slider
    scale_meatfree = xr.DataArray(data = 1-(meatfree/7)*logistic(k, 70, 2101-1961), coords = {"Year":years})

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

    scale_sparing_pasture = 1 - (pasture_sparing_4 + pasture_sparing_5)/200
    scale_sparing_arable = 1 - (arable_sparing_4 + arable_sparing_5)/200

    aux = scale_add(food=aux,
                    element_in="production",
                    element_out="imports",
                    items=animal_items,
                    scale = scale_sparing_pasture)

    aux = scale_add(food=aux,
                    element_in="production",
                    element_out="imports",
                    items=plant_items,
                    scale = scale_sparing_arable)

    # compute new scaled values
    scaling = aux / nutrient

    food_cap_day = food_cap_day_baseline * scaling
    co2e_cap_day = co2e_cap_day_baseline * scaling
    kcal_cap_day = kcal_cap_day_baseline * scaling
    prot_cap_day = prot_cap_day_baseline * scaling
    fats_cap_day = fats_cap_day_baseline * scaling

    co2e_year = co2e_year_baseline * scaling


    scaled_cap_day = {"Weight":food_cap_day,
                      "Emissions":co2e_cap_day,
                      "Energy":kcal_cap_day,
                      "Proteins":prot_cap_day,
                      "Fat":fats_cap_day}

    # Plot
    c = None
    f, plot1 = plt.subplots(1, figsize=(5,5))
    if plot_key == "CO2e concentration":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, C, c = 'k')
        plot1.set_ylabel(r"$CO_2$ concentrations (PPM)")

        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            st.pyplot(fig=f)

    elif plot_key == "CO2e emission per food group":

        # For some reason, xarray does not preserves the coordinates dtypes.
        # Here, we manually assign them to strings again to allow grouping by Non-dimension coordinate strigns
        co2e_year.Item_group.values = np.array(co2e_year.Item_group.values, dtype=str)
        co2e_year_groups = co2e_year.groupby("Item_group").sum().rename({"Item_group":"Item"})
        plot_years(co2e_year_groups["food"], ax=plot1)
        c = plot_years_altair(co2e_year_groups["food"], show="Item")

    elif plot_key == "Nutrients":
        pass

    elif plot_key == "Radiative forcing":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, F, c = 'k')
        plot1.set_ylabel(r"Total Radiative Forcing $(W/m^2)$")

        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            st.pyplot(fig=f)

    elif plot_key == "Temperature anomaly":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, T, c = 'k')
        plot1.set_ylabel(r"Temperature anomaly (K)")

        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            st.pyplot(fig=f)

    elif plot_key == "CO2e emission per food item":

        option_key = st.selectbox("Plot options", group_names)
        # Can't index by alternative coordinate name, use xr.where instead and squeeze
        co2e_year_item = co2e_year.sel(Item=co2e_year["Item_group"] == option_key).squeeze()
        plot_years(co2e_year_item["food"], ax=plot1)
        plot1.set_ylim(bottom=0)

        c = plot_years_altair(co2e_year_item["food"], show="Item_name")

    elif plot_key == "Per capita daily values":
        option_key = st.selectbox("Plot options", list(baseline.keys()))

        bar_plot_array = scaled_cap_day[option_key]
        # bar_plot_array = bar_plot_baseline * scaling
        bar_plot_array.Item_origin.values = np.array(bar_plot_array.Item_origin.values, dtype=str)
        bar_plot_array_groups = bar_plot_array.groupby("Item_origin").sum().rename({"Item_origin":"Item"})

        # altair
        c = plot_bars_altair(bar_plot_array_groups.sel(Year=2100), show="Item", xlimit = bar_plot_limits[option_key])

        # matplotlib
        # plot_bars(bar_plot_array_groups.sel(Year=2100), labels=bar_plot_array_groups.Item.values, ax=plot1)
        # col2_1, col2_2, col2_3 = st.columns((2,6,2))
        # with col2_2:
        #     st.pyplot(fig=f)

    elif plot_key == "Land Use":
        col_opt1, col_opt2 = st.columns((1,1))

        with col_opt1:
            option_key = st.selectbox("Plot options", land_options)

        if option_key == "Agricultural Land Classification":
            plot1.imshow(ALC.grade.T, interpolation="none", origin="lower", cmap = "RdYlGn_r")
            plot1.axis("off")

        elif option_key == "Crops":
            with col_opt2:
                crop_type = st.selectbox("Crop types", crop_types)
            plot1.imshow(CEH.area.sel(Type=crop_type).T, interpolation="none", origin="lower", cmap = "RdYlGn_r")
            plot1.axis("off")
        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            st.pyplot(fig=f)

        # c = plot_land_altair(ALC)

    if c is not None:
        st.altair_chart(altair_chart=c, use_container_width=True)

with col1:
    # MAIN
    st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
