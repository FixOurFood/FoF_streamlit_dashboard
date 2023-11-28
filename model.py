import xarray as xr
import numpy as np
from agrifoodpy.food.food_supply import scale_food

from afp_config import *
from helper_functions import *

def ruminant_consumption_model(food, ruminant, n_scale):

    scale_past_ruminant = xr.DataArray(data = np.ones(59),
                                        coords = {"Year":np.arange(1961,2020)})

    scale_future_ruminant = xr.DataArray(data = 1-(ruminant/100)*logistic(n_scale),
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
    
    scale_future_meatfree = xr.DataArray(data = 1-(meatfree/7)*logistic(n_scale),
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
    scale_future_waste = xr.DataArray(data = 1 - waste_factor*logistic(n_scale), coords = {"Year":np.arange(2020,2101)})
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

    # delta_spared = LC.loc[{"use":land_type}] * spare_scale/100 * np.isin(ALC.grade, grades)

    # scaled_LC_type.loc[{"use":"spared"}] += delta_spared
    # scaled_LC_type.loc[{"use":land_type}] -= delta_spared

    # scale animal products from scale_sparing_pasture slider
    scale_past = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    scale_future = xr.DataArray(data = 1-(spare_scale)*logistic(n_scale), coords = {"Year":np.arange(2020,2101)})
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

def sequestered_carbon_model(pasture_sparing, arable_sparing, foresting_spared, co2_seq, n_scale):

    scale_past = xr.DataArray(data = np.zeros(59),
                                       coords = {"Year":np.arange(1961,2020)})
    
    scale_future = xr.DataArray(data = logistic(n_scale),
                                         coords = {"Year":np.arange(2020,2101)})
    
    scale = xr.concat([scale_past, scale_future], dim="Year")

    spared_land_area_pasture = np.sum(use_by_grade[4:5,1])*pasture_sparing
    spared_land_area_arable= np.sum(use_by_grade[4:5,0])*arable_sparing

    spared_land_area = spared_land_area_arable + spared_land_area_pasture
    forested_spared_land_area = spared_land_area * foresting_spared / 100

    co2_seq_arable = spared_land_area_arable * foresting_spared / 100 * co2_seq
    co2_seq_pasture = spared_land_area_pasture * foresting_spared / 100 * co2_seq
    co2_seq_total = forested_spared_land_area * co2_seq

    return co2_seq_arable*scale, co2_seq_pasture*scale, co2_seq_total*scale, spared_land_area*scale

def cultured_meat_uptake_model(food, labmeat, n_scale, items, new_code=5000):
    
    scale_past_labmeat = xr.DataArray(data = np.ones(59),
                                       coords = {"Year":np.arange(1961,2020)})
    
    scale_future_labmeat = xr.DataArray(data = 1-(labmeat/100)*logistic(n_scale),
                                         coords = {"Year":np.arange(2020,2101)})
    
    scale_labmeat = xr.concat([scale_past_labmeat, scale_future_labmeat], dim="Year")

    food_out = food.copy(deep=True)

    food_out.loc[{"Item":items}] *= scale_labmeat
    
    delta = (food-food_out).sel(Item=items).sum(dim="Item")

    food_out.loc[{"Item":new_code}] += delta

    return food_out

def ghge_innovation(co2e, max_ghge, items, n_scale):

    co2e_scaled = co2e.copy(deep=True)

    scale_ones = xr.DataArray(data = np.ones(140), coords = {"Year":np.arange(1961,2101)})
    co2e_scaled = co2e_scaled*scale_ones
    scale_past_co2e = xr.DataArray(data = np.ones(59), coords = {"Year":np.arange(1961,2020)})
    
    scale_future_co2e_g_crop = xr.DataArray(data = 1-(max_ghge/100/4)*logistic(n_scale),
                                         coords = {"Year":np.arange(2020,2101)})

    scale_co2e_g = xr.concat([scale_past_co2e, scale_future_co2e_g_crop], dim="Year")
    co2e_new = co2e_g.sel({"Item":items}) * scale_co2e_g

    co2e_scaled.loc[{"Item":items}] = co2e_new

    return co2e_scaled

def engineered_sequestration_model(food, sequestration_dataset, waste_BECCS, overseas_BECCS, land_BECCS, DACCS, n_scale):
    # waste_BECCS in Mt CO2e / yr
    # overseas_BECCS in Mt CO2e / yr
    # land_BECCS in percentage
    # DACCS in Mt CO2e / yr

    scale_past = xr.DataArray(data = np.zeros(59), coords = {"Year":np.arange(1961,2020)})
    scale_future = xr.DataArray(data = logistic(n_scale), coords = {"Year":np.arange(2020,2101)})
    scale = xr.concat([scale_past, scale_future], dim="Year")

    waste_BECCS_arr = waste_BECCS * scale * 1e6
    overseas_BECCS_arr = overseas_BECCS * scale * 1e6
    DACCS_arr = DACCS * scale * 1e6

    waste_BECCS_arr.name = "BECCS from waste"
    DACCS_arr.name = "DACCS"
    overseas_BECCS_arr.name = "BECCS from overseas"

    sequestration_dataset.update({"BECCS from waste":waste_BECCS_arr,
                                  "BECCS from overseas":overseas_BECCS_arr,
                                  "DACCS":DACCS_arr})
    
    print(land_BECCS / 100 * scale)

    food = scale_add(food=food,
                    element_in="production",
                    element_out="imports",
                    items = plant_items,
                    scale = 1 - land_BECCS / 100 * scale)

    return food, sequestration_dataset