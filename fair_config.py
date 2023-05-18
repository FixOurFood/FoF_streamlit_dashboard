from fair import FAIR
import xarray as xr
from fair.interface import fill, initialise

def set_fair_base():
    fair_base = FAIR()

    fair_base.ghg_method='myhre1998'

    # Define timebounds
    fair_base.define_time(1960.5, 2100.5, 1)

    # Define scenarios
    fair_base.define_scenarios(["afp"])

    # Define configurations
    fair_base.define_configs(["defaults"])

    # Define species and their properties
    species = ['CO2']
    properties = {
        'CO2': {
            'type': 'co2',
            'input_mode': 'emissions',
            'greenhouse_gas': True,  # it doesn't behave as a GHG itself in the model, but as a precursor
            'aerosol_chemistry_from_emissions': False,
            'aerosol_chemistry_from_concentration': False,
        }}

    fair_base.define_species(species, properties)

    # Allocate arrays
    fair_base.allocate()

    # Set climate configs
    fill(fair_base.climate_configs["ocean_heat_transfer"], [1.1, 1.6, 0.9], config='defaults')
    fill(fair_base.climate_configs["ocean_heat_capacity"], [8, 14, 100], config='defaults')
    fill(fair_base.climate_configs["deep_ocean_efficacy"], 1.1, config='defaults')

    # Set initial conditions
    initialise(fair_base.concentration, 278.3, specie='CO2')
    initialise(fair_base.forcing, 0)
    initialise(fair_base.temperature, 0)
    initialise(fair_base.cumulative_emissions, 0)
    initialise(fair_base.airborne_emissions, 0)

    # Fill species configs
    fair_base.fill_species_configs()

    return fair_base