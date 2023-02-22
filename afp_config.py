import numpy as np
import xarray as xr

from agrifoodpy import food
from agrifoodpy.population.population_data import UN
from agrifoodpy.food.food_supply import FAOSTAT, Nutrients_FAOSTAT, scale_food, plot_years, plot_bars
from agrifoodpy.impact.impact import PN18_FAOSTAT
from agrifoodpy.impact import impact

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
area_fao = 229 #UK
years = np.arange(1961, 2101)

# ------------------------------
# Select population data from UN
# ------------------------------

pop_uk = UN.Medium.sel(Region=area_pop, Year=years)*1000

pop_past = pop_uk[pop_uk["Year"] < 2020]
pop_future = pop_uk[pop_uk["Year"] >= 2020]
proj_pop_ones = xr.ones_like(pop_future)

# ---------------------------
# Match FAOSTAT and PN18 data
# ---------------------------
co2e_g = PN18_FAOSTAT["GHG Emissions"]/1000

# -----------------------------------------
# Select food consumption data from FAOSTAT
# -----------------------------------------

# 1000Ton_food / Year
food_uk = FAOSTAT.sel(Region=area_fao, Item=items_uk).drop(["domestic", "residual", "tourist"])

meat_items = food_uk.sel(Item=food_uk.Item_group=="Meat").Item.values
animal_items = food_uk.sel(Item=food_uk.Item_origin=="Animal Products").Item.values
plant_items = food_uk.sel(Item=food_uk.Item_origin=="Vegetal Products").Item.values

# g_food / cap / day
food_cap_day_baseline = food_uk*1e9/pop_past/365.25
food_cap_day_baseline = xr.concat([food_cap_day_baseline, food_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")

# kCal, g_prot, g_fat / g_food
kcal_g = Nutrients_FAOSTAT.kcal.sel(Region=229)
prot_g = Nutrients_FAOSTAT.protein.sel(Region=229)
fats_g = Nutrients_FAOSTAT.fat.sel(Region=229)

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

baseline = {"Weight":food_year_baseline,
            "Energy":kcal_year_baseline,
            "Fat":fats_year_baseline,
            "Proteins":prot_year_baseline,
            "Emissions":co2e_year_baseline}

baseline_cap_day = {"Weight":food_cap_day_baseline,
            "Energy":kcal_cap_day_baseline,
            "Fat":prot_cap_day_baseline,
            "Proteins":fats_cap_day_baseline,
            "Emissions":co2e_cap_day_baseline}

bar_plot_limits = {"Weight":5000,
            "Energy":1500000,
            "Fat":45000,
            "Proteins":26000,
            "Emissions":18}


group_names = np.unique(food_uk.Item_group.values)

land_options = ["Agricultural Land Classification", "Crops"]
