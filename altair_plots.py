import altair as alt
import xarray as xr
import numpy as np
import pandas as pd
import streamlit as st

def plot_years_altair(food, show="Item", ylabel=None, colors=None, ymin=None, ymax=None):

    # If no years are found in the dimensions, raise an exception
    sum_dims = list(food.coords)
    if "Year" not in sum_dims:
        raise TypeError("'Year' dimension not found in array data")

    # Set yaxis limits
    if ymax is None:
        ymax = food.sum(dim="Item").max().item()
    if ymin is None:
        ymin = food.sum(dim="Item").min().item()
        if ymin > 0: ymin = 0

    # Create dataframe for altair
    df = food.to_dataframe().reset_index().fillna(0)
    df = df.melt(id_vars=sum_dims, value_vars=food.name)

#     selection = alt.selection_multi(fields=[show])
    selection = alt.selection_point(on='mouseover')

    if colors is None:
        color_scale = alt.Scale(scheme='category20b')
    else:
        show_list = np.unique(food[show].values)
        color_scale = alt.Scale(domain=show_list, range=colors)

    # Create altair chart
    c = alt.Chart(df).mark_area().encode(
            x=alt.X('Year:O', axis=alt.Axis(values = np.linspace(1960, 2100, 8))),
            y=alt.Y('sum(value):Q', axis=alt.Axis(format="~s", title=ylabel, ), scale=alt.Scale(domain=[ymin, ymax])),
            # color=alt.Color(f'{show}:N', scale=alt.Scale(scheme='category20b')),
            color=alt.Color(f'{show}:N', scale=color_scale),
            opacity=alt.condition(selection, alt.value(0.8), alt.value(0.2)),
            tooltip=f'{show}:N'
            ).add_params(selection).properties(height=600)
    
    return c

def plot_years_total(food, ylabel=None, sumdim=None, color="red"):
    years = food.Year.values
    if sumdim is not None and sumdim in food.dims:
        total = food.sum(dim="Item")
    else:
        total = food

    df = pd.DataFrame(data={"Year":years, "value":total})
    c = alt.Chart(df).encode(
        alt.X('Year:O', axis=alt.Axis(values = np.linspace(1960, 2100, 8))),
        alt.Y('sum(value):Q', axis=alt.Axis(format="~s", title=ylabel))
    ).mark_line(color=color)

    return c

def plot_bars_altair(food, show="Item", x_axis_title='', xlimit=None):

    n_origins = len(food.Item.values)

    df = food.to_dataframe().reset_index().fillna(0)
    df = df.melt(id_vars=show, value_vars=["production", "imports", "exports", "stock", "losses", "processing", "other", "feed", "seed", "food"])
    df["value_start"] = 0.
    df["value_end"] = 0.

    for i in range(2*n_origins,10*n_origins):
        if i % n_origins==0:
            temp = df.iloc[i].copy()
            df.iloc[i] = df.iloc[i+1]
            df.iloc[i+1] = temp
        else:
            pass

    cumul = 0
    for i in range(2*n_origins):
        df.loc[i, "value_start"] = cumul
        cumul += df.loc[i, "value"]
        df.loc[i, "value_end"] = cumul

    cumul = 0
    for i in reversed(range(2*n_origins,10*n_origins)):
        df.loc[i, "value_start"] = cumul
        cumul += df.loc[i, "value"]
        df.loc[i, "value_end"] = cumul

    source = df

    selection = alt.selection_point(on='mouseover')

    c = alt.Chart(source).mark_bar().encode(
        y = alt.Y('variable', sort=None, axis=alt.Axis(title='')),
        x2 ='value_start:Q',
        x = alt.X('value_end:Q', scale=alt.Scale(domain=(0, xlimit)), axis=alt.Axis(title=x_axis_title)),
        # x = alt.X('value_end:Q', axis=alt.Axis(title=x_axis_title)),
        # x = alt.X('value_end:Q'),
        # color=alt.Color('Item'),
        color=alt.Color('Item', scale=alt.Scale(domain=["Animal Products", "Cultured Product", "Vegetal Products"], range=["red", "blue", "green"])),
        opacity=alt.condition(selection, alt.value(0.9), alt.value(0.5)),
        tooltip='Item:N',
        ).add_params(selection).properties(height=500)

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
