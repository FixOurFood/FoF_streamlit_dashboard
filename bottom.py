import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
from streamlit_extras.stylable_container import stylable_container as sc
from utils.altair_plots import *
import pandas as pd

css_styles = """
    {
        border: 1px solid rgba(49, 51, 63, 0.5);
        border-radius: 0.5rem;
        padding: 0.2em;
    }
    """

css_styles_1 = """
    {
        padding: 0.05em;
    }
    """

def bottom_panel(datablock, metric_yr):

    # ----------------------------------------
    #               Bottom Panel
    # ----------------------------------------
    botcol1, botcol2, boltcol3 = st.columns((1, 1, 1))
    
    # -----------
    #     SSR
    # -----------

    with botcol1:
        SSR = datablock["food"]["g/cap/day"].fbs.SSR()

        SSR_metric_yr = SSR.sel(Year=metric_yr).to_numpy()
        SSR_ref = SSR.sel(Year=2020).to_numpy()

        df = pd.DataFrame({"Item":["Low", "Mid", "High"],
                           "variable":["SSR", "SSR", "SSR"],
                           "value":[SSR_ref, 1-SSR_ref, 0.2]})

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

        with sc(key="container_with_border", css_styles=css_styles):
            with sc(key="container_with_border_2", css_styles=css_styles_1):
                st.altair_chart(bars + ssr_line, use_container_width=True)

    # ----------
    #  Net zero
    # ----------
    
    with botcol2:
        emissions = datablock["impact"]["g_co2e/year"]["production"].sel(Year=metric_yr)/1e6
        emissions = emissions.fbs.group_sum(coordinate="Item_origin", new_name="Item")
        seq_da = datablock["impact"]["co2e_sequestration"].sel(Year=metric_yr)

        bars_emissions = plot_single_bar_altair(emissions, show="Item", x_axis_title="Net-zero meter",
                                          xmin=-3e8, xmax=3e8)
        bars_seq = plot_single_bar_altair(-seq_da, show="Item", x_axis_title="Net-zero meter",
                                          xmin=-3e8, xmax=3e8)

        zero_line = alt.Chart(pd.DataFrame({
            'Zero': 0,
            'color': ['black']
            })).mark_rule().encode(
            x='Zero:Q',
            tooltip='Zero:Q',
            color=alt.Color('color:N', scale=None),
            strokeWidth=alt.value(4)
        )

        total_emissions = (emissions.sum()-seq_da.sum()).to_numpy()

        emissions_line = alt.Chart(pd.DataFrame({
            'Total emissions': total_emissions,
            'color': ['red']
            })).mark_rule().encode(
            x='Total emissions:Q',
            tooltip='Total emissions:N',
            color=alt.Color('color:N', scale=None),
            strokeWidth=alt.value(4)
        )

        c = bars_emissions + bars_seq + zero_line + emissions_line

        # Using double containers because single ones are covered by the chart
        with sc(key="container_with_border", css_styles=css_styles):
            with sc(key="container_with_border_1", css_styles=css_styles_1):
                st.altair_chart(c, use_container_width=True)

    # ----------
    #  Land use
    # ----------

    with boltcol3:

        pctg = datablock["land"]["percentage_land_use"]
        totals = pctg.sum(dim=["x", "y"])
        bar_land_use = plot_single_bar_altair(totals, show="aggregate_class", x_axis_title="Land use")

        with sc(key="container_with_border", css_styles=css_styles):
            with sc(key="container_with_border_1", css_styles=css_styles_1):
                st.altair_chart(bar_land_use, use_container_width=True)
