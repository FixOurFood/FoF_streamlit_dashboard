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

from agrifoodpy.food.food_supply import FAOSTAT, Nutrients_FAOSTAT, scale_food, plot_years, plot_bars
from agrifoodpy.land.land import ALC_5000 as ALC
from altair_plots import *


# Helper Functions
def logistic(k, x0, xmax, xmin=0):
    return 1 / (1 + np.exp(-k*(np.arange(xmax-xmin) - x0)))

# GUI
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with st.sidebar:
    # Dietary interventions

    k = st.slider('Adoption timescale', 1, 10, 5)

    progress_dietary = st.progress(0)
    with st.expander("Dietary interventions"):
        scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                            ('Weight', 'Proteins', 'Fat', 'Energy'), horizontal=True)

        ruminant = cw.label_plus_slider('Reduce ruminant meat consumption', 0, 4, 0, ratio=(6,4))
        meatfree = cw.label_plus_slider('Number of meatfree days a week', 0, 7, 0, ratio=(6,4))
        extra_items = cw.label_plus_multiselect('Also exclude from meatfree days', ['Egg', 'FishSeafood', 'Dairy'])

        progress_dietary.progress(ruminant + meatfree)

    # Farming and Prodction interventions
    progress_farming = st.progress(0)
    with st.expander("Land use and farming interventions"):

        # manure = cw.label_plus_slider('Improve manure treatment', 0, 4, 0, ratio=(6,4))
        # breeding = cw.label_plus_slider('Improve breeding', 0, 4, 0, ratio=(6,4))
        # feed_composition = cw.label_plus_slider('Improve stock feed composition', 0, 4, 0, ratio=(6,4))
        # grazing_feedlot = cw.label_plus_slider('Grazing versus feedlot', 0, 4, 0, ratio=(6,4))
        # calves_dairy = cw.label_plus_slider('Use calves from dairy herd', 0, 4, 0, ratio=(6,4))

        # progress_farming.progress(manure + breeding + feed_composition + grazing_feedlot + calves_dairy)

        land_sparing = cw.label_plus_slider('Reforested spared land', 0, 4, 0, ratio=(6,4))
        silvopasture = cw.label_plus_slider('Pasture + tree replacement', 0, 4, 0, ratio=(6,4))
        agroforestry = cw.label_plus_slider('Crop + tree replacement', 0, 4, 0, ratio=(6,4))

        progress_farming.progress(land_sparing + silvopasture + agroforestry)

    # Policy interventions
    progress_policy = st.progress(0)
    with st.expander("Policy interventions"):
        st.write('Policy intervention sliders to be shown here')
        progress_policy.progress(10)

    st.markdown('''--- Created by [jucordero](https://github.com/jucordero/).''')


col1, col2 = st.columns((3,7))

with col2:
    # MAIN
    st.write("")
    st.write("")
    plot_key = st.selectbox("Figure to display", option_list)

    nutrient = baseline[scaling_nutrient]

    scale_ruminant = xr.DataArray(data = 1-(ruminant/4)*logistic(k, 70, 2101-1961), coords = {"Year":years})

    aux = scale_food(food=nutrient,
                         scale= scale_ruminant,
                         origin="imports",
                         items=groups["RuminantMeat"],
                         constant=True,
                         fallback="exports")

    scale_meatfree = xr.DataArray(data = 1-(meatfree/7)*logistic(k, 70, 2101-1961), coords = {"Year":years})

    meatfree_items = np.concatenate((groups["RuminantMeat"], groups["OtherMeat"]))

    for item in extra_items:
        meatfree_items = np.concatenate((extra_items, groups[item]))

    aux = scale_food(food=aux,
                         scale= scale_meatfree,
                         origin="imports",
                         items=meatfree_items,
                         constant=True,
                         fallback="exports")

    scaling = aux / nutrient
    co2e_year = co2e_year_baseline * scaling

    # Plot
    c = None
    f, plot1 = plt.subplots(1)
    if plot_key == "CO2e concentration":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, C, c = 'k')
        plot1.set_ylabel(r"$CO_2$ concentrations (PPM)")

    elif plot_key == "CO2e emission per food group":

        # For some reason, xarray does not preserves the coordinates dtypes.
        # Here, we manually assign them to strings again to allow grouping by Non-dimension coordinate strigns
        co2e_year.Item_group.values = np.array(co2e_year.Item_group.values, dtype=str)
        co2e_year_groups = co2e_year.groupby("Item_group").sum().rename({"Item_group":"Item"})
        plot_years(co2e_year_groups["food"], ax=plot1)
        c = plot_years_altair(co2e_year_groups["food"], show="Item")
        plot1.set_ylim(0, 4e11)

    elif plot_key == "Nutrients":
        pass

    elif plot_key == "Radiative forcing":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, F, c = 'k')
        plot1.set_ylabel(r"Total Radiative Forcing $(W/m^2)$")

    elif plot_key == "Temperature anomaly":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, T, c = 'k')
        plot1.set_ylabel(r"Temperature anomaly (K)")

    elif plot_key == "CO2e emission per food item":

        option_key = st.selectbox("Plot options", group_names)
        # Can't index by alternative coordinate name, use xr.where instead and squeeze
        co2e_year_item = co2e_year.sel(Item=co2e_year["Item_group"] == option_key).squeeze()
        plot_years(co2e_year_item["food"], ax=plot1)
        plot1.set_ylim(bottom=0)

        c = plot_years_altair(co2e_year_item["food"], show="Item_name")

    elif plot_key == "Per capita daily values":
        option_key = st.selectbox("Plot options", list(baseline.keys()))
        bar_plot_baseline = baseline_cap_day[option_key]

        bar_plot_array = bar_plot_baseline * scaling
        bar_plot_array.Item_origin.values = np.array(bar_plot_array.Item_origin.values, dtype=str)
        bar_plot_array_groups = bar_plot_array.groupby("Item_origin").sum().rename({"Item_origin":"Item"})

        # altair
        c = plot_bars_altair(bar_plot_array_groups.sel(Year=2100), show="Item", xlimit = bar_plot_limits[option_key])

        # matplotlib
        # plot_bars(bar_plot_array_groups.sel(Year=2100), labels=bar_plot_array_groups.Item.values, ax=plot1)

    elif plot_key == "Land Use":
        option_key = st.selectbox("Plot options", land_options)
        c = plot_land_altair(ALC)

    if c is None:
        st.pyplot(fig=f, use_container_width=True)
    else:
        st.altair_chart(altair_chart=c, use_container_width=True)

with col1:
    # MAIN
    st.write("")
    st.write("")
    #

col1.metric(label="Temperature", value="70 °F", delta="1.2 °F")
