import xarray as xr
import numpy as np
from agrifoodpy.food.food_supply import scale_food

from afp_config import *
from helper_functions import *

def ruminant_consumption_model(food, ruminant, n_scale):

    scale_past_ruminant = xr.DataArray(data = np.ones(59),
                                        coords = {"Year":np.arange(1961,2020)})

    scale_future_ruminant = xr.DataArray(data = 1-(ruminant/100)*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020),
                                        coords = {"Year":np.arange(2020,2101)})

    scale_ruminant = xr.concat([scale_past_ruminant, scale_future_ruminant], dim="Year")   

    out = scale_food(food=food,
                         scale= scale_ruminant,
                         origin="imports",
                         items=groups["RuminantMeat"],
                         constant=True,
                         fallback="exports")
    
    return out

def meatfree_consumption_model(food, meatfree, extra_items, n_scale):

    scale_past_meatfree = xr.DataArray(data = np.ones(59),
                                       coords = {"Year":np.arange(1961,2020)})
    
    scale_future_meatfree = xr.DataArray(data = 1-(meatfree/7)*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020),
                                         coords = {"Year":np.arange(2020,2101)})
    
    scale_meatfree = xr.concat([scale_past_meatfree, scale_future_meatfree], dim="Year")

    # add extra items
    meatfree_items = np.concatenate((groups["RuminantMeat"], groups["OtherMeat"]))
    for item in extra_items:
        meatfree_items = np.concatenate((meatfree_items, groups[item]))

    out = scale_food(food=food,
                     scale= scale_meatfree,
                     origin="imports",
                     items=meatfree_items,
                     constant=True,
                     fallback="exports")
    
    return out

def food_waste_model(food, waste, rda_kcal, n_scale):

    # reduce production and food consumed based on kcal
    waste_to_reduce = waste/100*(food["food"].sel(Year=2100).sum(dim="Item") - rda_kcal)
    waste_factor = waste_to_reduce / food["food"].sel(Year=2100).sum(dim="Item")
    waste_factor = waste_factor.to_numpy()

    # scale food from waste slider
    scale_past_waste = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future_waste = xr.DataArray(data = 1 - waste_factor*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020), coords = {"Year":np.arange(2020,2101)})
    scale_waste = xr.concat([scale_past_waste, scale_future_waste], dim="Year")

    out = food.copy(deep=True)
    out["food"] *= scale_waste
    delta = food["food"] - out["food"]
    out["production"] -= delta
    out["imports"] += out["production"].where(out["production"] < 0)
    out["production"] = out["production"].where(out["production"] > 0, other=0)

    return out

def spare_ALC_model(food, LC, spare_scale, land_type, grades, items, n_scale):
    
    scaled_LC_type = LC.copy(deep=True)

    delta_spared = LC.loc[{"use":land_type}] * spare_scale/100 * np.isin(ALC.grade, grades)

    scaled_LC_type.loc[{"use":"spared"}] += delta_spared
    scaled_LC_type.loc[{"use":land_type}] -= delta_spared

    # scale animal products from scale_sparing_pasture slider
    scale_past = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future = xr.DataArray(data = 1-(spare_scale)*logistic(2**(1-n_scale), 10+5*n_scale, 0, 2101-2020), coords = {"Year":np.arange(2020,2101)})
    scale = xr.concat([scale_past, scale_future], dim="Year")

    out = scale_add(food=food,
                element_in="production",
                element_out="imports",
                items= items,
                scale= scale)

    return scaled_LC_type, out

def forested_land_model(LC, foresting_spared, grades):

    scaled_LC_type = LC.copy(deep=True)

    delta_spared_woodland = scaled_LC_type.loc[{"use":"spared"}] * foresting_spared/100 * np.isin(ALC.grade, grades)
    
    scaled_LC_type.loc[{"use":"woodland"}] += delta_spared_woodland
    scaled_LC_type.loc[{"use":"spared"}] -= delta_spared_woodland

    return scaled_LC_type

def sequestered_carbon_model(pasture_sparing, arable_sparing, foresting_spared, co2_seq):

    spared_land_area_pasture = np.sum(use_by_grade[4:5,1])*pasture_sparing
    spared_land_area_arable= np.sum(use_by_grade[4:5,0])*arable_sparing

    spared_land_area = spared_land_area_arable + spared_land_area_pasture

    forested_spared_land_area = spared_land_area * foresting_spared / 100

    co2_seq_arable = spared_land_area_arable * foresting_spared / 100 * co2_seq
    co2_seq_pasture = spared_land_area_pasture * foresting_spared / 100 * co2_seq
    co2_seq_total = forested_spared_land_area * co2_seq

    return co2_seq_total, spared_land_area, forested_spared_land_area
