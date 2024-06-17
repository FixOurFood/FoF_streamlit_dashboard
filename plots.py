import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches
from utils.altair_plots import *
from agrifoodpy.food.food import FoodBalanceSheet
from glossary import *
from utils.helper_functions import *


def plots(datablock):

    # ----------------------------------------    
    #                  Plots
    # ----------------------------------------

    f, plot1 = plt.subplots(1, figsize=(8,8))

    # Add toggle to switch year horizon between 2050 and 2100
    col_multiselect, col_but_metric_yr = st.columns([11.5,1.5])

    with col_multiselect:
        plot_key = st.selectbox("Figure to display", option_list)

    with col_but_metric_yr:
        # metric_yr = st.slider("Year mode",
        #                       min_value=2050,
        #                       max_value=2100,
        #                       step=50,
        #                       value=2050)
        st.write("")
        st.write("")
        metric_year_toggle = st.toggle("Switch to 2100 mode")
        metric_yr = np.where(metric_year_toggle, 2100, 2050)

    # Emissions per food group or origin
    # ----------------------------------
    if plot_key == "CO2e emission per food group":
        emissions = datablock["impact"]["g_co2e/year"].sel(Year=slice(None, metric_yr))
        seq_da = datablock["impact"]["co2e_sequestration"].sel(Year=slice(None, metric_yr))
        col_opt, col_element = st.columns([1,1])
        with col_opt:
            option_key = st.selectbox("Plot options", ["Food group", "Food origin"])
        with col_element:
            element_key = st.selectbox("Food Supply Element", ["production", "food", "imports", "exports"])

        # f = plot_years_total(emissions_baseline["food"].sum(dim="Item"), xlabel="Year")

        if option_key == "Food origin":
            f = plot_years_altair(emissions[element_key]/1e6, show="Item_origin", ylabel="t CO2e / Year")

        elif option_key == "Food group":
            f = plot_years_altair(emissions[element_key]/1e6, show="Item_group", ylabel="t CO2e / Year")

        # Plot sequestration
        f += plot_years_altair(-seq_da, show="Item", ylabel="t CO2e / Year")
        emissions_sum = emissions["production"].sum(dim="Item")
        seqestration_sum = seq_da.sum(dim="Item")

        f += plot_years_total((emissions_sum/1e6 - seqestration_sum),
                              ylabel="t CO2e / Year",
                              color="black")

        f=f.configure_axis(
            labelFontSize=15,
            titleFontSize=15)

    # Emissions per food item from each group
    # ---------------------------------------
    elif plot_key == "CO2e emission per food item":
        emissions = datablock["impact"]["g_co2e/year"].sel(Year=slice(None, metric_yr))
        emissions_baseline = st.session_state["datablock_baseline"]["impact"]["g_co2e/year"]
        col_opt, col_element = st.columns([1,1])
        with col_opt:
            option_key = st.selectbox("Plot options", np.unique(emissions.Item_group.values))
        with col_element:
            element_key = st.selectbox("Food Supply Element", ["production", "food", "imports", "exports"])

        # plot1.plot(emissions_baseline.Year.values,
        #            emissions_baseline["food"].sel(
        #                Item=emissions_baseline["Item_group"] == option_key).sum(dim="Item"))
        
        to_plot = emissions[element_key].sel(Item=emissions["Item_group"] == option_key)/1e6

        f = plot_years_altair(to_plot, show="Item_name", ylabel="t CO2e / Year")
        f = f.configure_axis(
                labelFontSize=15,
                titleFontSize=15)
        

    # FAOSTAT bar plot with per-capita daily values
    # ---------------------------------------------
    elif plot_key == "Per capita daily values":
        per_cap_options = {"g/cap/day": 8000,
                   "g_prot/cap/day": 500,
                   "g_fat/cap/day": 550,
                   "g_co2e/cap/day": 18000,
                   "kCal/cap/day": 14000}

        option_key = st.selectbox("Plot options", list(per_cap_options.keys()))

        to_plot = datablock["food"][option_key].sel(Year=metric_yr).fillna(0)
        to_plot.Item_origin.values = np.array(to_plot.Item_origin.values, dtype=str)
        to_plot = to_plot.fbs.group_sum(coordinate="Item_origin", new_name="Item")

        f = plot_bars_altair(to_plot, show="Item", x_axis_title=option_key, xlimit=per_cap_options[option_key])

        if option_key == "kCal/cap/day":
            f += alt.Chart(pd.DataFrame({
            'Energy': [datablock["food"]["rda_kcal"]],
            'color': ['red']
            })).mark_rule().encode(
            x='Energy:Q',
            color=alt.Color('color:N', scale=None)
            )
        
        
    # Self-sufficiency ratio as a function of time
    # --------------------------------------------
    elif plot_key == "Self-sufficiency ratio":

        option_key = st.selectbox("Plot options", ["g/cap/day", "kCal/cap/day", "g_prot/cap/day", "g_fat/cap/day"])

        SSR = datablock["food"][option_key].fbs.SSR().sel(Year=slice(None, metric_yr)) * 100

        f = plot_years_total(SSR, ylabel="Self-sufficiency ratio [%]").configure_axis(
                labelFontSize=20,
                titleFontSize=20)

    # Various land plots, including Land use and ALC
    # ----------------------------------------------
    elif plot_key == "Land":

        col_opt1, col_opt2 = st.columns((1,1))
        ALC_toplot = datablock["land"]["dominant_classification"]
        pctg = datablock["land"]["percentage_land_use"]
        LC_toplot = map_max(pctg, dim="aggregate_class")

        with col_opt1:
            land_options = ["Land use", "Agricultural Land Classification"]
            option_key = st.selectbox("Plot options", land_options)

        if option_key == "Agricultural Land Classification":
            ALC_toplot.land.plot(ax=plot1)

        elif option_key == "Land use":
            color_list = [land_color_dict[key] for key in pctg.aggregate_class.values]
            label_list = [land_label_dict[key] for key in pctg.aggregate_class.values]

            unique_index = np.unique(label_list, return_index=True)[1]

            cmap_tar = colors.ListedColormap(color_list)
            bounds_tar = np.linspace(-0.5, len(color_list)-0.5, len(color_list)+1)
            norm_tar = colors.BoundaryNorm(bounds_tar, cmap_tar.N)

            plot1.imshow(LC_toplot, interpolation="none", origin="lower",
                         cmap=cmap_tar, norm=norm_tar)
            patches = [mpatches.Patch(color=color_list[i],
                                      label=label_list[i]) for i in unique_index]
            plot1.legend(handles=patches, loc="upper left")

            left, bottom, width, height = [0.1, 0.3, 0.3, 0.3]
            inset = f.add_axes([left, bottom, width, height])
            inset.pie(pctg.sum(dim=["x", "y"]), colors=color_list)
    
        plot1.axis("off")
        plot1.set_xlim(left=-500)


    # Output figure depending on type
    if isinstance(f, matplotlib.figure.Figure):
        col2_1, col2_2, col2_3 = st.columns((2,3,2))
        with col2_2:
            st.pyplot(fig=f)
    
    else:
        st.altair_chart(f, use_container_width=True)

    return metric_yr