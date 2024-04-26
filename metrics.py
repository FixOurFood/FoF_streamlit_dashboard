import streamlit as st
import pandas as pd
import numpy as np
from millify import millify
help = pd.read_csv(st.secrets["tooltips_url"], dtype='string')

def metrics(datablock, metric_yr=2100):

    # ----------------------------
    #       Metrics block
    # ----------------------------

    st.write("## Metrics")

    # ----------------------------
    # Environment and biodiversity
    # ----------------------------
    with st.expander("Environment and biodiversity", expanded=True):


        # TODO: This metric is only really useful if we scale to global emissions.
        #       For now, we are only interested in the UK emissions, which are negligible in terms
        #       of contribution to global warming

        # T = datablock["impact"]["T"]
        # st.metric(label="**:thermometer: Surface temperature warming by 2100**",
        #         value="{:.2f} °C".format(T.sel(Year=2020.5) - T.sel(Year=metric_yr+0.5)),
        #         # delta="{:.2f} °C - Compared to BAU".format((T[-1] - T[-80])-(T_base[-1] - T_base[-80])), delta_color="inverse",
        #         help=help["metrics"][0])
        co2_seq_da = datablock["impact"]["co2e_sequestration"]
        co2_seq_forest = co2_seq_da.sel(Item=[
            "Broadleaved woodland",
            "Coniferous woodland"
        ]).sum(dim="Item")

        co2_seq_ccs = co2_seq_da.sel(Item=[
            "BECCS from waste",
            "BECCS from overseas biomass",
            "BECCS from land",
            "DACCS"
        ]).sum(dim="Item")

        st.metric(label="**:chart_with_downwards_trend: Total carbon sequestration by forested agricultural land**",
                value=f"{millify(co2_seq_forest.sel(Year=metric_yr), precision=1)} t CO2/yr",
                help=help["metrics"][4])
        
        st.metric(label="**:chart_with_downwards_trend: Total carbon sequestration by engineered Carbon Capture and Storage**",
                value=f"{millify(co2_seq_ccs.sel(Year=metric_yr), precision=1)} t CO2/yr",
                help=help["metrics"][3])
        
    # --------
    # Land use
    # --------
    with st.expander("Land use", expanded=True):
        pctg = datablock["land"]["percentage_land_use"]

        land_spared_area = pctg.sel({"aggregate_class":"Spared"}).sum().to_numpy()
        land_forest_area = pctg.sel({"aggregate_class":["Broadleaf woodland", "Coniferous woodland"]}).sum().to_numpy()

        st.metric(label="**:sunrise_over_mountains: Total area of agricultural spared land**",
                value=f"{millify(land_spared_area, precision=2)} ha",
                help=help["metrics"][2])

        st.metric(label="**:deciduous_tree: Total area of forest land**",
                value=f"{millify(land_forest_area, precision=2)} ha",
                help=help["metrics"][3])

    # --------------
    # Socio-economic
    # --------------
    with st.expander("Socio-economic", expanded=True):

        cost = datablock["impact"]["cost"]
        total_spending = cost.sel(Year=np.arange(2020, metric_yr)).sum().to_numpy()

        st.metric(label="**:factory: Total public spending on CCS**",
                value=f"{total_spending / 1e9:.2f} billion £",

                help=help["metrics"][5])
        
        st.metric(label="**:farmer: Public spending on farming subsidy**",
                # value="£100 billion",
                value=0,
                help=help["metrics"][6])

    # ---------------
    # Food production
    # ---------------
    with st.expander("Food production", expanded=True):

        SSR = datablock["food"]["g/cap/day"].fbs.SSR()
        food_orig = datablock["food"]["g/cap/day"]
        animal_food = food_orig["food"].fbs.group_sum("Item_origin").sel(Item_origin="Animal Products")

        st.metric(label="**:factory: Change in animal origin food consumption**",
                value="{:.1f} %".format(100 - 100*animal_food.sel(Year=metric_yr) / animal_food.sel(Year=2020)),
                help=help["metrics"][7])
        
        st.metric(label="**:bar_chart: Food Self-sufficiency ratio**",
                value="{:.2f} %".format(100*SSR.sel(Year=metric_yr)),
                help=help["metrics"][8])