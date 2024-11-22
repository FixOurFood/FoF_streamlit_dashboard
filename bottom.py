import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
from utils.altair_plots import *
import pandas as pd

def bottom_panel(datablock, metric_yr):

    # ----------------------------------------
    #               Bottom Panel
    # ----------------------------------------
    _, botcol1, botcol2, boltcol3 = st.columns((0.6, 1, 1, 1))
    
    # -----------
    #     SSR
    # -----------

    with botcol2:
        SSR = datablock["food"]["g/cap/day"].fbs.SSR()

        SSR_metric_yr = SSR.sel(Year=metric_yr).to_numpy()
        SSR_ref = SSR.sel(Year=2020).to_numpy()

        df = pd.DataFrame({"Item":["Low", "Mid", "High"],
                           "variable":["SSR", "SSR", "SSR"],
                           "value":[float(SSR_ref), float(1-SSR_ref), 0.2]})

        bars = alt.Chart(df).mark_bar().encode(
            x=alt.X("sum(value):Q",
                    title="Self-sufficiency ratio",
                    axis=alt.Axis(labels=False)),
            color=alt.Color("Item",
                            title=None,
                            legend=None,
                            scale=alt.Scale(domain=["High", "Mid", "Low"],
                                            range=["#008000", "#FF8800", "#FF0000"])),
            tooltip="Item:N",
            order=alt.Order("value:Q", sort="descending")
        ).properties(height=80)

        ssr_line = alt.Chart(pd.DataFrame({
            'Self-sufficiency ratio': SSR_metric_yr,
            'color': ['black']
            })).mark_rule().encode(
            x='Self-sufficiency ratio:Q',
            tooltip='Self-sufficiency ratio:Q',
            color=alt.Color('color:N', scale=None),
            strokeWidth=alt.value(4)
        )

        ref_line = alt.Chart(pd.DataFrame({
                    'value': 0.682,
                    'color': ['blue']
                    })).mark_rule(
                        color="blue",
                        thickness=1,
                    ).encode(x="value")

        with st.container(border=True):
            bar1, bar2 = st.columns((10, 1))
            with bar1:
                st.altair_chart(bars + ssr_line + ref_line, use_container_width=True)
            with bar2:
                st.text("")
                st.text("", help="""Self sufficiency ratio (SSR) is the ratio of the
                        amount of food produced by a country to the amount of
                        food it would need to meet its own food needs.""")

    # ----------
    #  Net zero
    # ----------
    
    with botcol1:

        emissions = datablock["impact"]["g_co2e/year"]["production"].sel(Year=metric_yr)/1e6
        emissions = emissions.fbs.group_sum(coordinate="Item_origin", new_name="Item")
        seq_da = datablock["impact"]["co2e_sequestration"].sel(Year=metric_yr)

        if st.session_state.emission_factors == "NDC 2020":

            total_emissions = emissions.sum(dim="Item").values/1e6
            total_seq = seq_da.sel(Item=["Broadleaved woodland", "Coniferous woodland"]).sum(dim="Item").values/1e6
            total_removals = seq_da.sel(Item=["BECCS from waste", "BECCS from overseas biomass", "BECCS from land", "DACCS"]).sum(dim="Item").values/1e6

            emissions_balance = xr.DataArray(data = list(sector_emissions_dict.values()),
                                    name="Sectoral emissions",
                                    coords={"Sector": list(sector_emissions_dict.keys())})
            
            emissions_balance.loc[{"Sector": "Agriculture"}] = total_emissions
            emissions_balance.loc[{"Sector": "Land use sinks"}] = -total_seq
            emissions_balance.loc[{"Sector": "Removals"}] = -total_removals

            c = plot_single_bar_altair(emissions_balance, show="Sector",
                axis_title="Sectoral emissions and removals", unit="Mt CO2e / year", vertical=False,
                mark_total=True, show_zero=True)


        elif st.session_state.emission_factors == "PN18":

            c = plot_single_bar_altair(xr.concat([emissions, -seq_da], dim="Item"), show="Item",
                axis_title="Emissions - Sequestration balance",
                ax_min=-3e8, ax_max=3e8, unit="tCO2e", vertical=False,
                mark_total=True, show_zero=True, reference=92.39)

        with st.container(border=True):
            bar1, bar2 = st.columns((10, 1))
            with bar1:
                st.altair_chart(c, use_container_width=True)
            with bar2:
                    st.text("")
                    st.text("", help="""Balance between emissions from food production and
                        agricultural, forestry and land use sequestration.""")

    # ----------
    #  Land use
    # ----------

    with boltcol3:

        pctg = datablock["land"]["percentage_land_use"]
        totals = pctg.sum(dim=["x", "y"])
        bar_land_use = plot_single_bar_altair(totals, show="aggregate_class",
                                              axis_title="Land use", unit="Hectares",
                                              vertical=False, color=land_color_dict)

        with st.container(border=True):
            bar1, bar2 = st.columns((10, 1))
            with bar1:
                st.altair_chart(bar_land_use, use_container_width=True)
            with bar2:
                st.text("")
                st.text("", help="""Distribution of land use in the UK. Different land uses
                        provide sequestration, food production, or biodiversity.""")
