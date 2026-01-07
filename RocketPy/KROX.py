from math import exp 

from rocketpy import units
from rocketpy import Fluid 
from rocketpy import LiquidMotor
from rocketpy import CylindricalTank, MassFlowRateBasedTank


#these are also used as approximatons for gas entering prop tanks
OFratio_engine = 2.1
mDot_engine = 5 #kg/sec

KRmDotLiquid_engine = mDot_engine / (1 + OFratio_engine) 
OXmDotLiquid_engine = OFratio_engine*KRmDotLiquid_engine

#dependent on PROMPT
nozzleOutletRadius_engine = 0.075 #Radius of motor nozzle outlet in meters.
thurst_engine = units.convert_units(1200, "lb", "kg")*9.81

#dependent on how the chamber was designed
centerOfDryMassPositionRelativeToNozzle_engine = units.convert_units(8, "in", "m") #exit of nozzle is at origin.
dryweight_engine = units.convert_units(2, "lb", "kg")

#this is dependent on the ablative performance, and thickness of ablative
burnDuration_engine = 10 #seconds with OX running out first



#there is no pressurant yet

# LOX tank parameters
tankRadiusOX = units.convert_units(5.562/2, "in", "m")
tankLengthOX = units.convert_units(32, "in", "m")

# Kerosene tank parameters
tankRadiusKR = units.convert_units(5.562/2, "in", "m")
tankLengthKR = units.convert_units(24, "in", "m")

#creating tank geometry objects. standard ones here, not detailed. 
OXtank_geometry = CylindricalTank(radius=0.1, height=2.0, spherical_caps=True)
KRtank_geometry = CylindricalTank(radius=0.1, height=2.0, spherical_caps=True)

#defining our fluids, kerosene, lox, air. These values are approximated from engineering toolbox
#this uh, more accurate please LOL
OX_liquid = Fluid(name="Liquid Oxygen", density=1000)  #kg/m^3 somehwere near -100degC, somewhere near 50bara 
OX_vapour = Fluid(name="Vapour Oxygen", density=26)    #kg/m^3 somehwere near -100degC, somewhere near 10bara 

KR_liquid = Fluid(name="Liquid Kerosene", density=800) #kg/m^3 range was given as 775/840 o.o
AIR_vapour = Fluid(name="Air", density=10)             #kg/m^3 at 20C? bleh

# Leave small ullage (0.1%) to avoid numerical precision issues at initialization
OXtank_fillMass = OX_liquid.density * OXtank_geometry.total_volume * 0.99
KRtank_fillMass = KR_liquid.density * KRtank_geometry.total_volume * 0.99
OXtank_initial_gas = AIR_vapour.density * OXtank_geometry.total_volume * 0.01
KRtank_initial_gas = AIR_vapour.density * KRtank_geometry.total_volume * 0.01


#firing is OX limited. this figuring out leftover time the tank is dumping fuel
# this needs to be different, should figure out what is actually going to run out 
#KRtank_flameballtime = (KRtank_fillMass - (burnDuration_engine * KRmDotLiquid_engine)) / KRmDotLiquid_engine 

fluxTime = max(
    KRtank_fillMass / KRmDotLiquid_engine,
    OXtank_fillMass / OXmDotLiquid_engine
)

if fluxTime ==  KRtank_fillMass / KRmDotLiquid_engine:
    print("Oxidizer Limited")

else:
    print("Fuel Limited")

# i think i see it. there are two volumes in the prop tank, and they need to sorta match i think. 
# the error that was being thrown earlier was saying that the gas volume bubble wasnt matching or 
# was significantly off from liquid volume bubble

KR_gasMdot = float(KRmDotLiquid_engine * (1/KR_liquid.density) * AIR_vapour.density)
OX_gasMdot = float(OXmDotLiquid_engine * (1/OX_liquid.density) * AIR_vapour.density)


#fluxtime isnt just burn duration, because there are more propellants

OXtank = MassFlowRateBasedTank(
    name="Liquid Oxygen Tank",
    geometry=OXtank_geometry,
    flux_time=OXtank_fillMass / OXmDotLiquid_engine - 1,   #engine burn time basically.
    liquid=OX_liquid,
    gas=AIR_vapour,                 #hey so, is it just ox vapour? wouldnt it be both? someone run to mixed gas properties
    initial_liquid_mass=OXtank_fillMass,
    initial_gas_mass=OXtank_initial_gas,  #small ullage to avoid numerical issues
    liquid_mass_flow_rate_in=0,     #should be 0
    liquid_mass_flow_rate_out=OXmDotLiquid_engine,
    gas_mass_flow_rate_in=OX_gasMdot,   #pressurant gas flows in to maintain pressure
    gas_mass_flow_rate_out=0,           #well. none zero due to boil off. neglected 
    discretize=100,                     #i did not understand this
)

OXtank.info()

KRtank = MassFlowRateBasedTank(
    name="Kerosene Tank",
    geometry=KRtank_geometry,
    flux_time=KRtank_fillMass / KRmDotLiquid_engine,     #how long does tank need to be worried about
    liquid=KR_liquid,            
    gas=AIR_vapour,              #all air
    initial_liquid_mass=KRtank_fillMass,
    initial_gas_mass=0,          #basically 0
    liquid_mass_flow_rate_in=0,  #should be
    liquid_mass_flow_rate_out=KRmDotLiquid_engine,
    gas_mass_flow_rate_in= KR_gasMdot,    
    gas_mass_flow_rate_out=0,    #basically 0. 
    discretize=100,              # i did not understand this
)
KRtank.info()

KROXengine = LiquidMotor(
    coordinate_system_orientation="nozzle_to_combustion_chamber", #positive torwards to combustion chamber
    center_of_dry_mass_position=centerOfDryMassPositionRelativeToNozzle_engine,
    nozzle_position=0, #nozzle exit area to coord sys
    thrust_source= thurst_engine,
    dry_mass=dryweight_engine,
    dry_inertia=(0.125, 0.125, 0.002),           #uhm, need this.
    nozzle_radius=nozzleOutletRadius_engine,
    burn_time=burnDuration_engine,
)
KROXengine.add_tank(tank=OXtank, position=1.0)
KROXengine.add_tank(tank=KRtank, position=2.5)

KROXengine.all_info()


# KROXengine.propellant_mass.plot(0, )
#"""