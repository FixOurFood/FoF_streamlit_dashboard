import streamlit as st
from streamlit_extras.bottom_container import bottom
from streamlit_extras.add_vertical_space import add_vertical_space
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches
from utils.altair_plots import *
from agrifoodpy.food.food import FoodBalanceSheet
from glossary import *
from utils.helper_functions import *
from consultation_utils import submit_scenario, get_user_list, stage_I_deadline

def plots(datablock):

    # ----------------------------------------    
    #                  Plots
    # ----------------------------------------

    col_multiselect, col_but_metric_yr = st.columns([11.5,1.5])

    with col_multiselect:
        plot_key = st.selectbox("Figure to display", option_list)

    #Toggle to switch year horizon between 2050 and 2100
    with col_but_metric_yr:
        st.write("")
        st.write("")
        metric_year_toggle = st.toggle("Switch to 2100 mode")
        metric_yr = np.where(metric_year_toggle, 2100, 2050)

    # Summary
    # -------
    if plot_key == "Summary":

        col_comp_1, col_comp_2, col_comp_3 = st.columns([1,1,1])

        # Emissions and removals balance
        with col_comp_1:

            with st.container(height=750, border=True):
                
                st.markdown('''**UK Emissions and removals balance**''')
                if st.session_state.emission_factors == "NDC 2020":
                    
                    seq_da = datablock["impact"]["co2e_sequestration"].sel(Year=metric_yr)
                    emissions = datablock["impact"]["g_co2e/year"]["production"].sel(Year=metric_yr)/1e6
                    total_emissions = emissions.sum(dim="Item").values/1e6
                    total_seq = seq_da.sel(Item=["Broadleaved woodland", "Coniferous woodland"]).sum(dim="Item").values/1e6
                    total_removals = seq_da.sel(Item=["BECCS from waste", "BECCS from overseas biomass", "BECCS from land", "DACCS"]).sum(dim="Item").values/1e6

                    emissions_balance = xr.DataArray(data = list(sector_emissions_dict.values()),
                                          name="Sectoral emissions",
                                          coords={"Sector": list(sector_emissions_dict.keys())})
                    
                    emissions_balance.loc[{"Sector": "Agriculture"}] = total_emissions
                    emissions_balance.loc[{"Sector": "Land use sinks"}] = -total_seq
                    emissions_balance.loc[{"Sector": "Removals"}] = -total_removals

                    show_sectors = st.checkbox("Show agriculture and land use only", value=False)

                    reference = 92.39
                    if show_sectors:
                        reference = 31.61
                        emissions_balance = emissions_balance.sel(Sector=["Agriculture", "Land use sinks", "Removals"])

                    c = plot_single_bar_altair(emissions_balance, show="Sector",
                        axis_title="Mt CO2e / year", unit="Mt CO2e / year", vertical=True,
                        mark_total=True, show_zero=True, ax_ticks=True, legend=True,
                        ax_min=-90, ax_max=120, reference=reference)
                    
                elif st.session_state.emission_factors == "PN18":

                    emissions = datablock["impact"]["g_co2e/year"]["production"].sel(Year=metric_yr)/1e6
                    emissions = emissions.fbs.group_sum(coordinate="Item_origin", new_name="Item")
                    seq_da = datablock["impact"]["co2e_sequestration"].sel(Year=metric_yr)

                    emissions_balance = xr.concat([emissions/1e6, -seq_da/1e6], dim="Item")

                    c = plot_single_bar_altair(emissions_balance, show="Item",
                                                    axis_title="Sequestration / Production emissions [M tCO2e]",
                                                    ax_min=-3e2, ax_max=3e2, unit="M tCO2e", vertical=True,
                                                    mark_total=True, show_zero=True, ax_ticks=True)
                    
                c = c.properties(height=500)
                st.altair_chart(c, use_container_width=True)

                st.caption('''<div style="text-align: justify;">
                           Above is the comparison between the total emissions from
                           food produced in the UK and the sequestration from different land uses
                           Emissions include all stages of production up to retail, including
                           processing and transportation, and are dissagregated into food product,
                           origin. The yellow diamond shows the net balance between emissions and
                           sequestration from agriculture and land use combined
                           </div>''', unsafe_allow_html=True)

        # Self-sufficiency ratio
        with col_comp_2:
            with st.container(height=750, border=True):

                st.markdown('''**Self-sufficiency ratio.**''')

                ssr_metric = st.selectbox("Select metric", ["g/cap/day",
                                                           "g_prot/cap/day",
                                                           "g_fat/cap/day",
                                                           "g_co2e/cap/day",
                                                           "kCal/cap/day",], key="SSR_metric")

                gcapday = datablock["food"][ssr_metric].sel(Year=metric_yr).fillna(0)
                gcapday = gcapday.fbs.group_sum(coordinate="Item_origin", new_name="Item")
                gcapday_ref = datablock["food"][ssr_metric].sel(Year=2020).fillna(0)
                gcapday_ref = gcapday_ref.fbs.group_sum(coordinate="Item_origin", new_name="Item")

                SSR_ref = gcapday_ref.fbs.SSR()
                SSR_metric_yr = gcapday.fbs.SSR()

                st.metric(label="SSR", value="{:.2f} %".format(100*SSR_metric_yr),
                    delta="{:.2f} %".format(100*(SSR_metric_yr-SSR_ref)))
                
                origin_color={"Animal Products": "red",
                              "Vegetal Products": "green",
                              "Cultured Product": "blue"}
                
                domestic_use = gcapday["imports"]+gcapday["production"]-gcapday["exports"]
                domestic_use.name="domestic"

                production_bar = plot_single_bar_altair(gcapday["production"],
                                                        show="Item",
                                                        vertical=False,
                                                        ax_ticks=True,
                                                        bar_width=100,
                                                        ax_min=0,
                                                        ax_max=np.max([gcapday["production"].sum(), domestic_use.sum()]),
                                                        axis_title="Food production per capita",
                                                        unit=ssr_metric.replace("_"," "),
                                                        color=origin_color)

                imports_bar = plot_single_bar_altair(domestic_use,
                                                     show="Item",
                                                     vertical=False,
                                                     ax_ticks=True,
                                                     bar_width=100,
                                                     ax_min=0,
                                                     ax_max=np.max([gcapday["production"].sum(), domestic_use.sum()]),
                                                     axis_title="Domestic use per capita",
                                                     unit=ssr_metric.replace("_"," "),
                                                     color=origin_color)


                st.altair_chart(production_bar, use_container_width=True)
                st.altair_chart(imports_bar, use_container_width=True)
                
                if SSR_metric_yr < SSR_ref:
                    st.markdown(f'''
                    <span style="color:red">
                    <b>The UK is more dependent on imports than today</b>
                    </span>
                    ''', unsafe_allow_html=True)

                    st.caption('''<div style="text-align: justify;">
                               The selected pathway results in a future where
                               the UK is highly dependent on imports. Imports are
                               more influenced by external events such as conflicts,
                               climatic catastrophes, and trade disruptions.
                               </div>''', unsafe_allow_html=True)
                    
                elif SSR_metric_yr > SSR_ref and SSR_metric_yr < 1:
                    st.markdown(f'''
                    <span style="color:orange">
                    <b>The UK is more self-sufficient</b>
                    </span>
                    ''', unsafe_allow_html=True)

                    st.caption('''<div style="text-align: justify;">
                               The selected pathway results in a future where
                               the UK is more self-sufficient than today depending less
                               on imports to meet its food needs. This can result in
                               a more resilient food system, able to provide food security
                               in the face of external shocks.
                               </div>''', unsafe_allow_html=True)
                    
                elif SSR_metric_yr > 1:
                    st.markdown(f'''
                    <span style="color:green">
                    <b>The UK is completely self-sufficient</b>
                    </span>
                    ''', unsafe_allow_html=True)

                    st.caption('''<div style="text-align: justify;">
                               The selected pathway results in a future where
                               the UK is completely self-sufficient and does not depend
                               on imports to meet its food needs.
                               </div>''', unsafe_allow_html=True)
                st.write("")
                st.caption('''<div style="text-align: justify;">
                The self-sufficiency ratio (SSR) is the ratio of the
                amount of food produced by a country to the amount of
                food it would need to meet its own food needs.
                A low value indicates that a country is highly dependent
                on imports while a value higher than 100% means a country
                produces more food than it needs
                </div>''', unsafe_allow_html=True)
               
        # Land use
        with col_comp_3:
            with st.container(height=750, border=True):

                st.markdown('''**Land use distribution**''')


                f, plot1 = plt.subplots(1, figsize=(6, 6))
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

                plot1.axis("off")
                plot1.set_xlim(left=-100)
                plot1.set_ylim(top=1000)

                _, col_plot, _ = st.columns((0.1, 0.7, 0.1))
                with col_plot:
                    st.pyplot(f)

                pctg = datablock["land"]["percentage_land_use"]
                totals = pctg.sum(dim=["x", "y"])
                bar_land_use = plot_single_bar_altair(totals, show="aggregate_class",
                    axis_title="Land use [ha]", unit="Hectares", vertical=False,
                    color=land_color_dict, ax_ticks=True, bar_width=100)
                
                st.altair_chart(bar_land_use, use_container_width=True)

                st.caption('''<div style="text-align: justify;">
                The map above shows the distribution of land use types in the
                UK. Land use types are associated with different processes,
                including food production, carbon sequestration and hybrid
                productive systems such as agroforestry and silvopasture.
                </div>''', unsafe_allow_html=True)

        with st.container():
            st.markdown("## AgriFood Calculator")
            st.caption(f'''<div style="text-align: justify;">
                        Move the ambition level sliders to explore the outcomes of
                        different interventions on key metrics of the food system,
                        including GHG emissions, sequestration and land use.                    
                        Alternatively, select an scenario from the dropdown menu
                        on the top of the side bar to automatically position
                        sliders to their pre-set values.                    
                        Detailed charts describing the effects of interventions
                        on different aspects of the food system can be found in
                        the dropdown menu at the top of the page.
                        Once you have selected the ambition levels for the
                        different interventions, enter your unique ID on the
                        field below and click the "Submit pathway" button. You
                        can change your responses as many times as you want
                        before the Stage I deadline on {stage_I_deadline}.
                        </div>''', unsafe_allow_html=True)

            user_id = st.text_input("Enter your unique ID", "AFP")
            submit_state = st.button("Submit pathway")

            # submit scenario
            if submit_state:
                submit_scenario(user_id, SSR_metric_yr, emissions_balance.sum(), ambition_levels=True, check_users=st.session_state.check_ID)

    # Emissions per food group or origin
    # ----------------------------------
    if plot_key == "CO2e emission per food group":
        col_opt, col_element, col_y = st.columns([1,1,1])
        with col_opt:
            option_key = st.selectbox("Plot options", ["Food group", "Food origin"])
        with col_element:
            element_key = st.selectbox("Food Supply Element", ["production", "food", "imports", "exports", "feed"])
        with col_y:
            y_key = st.selectbox("Food Supply Element", ["Emissions", "kCal/cap/day", "g/cap/day"])

        if y_key == "Emissions":
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
        
        st.altair_chart(f, use_container_width=True)

    # Emissions per food item from each group
    # ---------------------------------------
    elif plot_key == "CO2e emission per food item":
        emissions = datablock["impact"]["g_co2e/year"].sel(Year=slice(None, metric_yr))
        emissions_baseline = st.session_state["datablock_baseline"]["impact"]["g_co2e/year"]
        col_opt, col_element = st.columns([1,1])
        with col_opt:
            option_key = st.selectbox("Plot options", np.unique(emissions.Item_group.values))
        with col_element:
            element_key = st.selectbox("Food Supply Element", ["production", "food", "imports", "exports", "feed"])

        # plot1.plot(emissions_baseline.Year.values,
        #            emissions_baseline["food"].sel(
        #                Item=emissions_baseline["Item_group"] == option_key).sum(dim="Item"))
        
        to_plot = emissions[element_key].sel(Item=emissions["Item_group"] == option_key)/1e6

        f = plot_years_altair(to_plot, show="Item_name", ylabel="t CO2e / Year")
        f = f.configure_axis(
                labelFontSize=15,
                titleFontSize=15)
        
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

        st.altair_chart(f, use_container_width=True)
        
    # Self-sufficiency ratio as a function of time
    # --------------------------------------------
    elif plot_key == "Self-sufficiency ratio":

        option_key = st.selectbox("Plot options", ["g/cap/day", "kCal/cap/day", "g_prot/cap/day", "g_fat/cap/day"])

        SSR = datablock["food"][option_key].fbs.SSR().sel(Year=slice(None, metric_yr)) * 100

        f = plot_years_total(SSR, ylabel="Self-sufficiency ratio [%]").configure_axis(
                labelFontSize=20,
                titleFontSize=20)
        
        st.altair_chart(f, use_container_width=True)

    # Various land plots, including Land use and ALC
    # ----------------------------------------------
    elif plot_key == "Land":

        f, plot1 = plt.subplots(1, figsize=(8,8))
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
        # patches = [mpatches.Patch(color=color_list[i],
                                    # label=label_list[i]) for i in unique_index]
        # plot1.legend(handles=patches, loc="upper left")

        plot1.axis("off")
        # plot1.set_xlim(left=-500)

        col2_1, col2_2, col2_3 = st.columns((2,1.3,2))
        with col2_2:
            st.pyplot(fig=f)
        with col2_3:
            add_vertical_space(8)
            land_pctg = pctg.sum(dim=["x", "y"])
            pie = pie_chart_altair(land_pctg, show="aggregate_class", unit="ha")
            st.altair_chart(pie)
    
    if plot_key != "Summary":
        with bottom():
            from bottom import bottom_panel
            bottom_panel(datablock, metric_yr)


