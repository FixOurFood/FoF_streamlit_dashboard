import altair as alt
import xarray as xr
import numpy as np
import pandas as pd
import streamlit as st
from glossary import *

import base64
from io import BytesIO
from PIL import Image

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
                     alt.Tooltip('sum(value)', title='Total' )],
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

def plot_single_bar_altair(da, show="Item", axis_title=None,
                                    ax_min=None, ax_max=None, unit="",
                                    vertical=True, mark_total=False,
                                    bar_width=80, show_zero=False,
                                    ax_ticks=False):
    
    df_pos = da.where(da>0).to_dataframe().reset_index().fillna(0)
    df_neg = da.where(da<0).to_dataframe().reset_index().fillna(0)

    df_pos = df_pos.melt(id_vars=show, value_vars=da.name)
    df_neg = df_neg.melt(id_vars=show, value_vars=da.name)
    
    # Create a new column for the tooltip with units
    df_pos['value_with_unit'] = df_pos['value'].apply(lambda x: f"{x:.2f} {unit}")
    df_neg['value_with_unit'] = df_neg['value'].apply(lambda x: f"{x:.2f} {unit}")

    # Set yaxis limits
    if ax_max is None:
        ax_max = da.where(da>0).sum(dim=show).max().item()
    if ax_min is None:
        ax_min = np.min([da.where(da<0).sum(dim=show).min().item(), 0])

    if vertical == True:
        chart_params = {"y":alt.Y('sum(value):Q',
                            title=axis_title,
                            axis=alt.Axis(labels=ax_ticks),
                            scale=alt.Scale(domain=(ax_min, ax_max))),
                        "x":alt.X('variable', axis=alt.Axis(labels=False, title=None))}
        icon_params = {"y": "total", "x": "variable"}
    else:
        chart_params = {"x":alt.X('sum(value):Q',
                            title=axis_title,
                            axis=alt.Axis(labels=ax_ticks),
                            scale=alt.Scale(domain=(ax_min, ax_max))),
                        "y":alt.Y('variable', axis=alt.Axis(labels=False, title=None))}
        icon_params = {"x": "total", "y": "variable"}

    # Plot positive values
    c = alt.Chart(df_pos).mark_bar().encode(
        **chart_params,
        order=alt.Order(sort='descending'),
        color=alt.Color(show, title=None, legend=None, scale=alt.Scale(scheme='category20b')),
        tooltip=[alt.Tooltip(f'{show}:N'),
                 alt.Tooltip('value_with_unit:N', title='Total')],
    )

    # Plot negative values
    c += alt.Chart(df_neg).mark_bar().encode(
        **chart_params,
        order=alt.Order(sort='descending'),
        color=alt.Color(show, title=None, legend=None, scale=alt.Scale(scheme='category20b')),
        tooltip=[alt.Tooltip(f'{show}:N'),
                 alt.Tooltip('value_with_unit:N', title='Total')],
    )

    # Add a marker for the total
    if mark_total == True:

        img_path = "images/rhomboid.png"
        pil_image = Image.open(img_path)
        output = BytesIO()
        pil_image.save(output, format='PNG')

        base64_img = "data:image/png;base64," + base64.b64encode(output.getvalue()).decode()

        total = da.sum(dim=show).item()
        source = pd.DataFrame.from_records([
            {"variable": da.name, "total": total, "total_with_unit": f"{total:.2f} {unit}",
            "img": base64_img},
        ])        

        c += alt.Chart(source).mark_image(
            width=25,
            height=25
        ).encode(
            **icon_params,
            url='img',
            tooltip=[alt.Tooltip('total_with_unit:N', title='Total')]
        )
    
    # Add a line for zero
    if show_zero == True:
        zero_line_params = {"y": "value"} if vertical else {"x": "value"}
        c += alt.Chart(pd.DataFrame({
            'value': 0.,
            'color': ['black']
            })).mark_rule(
                color="black",
                thickness=2,
            ).encode(
                **zero_line_params
        )

    # Set bar width
    if vertical:
        c = c.properties(width=bar_width)
    else:
        c = c.properties(height=bar_width)

    return c

def pie_chart_altair(da, show="Item"):
    df = da.to_dataframe().reset_index().fillna(0)
    df = df.melt(id_vars=show, value_vars=da.name)

    print(df)

    segment_order = ['Broadleaf woodland',
                     'Coniferous woodland',
                     'Arable',
                     'Improved grassland',
                     'Semi-natural grassland',
                     'Mountain, heath and bog',
                     'Saltwater',
                     'Freshwater',
                     'Coastal',
                     'Built-up areas and gardens',
                     'Spared',
                     'BECCS',
                     'Silvopasture',
                     'Agroforestry',]

    c = alt.Chart(df).mark_arc().encode(
        theta=alt.Theta("value:Q"),
        color=alt.Color(show+':N',
                        title="Land type",
                        scale=alt.Scale(domain=segment_order,
                                        range=list(land_color_dict.values()))
                                        ),
        tooltip=[alt.Tooltip(f'{show}:N', title="Type"),
                 alt.Tooltip('sum(value)', title='Total', format=".2f")],
        order=alt.Order('aggregate_class:N')
    )

    return c