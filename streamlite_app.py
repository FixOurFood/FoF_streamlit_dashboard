import streamlit as st

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import colors

import altair as alt
import numpy as np
import xarray as xr
from millify import millify
import pandas as pd

import custom_widgets as cw
from glossary import *
from afp_config import *
from altair_plots import *

from helper_functions import *

from agrifoodpy.food.food_supply import scale_food, scale_element, SSR

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

#     st.image("images/fof_logo.png")
    st.markdown("# Agrifood Calculator")

    # Consumer demand interventions
    with st.expander("**:spaghetti: Consumer demand**"):

        scaling_nutrient = st.radio("Which nutrient to keep constant when scaling food consumption",
                            ('Weight', 'Proteins', 'Fat', 'Energy'), horizontal=True, index=3, help=help["sidebar_consumer"][0])

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

#         # labmeat = cw.label_plus_slider('Increase labmeat uptake', ratio=(6,4),
#         labmeat = st.slider('Increase labmeat uptake',
#                                         min_value=0, max_value=100, step=25,
#                                         key="d5", help=help["sidebar_consumer"][6])
       
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
       
        # biofuel_spared = cw.label_plus_slider('Biofuel crops spared land fraction',ratio=(6,4),
#         biofuel_spared = st.slider('Biofuel crops spared land fraction',
#                                                 min_value=0, max_value=100, step=25,
#                                                 key='l4', help=help["sidebar_land"][3])
       
        # CCS_spared = cw.label_plus_slider('Carbon capture and storage spared land fraction',ratio=(6,4),
#         CCS_spared = st.slider('Carbon capture and storage spared land fraction',
#                                                 min_value=0, max_value=100, step=25,
#                                                 key='l5', help=help["sidebar_land"][4])

        st.button("Reset", on_click=update_slider, kwargs={"values": [0,0,0,0,0,0], "keys": ['l1', 'l2', 'l3', 'l4', 'l5']}, key='reset_l')
        # agroforestry = cw.label_plus_slider('Crop + tree replacement', 0, 4, 0, ratio=(6,4))

    # Technology and innovation
    with st.expander("**:gear: Technology and innovation**"):

#         # CCS_innovation = cw.label_plus_slider('Carbon capture and storage innovation', ratio=(6,4),
#         CCS_innovation = st.slider('Carbon capture and storage innovation',
#                                                 min_value=0, max_value=100, step=25,
#                                                 key='i1', help=help["sidebar_innovation"][0])

#         # labmeat_innovation = cw.label_plus_slider('Lab meat production innovation', ratio=(6,4),
#         labmeat_innovation = st.slider('Lab meat production innovation',
#                                                 min_value=0, max_value=100, step=25,
#                                                 key='i2', help=help["sidebar_innovation"][1])

#         # agg_innovation = cw.label_plus_slider('Inovation to improve aggricultural yield', ratio=(6,4),
#         agg_innovation = st.slider('Inovation to improve aggricultural yield',
#                                                 min_value=0, max_value=100, step=25,
#                                                 key='i3', help=help["sidebar_innovation"][2])
       
#         # incr_GHGE_innovation = cw.label_plus_slider('Incremental GHGE innovation', ratio=(6,4),
#         incr_GHGE_innovation = st.slider('Incremental GHGE innovation',
#                                                 min_value=0, max_value=100, step=25,
#                                                 key='i4', help=help["sidebar_innovation"][3])
       
#         # radc_GHGE_innovation = cw.label_plus_slider('Radical GHGE innovation', ratio=(6,4),
#         radc_GHGE_innovation = st.slider('Radical GHGE innovation',
#                                                 min_value=0, max_value=100, step=25,
#                                                 key='i5', help=help["sidebar_innovation"][4])
       
        st.button("Reset", on_click=update_slider, kwargs={"values": [0,0,0,0,0], "keys": ['i1', 'i2', 'i3', 'i4', 'i5']}, key='reset_i')

    # Policy interventions
    with st.expander("**:office: Policy interventions**"):
        st.write('Policy intervention sliders to be shown here')

    with st.expander("Advanced settings"):
        rda_kcal = st.slider('Recommended daily energy intake', min_value=2000, max_value=2500, value=2250)
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
    scale_sparing_pasture = pasture_sparing/100*np.sum(use_by_grade[4:6,1])/total_crops_pasture
    scale_sparing_arable = arable_sparing/100*np.sum(use_by_grade[4:6,0])/total_crops_arable

    print(np.sum(use_by_grade))

    spared_land_area_pasture = np.sum(use_by_grade[4:5,1])*pasture_sparing
    spared_land_area_arable= np.sum(use_by_grade[4:5,0])*arable_sparing

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

    # # Adjust the total emissions by subtracting sequestration

    # Adjust the total percentages in each pixel
    scaled_LC_type = LC_type.copy(deep=True)

    delta_spared_pasture = LC_type.loc[{"use":"grassland"}] * pasture_sparing/100 * np.isin(ALC.grade, [4,5])
    delta_spared_arable = LC_type.loc[{"use":"arable"}] * arable_sparing/100 * np.isin(ALC.grade, [4,5])

    scaled_LC_type.loc[{"use":"spared"}] += delta_spared_pasture
    scaled_LC_type.loc[{"use":"spared"}] += delta_spared_arable
    scaled_LC_type.loc[{"use":"grassland"}] -= delta_spared_pasture
    scaled_LC_type.loc[{"use":"arable"}] -= delta_spared_arable

    delta_spared_woodland = scaled_LC_type.loc[{"use":"spared"}] * foresting_spared/100 * np.isin(ALC.grade, [4,5])
    scaled_LC_type.loc[{"use":"woodland"}] += delta_spared_woodland
    scaled_LC_type.loc[{"use":"spared"}] -= delta_spared_woodland

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
       
    # reduce production and food consumed based on kcal
    waste_to_reduce = waste/100*(kcal_cap_day["food"].sel(Year=2100).sum(dim="Item") - rda_kcal)
    waste_factor = waste_to_reduce / kcal_cap_day["food"].sel(Year=2100).sum(dim="Item")
    waste_factor = waste_factor.to_numpy()
   
    # scale food from meatfree slider
    scale_past_waste = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future_waste = xr.DataArray(data = 1 - waste_factor*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020), coords = {"Year":np.arange(2020,2101)})
    scale_waste = xr.concat([scale_past_waste, scale_future_waste], dim="Year")

    aux = kcal_cap_day.copy(deep=True)
    aux["food"] *= scale_waste
    delta = kcal_cap_day["food"] - aux["food"]
    aux["production"] -= delta
    aux["imports"] += aux["production"].where(aux["production"] < 0)
    aux["production"] = aux["production"].where(aux["production"] > 0, other=0)

    # compute new scaled values (make sure NaN are set to 1 to avoid issues)
    scaling = aux / kcal_cap_day
    scaling = scaling.where(np.isfinite(scaling), other=1.0)

    food_cap_day = food_cap_day * scaling
    kcal_cap_day = kcal_cap_day * scaling
    prot_cap_day = prot_cap_day * scaling
    fats_cap_day = fats_cap_day * scaling

    co2e_year = co2e_year * scaling
    co2e_cap_day = co2e_cap_day * scaling

    scaled_cap_day = {"Weight":food_cap_day,
                      "Emissions":co2e_cap_day,
                      "Energy":kcal_cap_day,
                      "Proteins":prot_cap_day,
                      "Fat":fats_cap_day}
   
    # Plot
    c = None
    f, plot1 = plt.subplots(1, figsize=(4,4))

    total_emissions_gtco2e = (co2e_year["food"]*scaling["food"] * pop_world / pop_uk).sum(dim="Item").to_numpy()/1e15
    # C, F, T = fair.forward.fair_scm(, useMultigas=False)
    C, F, T = FAIR_run(total_emissions_gtco2e)
   
    if plot_key == "CO2e emission per food group":

        # For some reason, xarray does not preserves the coordinates dtypes.
        # Here, we manually assign them to strings again to allow grouping by Non-dimension coordinate strigns
        co2e_year.Item_group.values = np.array(co2e_year.Item_group.values, dtype=str)
        co2e_year_groups = co2e_year.groupby("Item_group").sum().rename({"Item_group":"Item"})
        c_groups = plot_years_altair(co2e_year_groups["food"]/1e6, show="Item", xlabel='Consumed food CO2e emissions [t CO2e / year]')
        c_baseline = plot_years_total(co2e_year_baseline["food"]/1e6, xlabel='Consumed food CO2e emissions [t CO2e / year]', sumdim="Item")
        c = c_groups + c_baseline

    elif plot_key == "CO2e emission per food item":

        option_key = st.selectbox("Plot options", group_names)
        # Can't index by alternative coordinate name, use xr.where instead and squeeze
        co2e_year_item = co2e_year.sel(Item=co2e_year["Item_group"] == option_key).squeeze()
        c_items = plot_years_altair(co2e_year_item["food"]/1e6, show="Item_name", xlabel='Consumed food CO2e emissions [t CO2e / year]')

        co2e_year_item_baseline = co2e_year_baseline.sel(Item=co2e_year_baseline["Item_group"] == option_key).squeeze()
        c_baseline = plot_years_total(co2e_year_item_baseline["food"]/1e6, xlabel='Consumed food CO2e emissions [t CO2e / year]', sumdim="Item")
        c=c_items + c_baseline

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

        if option_key == "Energy":

            c = c + alt.Chart(pd.DataFrame({
            'Energy': [rda_kcal],
            'color': ['red']
            })).mark_rule().encode(
            x='Energy:Q',
            color=alt.Color('color:N', scale=None)
            )

    elif plot_key == "Self-sufficiency ratio":

        SSR_scaled = SSR(food_cap_day)
        c = plot_years_total(SSR_scaled, xlabel="SSR")

        # col2_1, col2_2, col2_3 = st.columns((2,6,2))
        # with col2_2:
        #     plot1.plot(SSR_scaled)
        #     plot1.set_ylim(0,1)
        #     st.pyplot(fig=f)
       

    elif plot_key == "Land Use":
        col_opt1, col_opt2 = st.columns((1,1))

        with col_opt1:
            option_key = st.selectbox("Plot options", land_options)

        if option_key == "Agricultural Land Classification":
            plot1.imshow(ALC_ag_only.grade,
                         interpolation="none",
                         origin="lower",
                         cmap = "RdYlGn_r")

        elif option_key == "Land use":
            map_toplot = map_max(scaled_LC_type, dim="use")
            plot1.imshow(map_toplot, interpolation='none', origin='lower', cmap=cmap_tar, norm=norm_tar)

        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            plot1.axis("off")
            st.pyplot(fig=f)

        # c = plot_land_altair(ALC)

    if c is not None:
        st.altair_chart(altair_chart=c, use_container_width=True)

with col1:
    # MAIN
    st.metric(label="**:thermometer: Temperature rise by 2100 with respect to 2020, caused by world food consumed, assuming consumption similar to that of the UK**",
              value="{:.2f} °C".format(T[-1] - T[-80]),
              delta="{:.2f} °C - Compared to BAU".format((T[-1] - T[-80])-(T_base[-1] - T_base[-80])), delta_color="inverse",
              help=help["metrics"][0])

    st.metric(label="**:sunrise_over_mountains: Total area of agricultural spared land**",
              value=f"{millify(spared_land_area, precision=2)} ha",
              help=help["metrics"][1])

    st.metric(label="**:deciduous_tree: Total area of forested agricultural land**",
              value=f"{millify(forested_spared_land_area, precision=2)} ha",
              help=help["metrics"][2])

    st.metric(label="**:chart_with_downwards_trend: Total carbon sequestration by forested agricultural land**",
              value=f"{millify(co2_seq_total, precision=2)} t CO2/yr",
              help=help["metrics"][3])
