import altair as alt
import xarray as xr
import numpy as np
import pandas as pd
import streamlit as st

def plot_years_altair(food, show="Item", **kwargs):

    # If no years are found in the dimensions, raise an exception
    sum_dims = list(food.coords)
    if "Year" not in sum_dims:
        raise TypeError("'Year' dimension not found in array data")

    df = food.to_dataframe().reset_index().fillna(0)
    df = df.melt(id_vars=sum_dims, value_vars=food.name)

#     selection = alt.selection_multi(fields=[show])
    selection = alt.selection_single(on='mouseover')

    c = alt.Chart(df).mark_area().encode(
            x=alt.X('Year:O', axis=alt.Axis(values = np.linspace(1970, 2090, 7))),
            y=alt.Y('sum(value):Q', axis=alt.Axis(format="e", title='Consumed food CO2e emissions [t CO2e / year]')),
            color=alt.Color(f'{show}:N', scale=alt.Scale(scheme='category20b')),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
            tooltip=f'{show}:N'
            ).add_selection(selection).properties(height=500)

    return c

def plot_years_total(food):
    years = food.Year.values
    total = food.sum(dim="Item")

    df = pd.DataFrame(data={"Year":years, "value":total})
    c = alt.Chart(df).encode(
    alt.X('Year:O', axis=alt.Axis(values = np.linspace(1970, 2090, 7))),
    alt.Y('sum(value):Q', axis=alt.Axis(format="e", title='Consumed food CO2e emissions [t CO2e / year]'))
    ).mark_line(color='red')

    return c

def plot_bars_altair(food, xlimit, show="Item", x_axis_title=''):
    df = food.to_dataframe().reset_index().fillna(0)
    df = df.melt(id_vars=show, value_vars=["production", "imports", "exports", "stock", "losses", "processing", "other", "feed", "seed", "food"])
    df["value_start"] = 0
    df["value_end"] = 0

    for i in range(4,20):
        if i%2==0:
            temp = df.iloc[i].copy()
            df.iloc[i] = df.iloc[i+1]
            df.iloc[i+1] = temp
        else:
            pass

    cumul = 0
    for i in range(4):
        df.loc[i, "value_start"] = cumul
        cumul += df.loc[i, "value"]
        df.loc[i, "value_end"] = cumul

    cumul = 0
    for i in reversed(range(4,20)):
        df.loc[i, "value_start"] = cumul
        cumul += df.loc[i, "value"]
        df.loc[i, "value_end"] = cumul

    source = df

    selection = alt.selection_single(on='mouseover')

    c = alt.Chart(source).mark_bar().encode(
        y = alt.Y('variable', sort=None, axis=alt.Axis(title='')),
        x2 ='value_start:Q',
        x = alt.X('value_end:Q', scale=alt.Scale(domain=(0, xlimit)), axis=alt.Axis(title=x_axis_title)),
        # x = alt.X('value_end:Q'),
        color='Item',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.7)),
        tooltip='Item:N',
        ).add_selection(selection).properties(height=500)

    return c

def plot_land_altair(land):
    df = land.to_dataframe().reset_index()
    df = df.melt(id_vars = ['x', 'y'], value_vars = 'grade')
    c = alt.Chart(df).mark_rect().encode(
        x=alt.X('x:O', axis=None),
        y=alt.Y('y:O', scale=alt.Scale(reverse=True), axis=None),
        color='value:Q',
        tooltip='value',
        ).properties(width=300, height=500)

    return c
