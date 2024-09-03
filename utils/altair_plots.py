import altair as alt
import xarray as xr
import numpy as np
import pandas as pd
import streamlit as st
from glossary import *

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
            # opacity=alt.condition(selection, alt.value(0.5), alt.value(0.8)),
            tooltip=[alt.Tooltip(f'{show}:N', title=show.replace("_", " ")),
                     alt.Tooltip('Year'),
                     alt.Tooltip('sum(value)', title='Total', format=".2f")],
            ).add_params(selection).properties(height=550)
    
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
    ).mark_line(color=color).properties(height=550)

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
        tooltip=['Item:N', 'value:Q'],
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

def plot_single_bar_altair(da, show="Item", x_axis_title=None, xmin=None, xmax=None, unit=""):
    df = da.to_dataframe().reset_index().fillna(0)
    df = df.melt(id_vars=show, value_vars=da.name)
    
    # Create a new column for the tooltip with units
    df['value_with_unit'] = df['value'].apply(lambda x: f"{x:.3f} {unit}")

    # Set yaxis limits
    if xmax is None:
        xmax = da.sum(dim=show).max().item()
    if xmin is None:
        xmin = np.min([da.sum(dim=show).min().item(), 0])

    c = alt.Chart(df).mark_bar().encode(
        x = alt.X('sum(value):Q',
                  title=x_axis_title,
                  axis=alt.Axis(labels=False),
                  scale=alt.Scale(domain=(xmin, xmax))),
        order=alt.Order(sort='descending'),
        color=alt.Color(show, title=None, legend=None, scale=alt.Scale(scheme='category20b')),
        tooltip=[alt.Tooltip(f'{show}:N'),
                 alt.Tooltip('value_with_unit:N', title='Total')],
    ).properties(height=80)

    return c

def pie_chart_altair(da, show="Item"):
    df = da.to_dataframe().reset_index().fillna(0)
    df = df.melt(id_vars=show, value_vars=da.name)

    c = alt.Chart(df).mark_arc().encode(
        theta=alt.Theta("value:Q", sort=None),
        color=alt.Color(show,
                        sort=None,
                        title="Land type",
                        scale=alt.Scale(domain=list(land_color_dict.keys()),
                                        range=list(land_color_dict.values()))),
        tooltip=[alt.Tooltip(f'{show}:N', title="Type"),
                 alt.Tooltip('sum(value)', title='Total', format=".2f")],
    ).resolve_scale(theta='independent')

    return c