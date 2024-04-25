import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches
from altair_plots import *
from agrifoodpy.food.food import FoodBalanceSheet
from glossary import *
from helper_functions import *


def plots(datablock):

    # ----------------------------------------    
    #                  Plots
    # ----------------------------------------

    f, plot1 = plt.subplots(1, figsize=(7,7))
    
    plot_key = st.selectbox("Figure to display", option_list)

    # Emissions per food group or origin
    # ----------------------------------
    if plot_key == "CO2e emission per food group":
        emissions = datablock["impact"]["g_co2e/year"]
        emissions_baseline = st.session_state["datablock_baseline"]["impact"]["g_co2e/year"]
        option_key = st.selectbox("Plot options", ["Food group", "Food origin"])

        # f = plot_years_total(emissions_baseline["food"].sum(dim="Item"), xlabel="Year")

        if option_key == "Food origin":
            f = plot_years_altair(emissions["production"]/1e6, show="Item_origin", ylabel="t CO2e / Year")

        elif option_key == "Food group":
            f = plot_years_altair(emissions["production"]/1e6, show="Item_group", ylabel="t CO2e / Year")

        # Plot sequestration
        seq_da = datablock["impact"]["co2e_sequestration"]
        f += plot_years_altair(-seq_da, show="Item", ylabel="t CO2e / Year")

    # Emissions per food item from each group
    # ---------------------------------------
    elif plot_key == "CO2e emission per food item":
        emissions = datablock["impact"]["g_co2e/year"]
        emissions_baseline = st.session_state["datablock_baseline"]["impact"]["g_co2e/year"]
        option_key = st.selectbox("Plot options", np.unique(emissions.Item_group.values))

        # plot1.plot(emissions_baseline.Year.values,
        #            emissions_baseline["food"].sel(
        #                Item=emissions_baseline["Item_group"] == option_key).sum(dim="Item"))
        
        to_plot = emissions["production"].sel(Item=emissions["Item_group"] == option_key)

        f = plot_years_altair(to_plot, show="Item_name", ylabel="Year")

    # Temperature anomaly plot as a function of time
    # ----------------------------------------------
    elif plot_key == "Temperature anomaly":
        
        T = datablock["impact"]["T"]
        f = plot_years_total(T)

    # FAOSTAT bar plot with per-capita daily values
    # ---------------------------------------------
    elif plot_key == "Per capita daily values":
        per_cap_options = {"g/cap/day": 8000,
                   "g_prot/cap/day": 500,
                   "g_fat/cap/day": 550,
                   "g_co2e/cap/day": 18000,
                   "kCal/cap/day": 14000}

        
        option_key = st.selectbox("Plot options", list(per_cap_options.keys()))


        to_plot = datablock["food"][option_key].isel(Year=-1).fillna(0)
        to_plot.Item_origin.values = np.array(to_plot.Item_origin.values, dtype=str)
        to_plot = to_plot.groupby("Item_origin").sum().rename({"Item_origin":"Item"})

        f = plot_bars_altair(to_plot, show="Item", x_axis_title=option_key, xlimit=per_cap_options[option_key])
        
        
    # Self-sufficiency ratio as a function of time
    # --------------------------------------------
    elif plot_key == "Self-sufficiency ratio":

        SSR = datablock["food"]["g/cap/day"].fbs.SSR()
        f = plot_years_total(SSR)
        
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
            #             "broadl" "conif"  "arable"  "improv"  "semi-n"  "mount"  "saltw" "freshw""coast" "built" "purple"
            color_list = ["green", "green", "yellow", "orange", "orange", "gray", "gray", "gray", "gray", "gray", "purple", "red"]
            label_list = ["Forest", "Forest", "Arable", "Grass", "Grass", "Mountain", "Water", "Water", "Water", "Non agricultural", "Spared", "BECCS"]
            cmap_tar = colors.ListedColormap(color_list)
            bounds_tar = np.linspace(-0.5, len(color_list)-0.5, len(color_list)+1)
            norm_tar = colors.BoundaryNorm(bounds_tar, cmap_tar.N)

            plot1.imshow(LC_toplot, interpolation="none", origin="lower",
                         cmap=cmap_tar, norm=norm_tar)
            patches = [mpatches.Patch(color=color_list[i], label=label_list[i]) for i in [0,2,3,9,10,11]]
            plot1.legend(handles=patches, loc="upper left")

        plot1.axis("off")
        left, bottom, width, height = [0.1, 0.3, 0.3, 0.3]
        inset = f.add_axes([left, bottom, width, height])

        inset.pie(pctg.sum(dim=["x", "y"]), colors=color_list )

    # Output figure depending on type
    if isinstance(f, matplotlib.figure.Figure):
        col2_1, col2_2, col2_3 = st.columns((2,6,2))
        with col2_2:
            st.pyplot(fig=f)
    
    else:
        # st.altair_chart(f, use_container_width=True)
        st.altair_chart(f, use_container_width=True)