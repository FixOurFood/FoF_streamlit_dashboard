import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches
from utils.altair_plots import *
from agrifoodpy.food.food import FoodBalanceSheet
from glossary import *
from utils.helper_functions import *

stage_I_deadline = 'December 31, 2024'

def plots(datablock):

    f, plot1 = plt.subplots(1, figsize=(8,8))

    # Add toggle to switch year horizon between 2050 and 2100
    col_multiselect, col_but_metric_yr = st.columns([11.5,1.5])

    with col_multiselect:
        plot_key = st.selectbox("Figure to display", option_list)

    with col_but_metric_yr:
        st.write("")
        st.write("")
        metric_year_toggle = st.toggle("Switch to 2100 mode")
        metric_yr = np.where(metric_year_toggle, 2100, 2050)
    # ----------------------------------------    
    #                  Plots
    # ----------------------------------------

    # Summary
    # -------
    if plot_key == "Summary":

        col_text, col_comp_1, col_comp_2 = st.columns([1,1,1])
        with col_text:
            st.markdown(f'''Once you have selected the ambition levels for the
                        different interventions, enter your unique ID on the
                        field below and click the "Submit scenario" button. You can
                        change your responses as many times as you want before
                        the Stage I deadline on {stage_I_deadline}.''')

            user_id = st.text_input("Enter your unique ID", "AFP")
            submit_state = st.button("Submit scenario")

            if submit_state:
                st.success(f'Scenario submitted for user {user_id}', icon="✅")

        with col_comp_1:
            with st.container(height=50, border=True):
                st.markdown("""Just testing stacking containers one after the other
                            This one has 50 pixels of height""")
            with st.container(height=150, border=True):
                st.markdown("""Just testing stacking containers one after the other
                            This one has 150 pixels of height""")
            with st.container(height=250, border=True):
                st.markdown("""Just testing stacking containers one after the other
                            This one has 250 pixels of height""")

        with col_comp_2:
            with st.container(height=100, border=True):
                st.markdown("""Just testing stacking containers one after the other
                            This one has 100 pixels of height""")
            with st.container(height=200, border=True):
                st.markdown("""Just testing stacking containers one after the other
                            This one has 200 pixels of height""")
            with st.container(height=300, border=True):
                st.markdown("""Just testing stacking containers one after the other
                            This one has 300 pixels of height""")

    # Emissions per food group or origin
    # ----------------------------------
    elif plot_key == "Quantities per food group":
        col_opt, col_element, col_y = st.columns([1,1,1])
        with col_opt:
            option_key = st.selectbox("Plot options", ["Food group", "Food origin"])
        with col_element:
            element_key = st.selectbox("Food Supply Element", ["production", "food", "imports", "exports", "feed"])
        with col_y:
            y_key = st.selectbox("Quantity", ["CO2e emissions", "kCal/cap/day", "g/cap/day"])

        if y_key == "CO2e emissions":
            emissions = datablock["impact"]["g_co2e/year"].sel(Year=slice(None, metric_yr))
            seq_da = datablock["impact"]["co2e_sequestration"].sel(Year=slice(None, metric_yr))

            if option_key == "Food origin":
                f = plot_years_altair(emissions[element_key]/1e6, show="Item_origin", ylabel="t CO2e / Year")

            elif option_key == "Food group":
                f = plot_years_altair(emissions[element_key]/1e6, show="Item_group", ylabel="t CO2e / Year")

            # Plot sequestration
            f += plot_years_altair(-seq_da, show="Item", ylabel="t CO2e / Year")
            emissions_sum = emissions[element_key].sum(dim="Item")
            seqestration_sum = seq_da.sum(dim="Item")

            f += plot_years_total((emissions_sum/1e6 - seqestration_sum),
                                ylabel="t CO2e / Year",
                                color="black")
        else:
            emissions = datablock["food"][y_key].sel(Year=slice(None, metric_yr))

            if option_key == "Food origin":
                f = plot_years_altair(emissions[element_key], show="Item_origin", ylabel=y_key)

            elif option_key == "Food group":
                f = plot_years_altair(emissions[element_key], show="Item_group", ylabel=y_key)

        f=f.configure_axis(
            labelFontSize=15,
            titleFontSize=15)
        
        col2_1, col2_2, col2_3 = st.columns((1,4,1))
        with col2_2:
            st.altair_chart(f, use_container_width=True)

    # Emissions per food item from each group
    # ---------------------------------------
    elif plot_key == "Quantities per food item":
        col_opt, col_element, col_y = st.columns([1,1,1])
        emissions = datablock["impact"]["g_co2e/year"].sel(Year=slice(None, metric_yr))
        with col_opt:
            option_key = st.selectbox("Plot options", np.unique(emissions.Item_group.values))
        with col_element:
            element_key = st.selectbox("Food Supply Element", ["production", "food", "imports", "exports", "feed"])
        with col_y:
            y_key = st.selectbox("Quantity", ["CO2e emissions", "kCal/cap/day", "g/cap/day"])

        if y_key == "CO2e emissions":
            to_plot = emissions[element_key].sel(Item=emissions["Item_group"] == option_key)/1e6

        else:
            to_plot = datablock["food"][y_key].sel(Year=slice(None, metric_yr))
            to_plot = to_plot[element_key].sel(Item=to_plot["Item_group"] == option_key)

        f = plot_years_altair(to_plot, show="Item_name", ylabel="t CO2e / Year")
        f = f.configure_axis(
                labelFontSize=15,
                titleFontSize=15)
        
        col2_1, col2_2, col2_3 = st.columns((1,4,1))
        with col2_2:
            st.altair_chart(f, use_container_width=True)
        

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

        col2_1, col2_2, col2_3 = st.columns((1,4,1))
        with col2_2:
            st.altair_chart(f, use_container_width=True)
        
        
    # Self-sufficiency ratio as a function of time
    # --------------------------------------------
    elif plot_key == "Self-sufficiency ratio":

        option_key = st.selectbox("Plot options", ["g/cap/day", "kCal/cap/day", "g_prot/cap/day", "g_fat/cap/day"])

        SSR = datablock["food"][option_key].fbs.SSR().sel(Year=slice(None, metric_yr)) * 100

        f = plot_years_total(SSR, ylabel="Self-sufficiency ratio [%]").configure_axis(
                labelFontSize=20,
                titleFontSize=20)
        
        col2_1, col2_2, col2_3 = st.columns((1,4,1))
        with col2_2:
            st.altair_chart(f, use_container_width=True)

    # Various land plots, including Land use and ALC
    # ----------------------------------------------
    elif plot_key == "Land":

        pctg = datablock["land"]["percentage_land_use"]
        LC_toplot = map_max(pctg, dim="aggregate_class")

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
        # plot1.legend(handles=patches, loc="upper left")

        plot1.axis("off")
        plot1.set_xlim(left=-500)

        col2_1, col2_2, col2_3 = st.columns((3,2,2))
        with col2_1:
            st.pyplot(fig=f)
        with col2_2:
            land_pctg = pctg.sum(dim=["x", "y"])
            pie = pie_chart_altair(land_pctg, show="aggregate_class")

            # source = pd.DataFrame({"category": [2, 1, 3, 4, 5, 6],
            #                        "value": [4, 6, 10, 3, 7, 8]})

            # pie = alt.Chart(source).mark_arc().encode(
            #     theta=alt.Theta(field="value",
            #                     type="quantitative", stack=True),

            #     order=alt.Order(field="category", type="nominal"),
            #     color=alt.Color(field="category", type="nominal"),
            #     )
            st.altair_chart(pie)

    elif plot_key == "Sectoral emissions":

        # Create dataarray with sectoral emissions for the different 
        sectoral_emissions = xr.DataArray(data = list(sector_emissions_dict.values()),
                                          name="Sectoral emissions",
                                          coords={"Sector": list(sector_emissions_dict.keys())})

        # Fill values for Agriculture, Land use sinks, and removals
        emissions_ds = datablock["impact"]["g_co2e/year"].sel(Year=metric_yr)
        total_emissions = emissions_ds["production"].sum(dim="Item").values/1e12
        seq_da = datablock["impact"]["co2e_sequestration"].sel(Year=metric_yr)
        total_seq = seq_da.sum(dim="Item").values/1e6

        sectoral_emissions.loc[{"Sector": "Agriculture"}] = total_emissions
        sectoral_emissions.loc[{"Sector": "Land use sinks"}] = -total_seq

        f = plot_single_bar_altair(sectoral_emissions, show="Sector", axis_title="Mt CO2e / year",
                                            unit="Mt CO2e / year", vertical=True,
                                            mark_total=True, show_zero=True, ax_ticks=True)
        
        f = f.properties(height=600)
        
        col2_1, col2_2, col2_3 = st.columns((1,1,1))
        with col2_1:
            st.altair_chart(f, use_container_width=True)

    return metric_yr