import numpy as np
import xarray as xr


from agrifoodpy_data.food import FAOSTAT, Nutrients_FAOSTAT
from agrifoodpy_data.impact import PN18_FAOSTAT
from agrifoodpy_data.population import UN
from agrifoodpy_data.land import ALC_1000 as ALC
from agrifoodpy_data.land import UKCEH_LC_1000

from agrifoodpy.impact.model import fbs_impacts, fair_co2_only
from utils.pipeline import Pipeline

datablock = {}
datablock["food"] = {}
datablock["land"] = {}
datablock["impact"] = {}
datablock["population"] = {}

# ----------------------
# Regional configuration
# ----------------------

area_pop = 826 #UK
# area_pop = 900 # WORLD
area_pop_world = 900 #WORLD

area_fao = 229 #UK
# area_fao = 5000 # WORLD
years = np.arange(1961, 2101)

# ------------------------------
# Select population data from UN
# ------------------------------

pop = UN.Medium.sel(Region=[area_pop, area_pop_world], Year=years, Datatype="Total")*1000
# pop_world = UN.Medium.sel(Region=area_pop_world, Year=years, Datatype="Total")*1000

# pop_past = pop_uk[pop_uk["Year"] < 2021]
# pop_future = pop_uk[pop_uk["Year"] >= 2021]

proj_pop = pop.sel(Region=area_pop_world, Year=np.arange(2021, 2101)) / \
           pop.sel(Region=area_pop_world, Year=2020)

datablock["population"]["population"] = pop

# -----------------------------------------
# Select food consumption data from FAOSTAT
# -----------------------------------------

FAOSTAT *= 1
# 1000 T / year
food_uk = FAOSTAT.sel(Region=229)
datablock["food"]["1000 T/year"] = food_uk

# ----------------
# Emission factors
# ----------------

scale_ones = xr.DataArray(data = np.ones_like(food_uk.Year.values),
                          coords = {"Year":food_uk.Year.values})
datablock["impact"]["gco2e/gfood"] = PN18_FAOSTAT["GHG Emissions"] * scale_ones


# --------------------------
# UK Per capita daily values
# --------------------------

# g_food / cap / day
pop_past_uk = pop.sel(Year=np.arange(1961,2021), Region=area_pop)
food_cap_day_baseline = food_uk*1e9/pop_past_uk/365.25

datablock["food"]["g/cap/day"] = food_cap_day_baseline

# kCal, g_prot, g_fat / g_food
qty_g = Nutrients_FAOSTAT[["kcal", "protein", "fat"]].sel(Region=area_fao, Year=2020)
qty_g = qty_g.where(np.isfinite(qty_g), other=0)

datablock["food"]["kCal/g_food"] = qty_g["kcal"]
datablock["food"]["g_prot/g_food"] = qty_g["protein"]
datablock["food"]["g_fat/g_food"] = qty_g["fat"]

# kCal, g_prot, g_fat, g_co2e / cap / day
kcal_cap_day_baseline = food_cap_day_baseline * datablock["food"]["kCal/g_food"]
prot_cap_day_baseline = food_cap_day_baseline * datablock["food"]["g_prot/g_food"]
fats_cap_day_baseline = food_cap_day_baseline * datablock["food"]["g_fat/g_food"]
co2e_cap_day_baseline = food_cap_day_baseline * datablock["impact"]["gco2e/gfood"]

datablock["food"]["kCal/cap/day"] = kcal_cap_day_baseline
datablock["food"]["g_prot/cap/day"] = prot_cap_day_baseline
datablock["food"]["g_fat/cap/day"] = fats_cap_day_baseline
datablock["food"]["g_co2e/cap/day"] = co2e_cap_day_baseline

# g_co2e / year

# These are UK values for the entire population and year
datablock["impact"]["g_co2e/year"] = fbs_impacts(food_uk, datablock["impact"]["gco2e/gfood"])

per_cap_day = {"Weight":food_cap_day_baseline,
            "Energy":kcal_cap_day_baseline,
            "Proteins":prot_cap_day_baseline,
            "Fat":fats_cap_day_baseline,
            "Emissions":co2e_cap_day_baseline}

# ------------------
# UK Per year values
# ------------------

# g_food, kCal, g_prot, g_fat, g_co2e / Year
food_year_baseline = food_cap_day_baseline * pop_past_uk * 365.25
kcal_year_baseline = kcal_cap_day_baseline * pop_past_uk * 365.25
prot_year_baseline = prot_cap_day_baseline * pop_past_uk * 365.25
fats_year_baseline = fats_cap_day_baseline * pop_past_uk * 365.25
co2e_year_baseline = co2e_cap_day_baseline * pop_past_uk * 365.25

datablock["food"]["g/year"] = food_year_baseline
datablock["food"]["kCal/year"] = kcal_year_baseline
datablock["food"]["g_prot/year"] = prot_year_baseline
datablock["food"]["g_fat/year"] = fats_year_baseline
datablock["food"]["g_co2e/year"] = co2e_year_baseline

per_year = {"Weight":food_year_baseline,
            "Energy":kcal_year_baseline,
            "Fat":fats_year_baseline,
            "Proteins":prot_year_baseline,
            "Emissions":co2e_year_baseline}

# -------------------------------
# Atmosferic model - Baseline run
# -------------------------------

pop_world_past = pop.sel(Year=np.arange(1961,2021), Region=area_pop_world)

# # Convert from grams to Gt: /1e15
# total_emissions_gtco2e_baseline = (co2e_year_baseline["food"] * pop_world_past / pop_past_uk).sum(dim="Item")/1e15

# T_base, C_base, F_base = fair_co2_only(total_emissions_gtco2e_baseline)

# datablock["impact"]["T"] = T_base
# datablock["impact"]["C"] = C_base
# datablock["impact"]["F"] = F_base

# -------------------------------
# Land use data
# -------------------------------

LC = UKCEH_LC_1000["percentage_aggregate"]

datablock["land"]["percentage_land_use"] = LC.where(np.isfinite(ALC.grade))
datablock["land"]["dominant_classification"] = ALC.grade
