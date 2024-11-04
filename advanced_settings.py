import streamlit as st
from utils.helper_functions import update_slider

advanced_settings = {
    "labmeat_co2e" : {"label":"Cultured meat GHG emissions [g CO2e / g]",
                      "min_value": 1.0, "max_value": 120.0, "value": 25.0, "step":0.1, "key": "labmeat_slider"},

    "rda_kcal" : {"label":"Recommended daily energy intake [kCal]",
                  "min_value": 2000, "max_value": 2500, "value": 2250, "step":50, "key": "rda_slider"},

    "n_scale" : {"label":"Adoption timescale [years]",
                 "min_value": 0, "max_value": 50, "value": 20, "step":1, "key": "timescale_slider"},

    "max_ghge_animal" : {"label":"Maximum animal production GHGE reduction due to innovation [%]",
                         "min_value": 0, "max_value": 100, "value": 30, "step":1, "key": "max_ghge_animal"},
                         
    "max_ghge_plant" : {"label":"Maximum plant production GHGE reduction due to innovation [%]",
                        "min_value": 0, "max_value": 100, "value": 30, "step":1, "key": "max_ghge_plant"},

    "bdleaf_conif_ratio" : {"label":"Ratio of coniferous to broadleaved reforestation",
                             "min_value": 0., "max_value": 100., "value": 50., "step":0.1, "key": "bdleaf_conif_ratio"},

    "bdleaf_seq_ha_yr" : {"label":"Broadleaved forest CO2 sequestration [t CO2 / ha / year]",
                          "min_value": 0., "max_value": 100., "value": 12.5, "step":0.1, "key": "bdleaf_seq_ha_yr"},

    "conif_seq_ha_yr" : {"label":"Coniferous forest CO2 sequestration [t CO2 / ha / year]",
                         "min_value": 0., "max_value": 100., "value": 23.5, "step":0.1, "key": "conif_seq_ha_yr"},

    "elasticity" : {"label":"Production / Imports elasticity ratio",
                    "min_value": 0., "max_value": 1., "value": 0., "step":0.1, "key": "elasticity"},

    "agroecology_tree_coverage" : {"label":"Tree coverage in agroecology land",
                    "min_value": 0., "max_value": 1., "value": 0.1, "step":0.01, "key": "tree_coverage"},

    "manure_prod_factor" : {"label":"Manure production reduction",
                            "min_value": 0., "max_value": 1., "value": 0.3, "step":0.01, "key": "manure_prod"},
    "manure_ghg_factor" : {"label":"Manure GHG emissions reduction",
                           "min_value": 0., "max_value": 1., "value": 0.3, "step":0.01, "key": "manure_ghg"},

    "breeding_prod_factor" : {"label":"Breeding production reduction",
                            "min_value": 0., "max_value": 1., "value": 0.3, "step":0.01, "key": "breeding_prod"},
    "breeding_ghg_factor" : {"label":"Breeding GHG reduction",
                           "min_value": 0., "max_value": 1., "value": 0.3, "step":0.01, "key": "breeding_ghg"},

    "methane_prod_factor" : {"label":"Methane inhibitors production reduction",
                            "min_value": 0., "max_value": 1., "value": 0.3, "step":0.01, "key": "methane_prod"},
    "methane_ghg_factor" : {"label":"Methane inhibitors GHG reduction",
                           "min_value": 0., "max_value": 1., "value": 0.3, "step":0.01, "key": "methane_ghg"},

    "fossil_livestock_prod_factor" : {"label":"Livestock fossil fuel production reduction",
                                      "min_value": 0., "max_value": 1., "value": 0.3, "step":0.01, "key": "fossil_livestock_prod"},
    "fossil_livestock_ghg_factor" : {"label":"Livestock fossil fuel GHG reduction",
                            "min_value": 0., "max_value": .2, "value": .05, "step":0.01, "key": "fossil_livestock_ghg"},


    "fossil_arable_prod_factor" : {"label":"Arable fossil fuel production reduction",
                                   "min_value": 0., "max_value": 1., "value": 0.3, "step":0.01, "key": "fossil_arable_prod"},
    "fossil_arable_ghg_factor" : {"label":"Arable fossil fuel GHG reduction",
                           "min_value": 0., "max_value": .2, "value": .05, "step":0.01, "key": "fossiil_arable_ghg"},
}