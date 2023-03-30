import numpy as np
import xarray as xr
import pandas as pd
import streamlit as st

from agrifoodpy.population.population_data import UN
from agrifoodpy.food.food_supply import FAOSTAT, Nutrients_FAOSTAT
from agrifoodpy.impact.impact import PN18_FAOSTAT
from agrifoodpy.impact import impact

from agrifoodpy.land.land import ALC_1000 as ALC
from agrifoodpy.land.land import CEH_1000 as CEH
from agrifoodpy.land.land import CEHLCperagg_1000 as LC

import fair
from helper_functions import *

# ------------------------
# Item base
# ------------------------
groups = {
    "Cereals" : np.array([2511, 2513, 2514, 2515, 2516, 2517, 2518, 2520, 2531, 2532, 2533, 2534, 2535, 2807]),
    "Pulses" : np.array([2546, 2547, 2549, 2555]),
    "Sugar" : np.array([2536, 2537, 2541, 2542, 2543, 2558, 2562, 2570, 2571, 2572, 2573, 2574, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2586, 2745]),
    "NutsSeed" : np.array([2551, 2552, 2557, 2560, 2561]),
    "VegetablesFruits" : np.array([2563, 2601, 2602, 2605, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2625, 2641, 2775]),
    "RuminantMeat" : np.array([2731, 2732]),
    "OtherMeat" : np.array([2733, 2734, 2735, 2736]),
    "Egg" : np.array([2949]),
    "Dairy" : np.array([2740, 2743, 2948]),
    "FishSeafood" : np.array([2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769]),
    "Other" : np.array([2630, 2633, 2635, 2640, 2642, 2645, 2655, 2656, 2657, 2658, 2680, 2737]),
    "NonFood" : np.array([2559, 2575, 2659, 2781, 2782])
}

items_uk = np.hstack(list(groups.values()))

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

pop_uk = UN.Medium.sel(Region=area_pop, Year=years)*1000
pop_world = UN.Medium.sel(Region=area_pop_world, Year=years)*1000

pop_past = pop_uk[pop_uk["Year"] < 2020]
pop_future = pop_uk[pop_uk["Year"] >= 2020]
proj_pop_ones = xr.ones_like(pop_future)

# ---------------------------
# Match FAOSTAT and PN18 data
# ---------------------------
co2e_g = PN18_FAOSTAT["GHG Emissions"]

# -----------------------------------------
# Select food consumption data from FAOSTAT
# -----------------------------------------

# 1000Ton_food / Year
food_uk = FAOSTAT.sel(Region=area_fao, Item=items_uk).drop(["domestic"]).fillna(0)

meat_items = food_uk.sel(Item=food_uk.Item_group=="Meat").Item.values
animal_items = food_uk.sel(Item=food_uk.Item_origin=="Animal Products").Item.values
plant_items = food_uk.sel(Item=food_uk.Item_origin=="Vegetal Products").Item.values

# g_food / cap / day
food_cap_day_baseline = food_uk*1e9/pop_past/365.25
food_cap_day_baseline = xr.concat([food_cap_day_baseline, food_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")

# kCal, g_prot, g_fat / g_food
kcal_g = Nutrients_FAOSTAT["kcal"].sel(Item=items_uk, Region=area_fao) / food_cap_day_baseline["food"]
prot_g = Nutrients_FAOSTAT["protein"].sel(Item=items_uk, Region=area_fao) / food_cap_day_baseline["food"]
fats_g = Nutrients_FAOSTAT["fat"].sel(Item=items_uk, Region=area_fao) / food_cap_day_baseline["food"]

# This can give weird numbers in the case of produced/imported items not use for food.
# We set their nutrient values per mass to zero to avoid issues.
kcal_g = kcal_g.where(np.isfinite(kcal_g), other=0)
prot_g = prot_g.where(np.isfinite(prot_g), other=0)
fats_g = fats_g.where(np.isfinite(fats_g), other=0)

# kCal, g_prot, g_fat, g_co2e / cap / day
kcal_cap_day_baseline = food_cap_day_baseline * kcal_g
prot_cap_day_baseline = food_cap_day_baseline * prot_g
fats_cap_day_baseline = food_cap_day_baseline * fats_g
co2e_cap_day_baseline = food_cap_day_baseline * co2e_g

kcal_cap_day_baseline = xr.concat([kcal_cap_day_baseline, kcal_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")
prot_cap_day_baseline = xr.concat([prot_cap_day_baseline, prot_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")
fats_cap_day_baseline = xr.concat([fats_cap_day_baseline, fats_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")

# g_food, kCal, g_prot, g_fat, g_co2e / Year
food_year_baseline = food_cap_day_baseline * pop_uk * 365.25
kcal_year_baseline = kcal_cap_day_baseline * pop_uk * 365.25
prot_year_baseline = prot_cap_day_baseline * pop_uk * 365.25
fats_year_baseline = fats_cap_day_baseline * pop_uk * 365.25
co2e_year_baseline = co2e_cap_day_baseline * pop_uk * 365.25

# Dictionaries to call values on the GUI
baseline = {"Weight":food_year_baseline,
            "Energy":kcal_year_baseline,
            "Fat":fats_year_baseline,
            "Proteins":prot_year_baseline,
            "Emissions":co2e_year_baseline}

baseline_cap_day = {"Weight":food_cap_day_baseline,
            "Energy":kcal_cap_day_baseline,
            "Proteins":prot_cap_day_baseline,
            "Fat":fats_cap_day_baseline,
            "Emissions":co2e_cap_day_baseline}

bar_plot_limits = {"Weight":5000,
            "Energy":10000,
            "Fat":250,
            "Proteins":250,
            "Emissions":18000}

group_names = np.unique(food_uk.Item_group.values)

# -------------------------------
# Atmosferic model - Baseline run
# -------------------------------


total_emissions_gtco2e_baseline = (co2e_year_baseline["food"] * pop_world / pop_uk).sum(dim="Item").to_numpy()/1e15
C_base, F_base, T_base = fair.forward.fair_scm(total_emissions_gtco2e_baseline, useMultigas=False)

# --------------------------------------------
# Land data - Area for sparing and forestation
# --------------------------------------------


# Carbon sequestration of forested land in t CO2/ha/yr
land_options = ["Agricultural Land Classification", "Land use"]

CEH = CEH.sel(Year=2021)
ALC_ag_only = ALC.where((ALC.grade < 6) & (ALC.grade > 0))

crop_types = CEH.Type.values

pasture_land_types = "gr"
arable_land_types = list(crop_types)
arable_land_types.remove("gr")

# Create a new label coordinate to classify types of crops
use_type_list = ["arable", "pasture", "urban"]
use_type = ["arable", "arable", "pasture", "arable",
            "arable", "arable", "arable", "arable",
            "arable", "urban", "arable", "arable",
            "arable", "arable", "arable"]

crop_strings = ["Beet",
                "Field beans",
                "Grass",
                "Maize",
                "Oilseed rape",
                "Other crops",
                "Peas",
                "Potatoes",
                "Spring barley",
                "Solar panels",
                "Sprint oats",
                "Spring wheat",
                "Winter barley",
                "Winter oats",
                "Winter wheat ",
               ]

# And assign it to the CEH dataset
CEH = CEH.assign_coords({"use":("Type", use_type)})
CEH = CEH.assign_coords({"Crop name":("Type", crop_strings)})

# Create a new dataset with the same coordinates names, but this time "use" is referring to arable/pasture/urban use
CEH_pasture_arable = CEH.groupby("use").sum()
CEH_pasture_arable = CEH_pasture_arable.where(CEH_pasture_arable!=0)
CEH_pasture_arable = CEH_pasture_arable.assign_coords({"use":use_type_list})

# This is probably a very inneficient way of appending an extra use type to the "use" coordinate 
woodland_array = CEH_pasture_arable.sel(use="arable") #copy the arable coordinate
woodland_array = woodland_array.assign_coords({"use":"woodland"}) #rename it to woodland
woodland_array = woodland_array.where(np.isnan(woodland_array), other=0) #assign all non-nan values to zero
CEH_pasture_arable = xr.concat((CEH_pasture_arable, woodland_array), dim="use") # concatenate along the "use" dimension
CEH_pasture_arable = CEH_pasture_arable.sel(use=["arable", "pasture", "woodland", "urban"]) #rearrange the use coordinate

# Here we compute the crop areas by grade
crops_by_grade = [[CEH_pasture_arable.area.where(ALC_ag_only.grade==grade).sel(use=use).sum(dim=("x", "y")).values for use in use_type_list] for grade in np.arange(1,6)]
crops_by_grade = np.array(crops_by_grade)
crops_by_grade /= 10000

total_crops_arable = np.sum(crops_by_grade[:,0])
total_crops_pasture = np.sum(crops_by_grade[:,1])


# Let's do the same, this time with LC map instead of Crop maps

lamd_map_size = ALC_ag_only.grade.shape
LC = LC.percentage[:, :lamd_map_size[0], :lamd_map_size[1]]

# Category strings

# ['Broadleaf woodland',
# 'Coniferous woodland',
# 'Arable',
# 'Improved grassland',
# 'Semi-natural grassland',
# 'Mountain, heath and bog',
# 'Saltwater',
# 'Freshwater',
# 'Coastal',
# 'Built-up areas and gardens']

# Use strings

# ['arable',
#  'grassland',
#  'mountain',
#  'urban',
#  'water',
#  'woodland']


# make a color map of fixed colors
from matplotlib import colors

#              arable    grassland mountain urban    water   woodland 
color_list = ["yellow", "orange", "gray", "gray", "gray", "green"]
cmap_tar = colors.ListedColormap(color_list)
bounds_tar = np.linspace(-0.5, 5.5, 7)
norm_tar = colors.BoundaryNorm(bounds_tar, cmap_tar.N)

category_type = ["woodland", "woodland", "arable", "grassland", "grassland", "mountain", "water", "water", "water", "urban"]

# And assign it to the LC dataset
LC = LC.assign_coords({"use":("Category", category_type)})

# Create a new dataset with the same coordinates names, but this time "use" is referring to arable/pasture/urban use
LC_type = LC.groupby("use").sum()
LC_type = LC_type.where(~np.isnan(ALC.grade)) # make sure everyhting equal to zero is nan 

# use by grade
use_by_grade = [[LC_type[cat].where(ALC.grade==grade).sum(dim=("x", "y")).values/100 for cat in np.arange(6)] for grade in np.arange(0,8)]
use_by_grade = np.array(use_by_grade)