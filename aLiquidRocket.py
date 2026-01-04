from math import exp
from rocketpy import Fluid, LiquidMotor, CylindricalTank, MassFlowRateBasedTank, UllageBasedTank

"""
Pay special attention to:

    dry_inertia is defined as a tuple of the form (I11, I22, I33). Where I11 and I22 are the inertia of the dry mass around the perpendicular axes to the motor, and I33 is the inertia around the motor center axis.

    dry inertia is defined in relation to the center of dry mass, and not in relation to the coordinate system origin.

    center_of_dry_mass_position, nozzle_position and the tanks position are defined in relation to the coordinate system origin, which is the nozzle outlet in this case.

    Both dry_mass and center_of_dry_mass_position must consider the mass of the tanks.
"""

# Define fluids
oxidizer_liq = Fluid(name="N2O_l", density=1220)
oxidizer_gas = Fluid(name="N2O_g", density=1.9277)
fuel_liq = Fluid(name="ethanol_l", density=789)
fuel_gas = Fluid(name="ethanol_g", density=1.59)

# Define tanks geometry
tanks_shape = CylindricalTank(radius = 0.1, height = 1.2, spherical_caps = True)
cylindrical_geometry = CylindricalTank(radius=0.1, height=2.0, spherical_caps=False)

# Define tanks
oxidizer_tank = MassFlowRateBasedTank(
    name="oxidizer tank",
    geometry=tanks_shape,
    flux_time=5,
    initial_liquid_mass=32,
    initial_gas_mass=0.01,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=lambda t: 32 / 3 * exp(-0.25 * t),
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0,
    liquid=oxidizer_liq,
    gas=oxidizer_gas,
)

fuel_tank = MassFlowRateBasedTank(
    name="fuel tank",
    geometry=tanks_shape,
    flux_time=5,
    initial_liquid_mass=21,
    initial_gas_mass=0.01,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=lambda t: 21 / 3 * exp(-0.25 * t),
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=lambda t: 0.01 / 3 * exp(-0.25 * t),
    liquid=fuel_liq,
    gas=fuel_gas,
)


N2O_flow_tank = MassFlowRateBasedTank(
    name="MassFlowRateBasedTank",
    geometry=cylindrical_geometry,
    flux_time=24.750,
    liquid=oxidizer_liq,
    gas=oxidizer_gas,
    initial_liquid_mass=42.8,
    initial_gas_mass=0.1,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out="../data/motors/liquid_motor_example/liquid_mass_flow_out.csv",
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out="../data/motors/liquid_motor_example/gas_mass_flow_out.csv",
    discretize=100,
)

# Pay special attention to the flux_time and ullage parameters.
tank_volume = cylindrical_geometry.total_volume
ullage = (-1 * N2O_flow_tank.liquid_volume) + tank_volume

N2O_ullage_tank = UllageBasedTank(
    name="UllageBasedTank",
    geometry=cylindrical_geometry,
    flux_time=24.750,
    gas=oxidizer_gas,
    liquid=oxidizer_liq,
    ullage=ullage,
    discretize=100,
)



example_liquid = LiquidMotor(
    thrust_source=lambda t: 4000 - 100 * t**2,
    dry_mass=2,
    dry_inertia=(0.125, 0.125, 0.002),
    nozzle_radius=0.075,
    center_of_dry_mass_position=1.75,
    nozzle_position=0,
    burn_time=5,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)
example_liquid.add_tank(tank=oxidizer_tank, position=1.0)
example_liquid.add_tank(tank=fuel_tank, position=2.5)

#example_liquid.all_info()