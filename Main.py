# -*- coding: utf-8 -*-
"""
Author: Paulo Chainho / Kilian Kruggel

This program was developed in the scope of WESE H2020 project

The FEMM model here developed is used to estimate the EMF's surrounding a 
3-phase submarine power cable. 

For more information on the femm functions used, please check the manual 
available here -> https://www.femm.info/wiki/pyFEMM

""" 
import os
import numpy as np
import scipy as sp
import femm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.ticker import FormatStrFormatter

dir = os.getcwd()

#==============================================================================
# Subsea Cable Parameters 
#==============================================================================

# User Inputs -----------------------------------------------------------------
A_cond = 50  # Conductor cross sectional area (mm^2)
cond_screen = 0.2 # Conductor screen thickness (mm)
insulation = 3.4 # Conductor insulation thickness (mm)
insul_screen_NM = 3.0 # Conductor insulation screen - non metallic thickness (mm)
insul_screen_ME = 0.2 # Conductor insulation screen (sheath) - metallic thickness (mm)
bedding = 0.2 # Bedding thickness (mm)
r_armour = 2.00 # Armour radius (mm)
r_armour_2 = 0 # 2nd Armour layer radius (mm) -> set 0 if non-existant
over_sheath = 2.0 # Over Sheath thickness (mm)

AMPS_RMS = 0.057 # RMS Phase Current (A)
AMPS = sp.sqrt(2) * AMPS_RMS #Peak Phase Current (A)
freq = 50 #Hz grid frequency

burial_depth = 2000 # Burial depth [mm] -> set 0 if surface laid

# Support Variables -----------------------------------------------------------
r_cond = sp.sqrt( (A_cond/sp.pi) ) # Conductor radius (mm)
r_cond_screen = r_cond + cond_screen # Conductor screen radius
r_cond_insul = r_cond + cond_screen + insulation # Conductor insulation radius
r_cond_insu_screen_NM = r_cond + cond_screen + insulation + insul_screen_NM # Conductor insul. screen radius (non metallic)
r_cond_total = r_cond + cond_screen + insulation + insul_screen_NM + insul_screen_ME # Total conductor radius

dist1 = 0.01 # Distance to create a small gap between the conductors and the bedding (mm)
dist2 = 0.01 # Distance to create a small gap between the subsea cable and the core (mm)

cond_surf = 0.2  #distance between conductor surfaces

cond_center = 2*r_cond_total + cond_surf # distance between conductor centers

#==============================================================================
# Environment and Cable component characteristics
#==============================================================================

# copper conductors
copper_conductivity = 58000000 # [S/m]
copper_permeability = 1.0 # relative permeability [unitless]

# XLPE insulation
XLPE_conductivity = 0.0 # [S/m]
XLPE_permeability = 1.0 # relative permeability [unitless]

# Non metallic Insulation Screen (e.g. semi-conductive conductor screen, insulation screen,...)
NM_screen_conductivity = 1.0 # [S/m]
NM_screen_permeability = 1.0 # relative permeability [unitless]

# Metallic Insulation screen (e.g. lead -> check cable material)
M_screen_conductivity = 5000000 # [S/m]
M_screen_permeability = 1.0     # relative permeability [unitless]

# Inner Sheath (e.g. PVC)
inner_conductivity = 0.0 # [S/m]
inner_permeability = 1.0     # relative permeability [unitless]

# Bedding (e.g. PVC)
bedding_conductivity = 0.0 # [S/m]
bedding_permeability = 1.0     # relative permeability [unitless]

# Armour (e.g. Galvanised steel wire)
armour_conductivity = 1100000 # [S/m]
armour_permeability = 300     # relative permeability [unitless]

# Over Sheath 
over_conductivity = 0.0 # [S/m]
over_permeability = 1.0     # relative permeability [unitless]

# Seawater
seawater_conductivity = 5.0 # [S/m]
seawater_permeability = 1.0 # relative permeability [unitless]

# Seabed (sand)
seabed_conductivity = 1.0 # [S/m]
seabed_permeability = 1.0 # relative permeability [unitless]

#==============================================================================
## Starting FEMM and creating a new FEMM-document
#==============================================================================
# Starting FEMM
femm.openfemm() # opens FEMM app, add (1) to hide the main window

# Creating new magnostatic problem 
femm.newdocument(0) # Specify doctype to be 0 for a magnetics problem, 
                    #                       1 for an electrostatics problem, 
                    #                       2 for a heat flow problem, 
                    #                       3 for a current flow problem.

# Problem definition: Frequency, units, problemtype, precision, depth,
# minangle(Mesh), solver type: 0 for successive appr., 1 for Newton
femm.mi_probdef(freq, 'millimeters', 'planar', 1.e-8, 5000, 10, 0)

# Set display area ------------------------------------------------------------
# mi_zoom(x1,y1,x2,y2) sets the display area to be from the bottom left corner 
# specified by (x1,y1) to the top right corner specified by (x2,y2).
femm.mi_zoom(-400, -400, 400, 400)


# Component Materials

femm.mi_addmaterial('copper_conductors', copper_permeability, copper_permeability, 
                    0, 0, seawater_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('XLPE', XLPE_permeability, XLPE_permeability, 0, 0, 
                    XLPE_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('M_screen', M_screen_permeability, M_screen_permeability, 0, 0, 
                    M_screen_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('NM_screen', NM_screen_permeability, NM_screen_permeability,
                    0, 0, NM_screen_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('inner', inner_permeability, inner_permeability, 0, 0, 
                    inner_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('bedding', bedding_permeability, bedding_permeability, 0, 0, 
                    bedding_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('armour', armour_permeability, armour_permeability, 0, 0, 
                    armour_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('over', over_permeability, over_permeability, 0, 0, 
                    over_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('seawater', seawater_permeability, seawater_permeability, 0, 0, 
                    seawater_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)
femm.mi_addmaterial('seabed', seabed_permeability, seabed_permeability, 0, 0, 
                    seabed_conductivity*10**-6, 0, 0, 0, 0, 0, 0, 0, 0)

# General

GridSize = 0.3 * r_cond_total

# Geometry: Subsea Cable

# Apothem of an equilateral triangle
delta_y_triangle = (1 / 6) * sp.sqrt(3) * cond_center

#==============================================================================
# Draw Environment Geometry 
#==============================================================================
#Process:
# 1- Draw the lines/arcs segments
# 2- Add a "Block Label" marker into each enclosed section to define material 
#    properties and mesh size

#Constant to define the Environment
limit_fine = 400  # in [mm]
limit_coarse = 3500 # in [mm]

# Draw a square  to use as the outer boundary for the problem
femm.mi_addblocklabel(limit_coarse*4/5, limit_coarse*4/5)
femm.mi_drawline(limit_coarse, limit_coarse, limit_coarse, -limit_coarse)
femm.mi_drawline(limit_coarse, limit_coarse, -limit_coarse, limit_coarse)
femm.mi_drawline(-limit_coarse, -limit_coarse, limit_coarse, -limit_coarse)
femm.mi_drawline(-limit_coarse, -limit_coarse, -limit_coarse, limit_coarse)

# Draw a secound square to use a finer mesh close to the cable
femm.mi_addblocklabel(limit_fine*4/5, limit_fine*4/5)
femm.mi_drawline(limit_fine, limit_fine, limit_fine, -limit_fine)
femm.mi_drawline(limit_fine, limit_fine, -limit_fine, limit_fine)
femm.mi_drawline(-limit_fine, -limit_fine, limit_fine, -limit_fine)
femm.mi_drawline(-limit_fine, -limit_fine, -limit_fine, limit_fine)

################
# Seabed
################

if burial_depth!=0 and burial_depth>limit_fine:
   
    # Draw a square  to use as the outer boundary for the problem
    femm.mi_addblocklabel(limit_coarse*4/5, -limit_coarse*4/5)
    femm.mi_drawline(-limit_coarse, burial_depth, limit_coarse, burial_depth)

################
#Conductor 1
################
#Constants 
cos60 =  sp.cos(np.radians(60))
sin60 =  sp.sin(np.radians(60))

# Draw a circle corresponding to 'Conductor 1'
femm.mi_addblocklabel(cond_center*cos60, -delta_y_triangle),
femm.mi_drawarc(cond_center*cos60-r_cond, -delta_y_triangle, cond_center*cos60+r_cond, -delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(cond_center*cos60+r_cond, -delta_y_triangle, cond_center*cos60-r_cond, -delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)

# Draw a  circle corresponding to the 'Conductor Screen 1',
femm.mi_addblocklabel(cond_center*cos60+r_cond_screen-0.5*cond_screen, -delta_y_triangle),
femm.mi_drawarc(cond_center*cos60-r_cond_screen, -delta_y_triangle, cond_center*cos60+r_cond_screen, -delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(cond_center*cos60+r_cond_screen, -delta_y_triangle, cond_center*cos60-r_cond_screen, -delta_y_triangle, 180, 3)  # (x1, y1 , x2, y2, angle, maxseg)

# Draw a circle corresponding to 'Insulation 1'
femm.mi_addblocklabel(cond_center*cos60+r_cond_insul-0.5*insulation, -delta_y_triangle),
femm.mi_drawarc(cond_center*cos60-r_cond_insul, -delta_y_triangle, cond_center*cos60+r_cond_insul, -delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(cond_center*cos60+r_cond_insul, -delta_y_triangle, cond_center*cos60-r_cond_insul, -delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)

# Draw a circle corresponding to 'Insulation Screen - Non metallic 1'
femm.mi_addblocklabel(cond_center*cos60+r_cond_insu_screen_NM-0.5*insul_screen_NM, -delta_y_triangle),
femm.mi_drawarc(cond_center*cos60-r_cond_insu_screen_NM, -delta_y_triangle, cond_center*cos60+r_cond_insu_screen_NM, -delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(cond_center*cos60+r_cond_insu_screen_NM, -delta_y_triangle, cond_center*cos60-r_cond_insu_screen_NM, -delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)

# Draw a  circle corresponding to the 'Insulation Screen - Metallic 1',
femm.mi_addblocklabel(cond_center*cos60+r_cond_total-0.5*insul_screen_ME, -delta_y_triangle),
femm.mi_drawarc(cond_center*cos60-r_cond_total, -delta_y_triangle, cond_center*cos60+r_cond_total, -delta_y_triangle, 180, 3)  # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(cond_center*cos60+r_cond_total, -delta_y_triangle, cond_center*cos60-r_cond_total, -delta_y_triangle, 180, 3)  # (x1, y1 , x2, y2, angle, maxseg)

################
#Conductor 2
################

# Draw a circle corresponding to 'Conductor 2'
femm.mi_addblocklabel(0, cond_center*sin60-delta_y_triangle),
femm.mi_drawarc(0, cond_center*sin60-r_cond-delta_y_triangle, 0, cond_center*sin60+r_cond-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(0, cond_center*sin60+r_cond-delta_y_triangle, 0, cond_center*sin60-r_cond-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)

# Draw a  circle corresponding to the 'Conductor Screen 2',
femm.mi_addblocklabel(0+r_cond_screen-0.5*cond_screen, cond_center*sin60-delta_y_triangle),
femm.mi_drawarc(0, cond_center*sin60-r_cond_screen-delta_y_triangle, 0, cond_center*sin60+r_cond_screen-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(0, cond_center*sin60+r_cond_screen-delta_y_triangle, 0, cond_center*sin60-r_cond_screen-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)

# Draw a circle corresponding to 'Insulation 2'
femm.mi_addblocklabel(0+r_cond_insul-0.5*insulation, cond_center*sin60-delta_y_triangle),
femm.mi_drawarc(0, cond_center*sin60-r_cond_insul-delta_y_triangle, 0, cond_center*sin60+r_cond_insul-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(0, cond_center*sin60+r_cond_insul-delta_y_triangle, 0, cond_center*sin60-r_cond_insul-delta_y_triangle, 180, 3) # (x1, y1 , x2, y2, angle, maxseg)

# Draw a circle corresponding to 'Insulation Screen - Non metallic 2'
femm.mi_addblocklabel(0+r_cond_insu_screen_NM-0.5*insul_screen_NM, cond_center*sin60-delta_y_triangle),
femm.mi_drawarc(0, cond_center*sin60-r_cond_insu_screen_NM-delta_y_triangle, 0, cond_center*sin60+r_cond_insu_screen_NM-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(0, cond_center*sin60+r_cond_insu_screen_NM-delta_y_triangle, 0, cond_center*sin60-r_cond_insu_screen_NM-delta_y_triangle, 180, 3)

# Draw a  circle corresponding to 'Insulation Screen - Metallic 2',
femm.mi_addblocklabel(0+r_cond_total-0.5*insul_screen_ME, cond_center*sin60-delta_y_triangle),
femm.mi_drawarc(0, cond_center*sin60-r_cond_total-delta_y_triangle, 0, cond_center*sin60+r_cond_total-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(0, cond_center*sin60+r_cond_total-delta_y_triangle, 0, cond_center*sin60-r_cond_total-delta_y_triangle, 180, 3)

################
#Conductor 3
################

# Draw a circle corresponding to 'Conductor 3'
femm.mi_addblocklabel(-cond_center*cos60, -delta_y_triangle),
femm.mi_drawarc(-cond_center*cos60-r_cond, 0-delta_y_triangle, -cond_center*cos60+r_cond, 0-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(-cond_center*cos60+r_cond, 0-delta_y_triangle, -cond_center*cos60-r_cond, 0-delta_y_triangle, 180, 3)

# Draw a  circle corresponding to the 'Conductor Screen 3',
femm.mi_addblocklabel(-cond_center*cos60+r_cond_screen-0.5*cond_screen, -delta_y_triangle)
femm.mi_drawarc(-cond_center*cos60-r_cond_screen, 0-delta_y_triangle, -cond_center*cos60+r_cond_screen, 0-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(-cond_center*cos60+r_cond_screen, 0-delta_y_triangle, -cond_center*cos60-r_cond_screen, 0-delta_y_triangle, 180, 3)

# Draw a circle corresponding to 'Insulation 3'
femm.mi_addblocklabel(-cond_center*cos60+r_cond_insul-0.5*insulation, -delta_y_triangle)
femm.mi_drawarc(-cond_center*cos60-r_cond_insul, 0-delta_y_triangle, -cond_center*cos60+r_cond_insul, 0-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(-cond_center*cos60+r_cond_insul, 0-delta_y_triangle, -cond_center*cos60-r_cond_insul, 0-delta_y_triangle, 180, 3)

# Draw a circle corresponding to 'Insulation Screen - Non metallic 3'
femm.mi_addblocklabel(-cond_center*cos60+r_cond_insu_screen_NM-0.5*insul_screen_NM, -delta_y_triangle)
femm.mi_drawarc(-cond_center*cos60-r_cond_insu_screen_NM, 0-delta_y_triangle, -cond_center*cos60+r_cond_insu_screen_NM, 0-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(-cond_center*cos60+r_cond_insu_screen_NM, 0-delta_y_triangle, -cond_center*cos60-r_cond_insu_screen_NM, 0-delta_y_triangle, 180, 3)

# Draw a  circle corresponding to 'Insulation Screen - Metallic 3'
femm.mi_addblocklabel(-cond_center*cos60+r_cond_total-0.5*insul_screen_ME, -delta_y_triangle),
femm.mi_drawarc(-cond_center*cos60-r_cond_total, 0-delta_y_triangle, -cond_center*cos60+r_cond_total, 0-delta_y_triangle, 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(-cond_center*cos60+r_cond_total, 0-delta_y_triangle, -cond_center*cos60-r_cond_total, 0-delta_y_triangle, 180, 3)

################
#Laying Up / Filling
################
femm.mi_addblocklabel(0,0),

################
#Bedding
################

# Draw a  circle corresponding to the 'Bedding' - inner radius
femm.mi_addblocklabel(0,cond_center*sin60+r_cond_total-delta_y_triangle+0.5*bedding),
femm.mi_drawarc(0, cond_center*sin60+r_cond_total-delta_y_triangle+dist1, 0, -cond_center*sin60-r_cond_total+delta_y_triangle-dist1, 180, 3),   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(0, -cond_center*sin60-r_cond_total+delta_y_triangle-dist1, 0, cond_center*sin60+r_cond_total-delta_y_triangle+dist1, 180, 3),

 # Draw a  circle corresponding to the 'Bedding' - outer radius
femm.mi_drawarc(0, cond_center*sin60+r_cond_total-delta_y_triangle+bedding, 0, -cond_center*sin60-r_cond_total+delta_y_triangle-bedding, 180, 3),   # (x1, y1 , x2, y2, angle, maxseg)
femm.mi_drawarc(0, -cond_center*sin60-r_cond_total+delta_y_triangle-bedding, 0, cond_center*sin60+r_cond_total-delta_y_triangle+bedding, 180, 3),

################
# Armour - 1st Layer 
################

#Calculate the number of shielding elements in the cable
space = 0.05 #distance between armour elements
R_armour = (cond_center * sin60 - delta_y_triangle) + r_cond_total + bedding + r_armour
Armour_perimeter = 2 * sp.pi * (R_armour)
NbrOfArmourElem = int( sp.floor( Armour_perimeter/(2*r_armour + space)) )
theta = np.radians(360/NbrOfArmourElem)

# Draw a circle cooresponding to the 1st shielding layer;
for i in range(1,NbrOfArmourElem+1):
     femm.mi_addblocklabel(R_armour*sp.sin((i-1)*theta) , R_armour*sp.cos((i-1)*theta) )
     femm.mi_drawarc((R_armour-r_armour+dist1)*sp.sin((i-1)*theta), (R_armour-r_armour+dist1)*sp.cos((i-1)*theta), (R_armour+r_armour-dist1)*sp.sin((i-1)*theta), (R_armour+r_armour-dist1)*sp.cos((i-1)*theta), 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
     femm.mi_drawarc((R_armour+r_armour-dist1)*sp.sin((i-1)*theta), (R_armour+r_armour-dist1)*sp.cos((i-1)*theta), (R_armour-r_armour+dist1)*sp.sin((i-1)*theta), (R_armour-r_armour+dist1)*sp.cos((i-1)*theta), 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)

################
# Area between armouring 
################
 
femm.mi_addblocklabel((R_armour-0.4*r_armour)*sp.sin((1-0.5)*theta), (R_armour-0.4*r_armour)*sp.cos((1-0.5)*theta));

if r_armour_2!=0:    # check if cable has a 2nd armour layer

    ################
    # Armour - 2nd Layer 
    ################
    
    #Calculate the number of shielding elements in the cable
    space = 0.05 #distance between armour elements
    R_armour_2 = R_armour + r_armour + space + r_armour_2
    Armour_perimeter_2 = 2 * sp.pi * (R_armour_2)
    NbrOfArmourElem2 = int( sp.floor( Armour_perimeter_2/(2*r_armour_2 + space)) )
    theta_2 = np.radians(360/NbrOfArmourElem2)
    
    # Draw a circle cooresponding to the 2nd shielding layer;
    for i in range(1,NbrOfArmourElem2+1):
         femm.mi_addblocklabel(R_armour_2*sp.sin((i-1)*theta_2) , R_armour_2*sp.cos((i-1)*theta_2) )
         femm.mi_drawarc((R_armour_2-r_armour_2+dist1)*sp.sin((i-1)*theta_2), (R_armour_2-r_armour_2+dist1)*sp.cos((i-1)*theta_2), (R_armour_2+r_armour_2-dist1)*sp.sin((i-1)*theta_2), (R_armour_2+r_armour_2-dist1)*sp.cos((i-1)*theta_2), 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
         femm.mi_drawarc((R_armour_2+r_armour_2-dist1)*sp.sin((i-1)*theta_2), (R_armour_2+r_armour_2-dist1)*sp.cos((i-1)*theta_2), (R_armour_2-r_armour_2+dist1)*sp.sin((i-1)*theta_2), (R_armour_2-r_armour_2+dist1)*sp.cos((i-1)*theta_2), 180, 3)   # (x1, y1 , x2, y2, angle, maxseg)
    
    ################
    #Over Sheath
    ################
    
    # Draw a  circle corresponding to the 'Over Sheath' - inner radius
    femm.mi_addblocklabel(0,R_armour_2+r_armour_2+dist1+0.5*over_sheath)
    femm.mi_drawarc(0, R_armour_2+r_armour_2+dist1, 0, -R_armour_2-r_armour_2-dist1, 180, 2)   # ([x1 y1 ; x2, y2], angle, maxseg)
    femm.mi_drawarc(0, -R_armour_2-r_armour_2-dist1, 0, R_armour_2+r_armour_2+dist1, 180, 2)
    
    # Draw a  circle corresponding to the 'Over Sheath' - outer radius
    femm.mi_drawarc(0, R_armour_2+r_armour_2+over_sheath+2*dist1, 0, -R_armour_2-r_armour_2-over_sheath-2*dist1, 180, 2)  # ([x1 y1 ; x2, y2], angle, maxseg)
    femm.mi_drawarc(0, -R_armour_2-r_armour_2-over_sheath-2*dist1, 0, R_armour_2+r_armour_2+over_sheath+2*dist1, 180, 2);

    #Overall Cable Radius
    R_cable_total = R_armour_2 + r_armour_2 + over_sheath + dist1
     
    #Display
    print('Overall Cable Diameter :',2*R_cable_total)

else:

    ################
    #Over Sheath
    ################
    
    # Draw a  circle corresponding to the 'Over Sheath' - inner radius
    femm.mi_addblocklabel(0,R_armour+r_armour+dist1+0.5*over_sheath)
    femm.mi_drawarc(0, R_armour+r_armour+dist1, 0, -R_armour-r_armour-dist1, 180, 2)   # ([x1 y1 ; x2, y2], angle, maxseg)
    femm.mi_drawarc(0, -R_armour-r_armour-dist1, 0, R_armour+r_armour+dist1, 180, 2)
    
    # Draw a  circle corresponding to the 'Over Sheath' - outer radius
    femm.mi_drawarc(0, R_armour+r_armour+over_sheath+2*dist1, 0, -R_armour-r_armour-over_sheath-2*dist1, 180, 2)  # ([x1 y1 ; x2, y2], angle, maxseg)
    femm.mi_drawarc(0, -R_armour-r_armour-over_sheath-2*dist1, 0, R_armour+r_armour+over_sheath+2*dist1, 180, 2);

    #Overall Cable Radius
    R_cable_total = R_armour + r_armour + over_sheath + dist1
     
    #Display
    print('Overall Cable Diameter :',2*R_cable_total)

#Display
print('Objects geometries defined')

#==============================================================================
# Define Object Properties  
#==============================================================================
# Note: Because the function "femm.mi_clearselected" doesn't seem to be working
#       to deselect the labels, the most simple way found to achieve this was to
#       double selected using a for loop, odd but effective. 


################
# Environment (rectangles):
################

# Apply the materials to the appropriate block labels

for i in range(2):
    femm.mi_selectlabel(limit_coarse*4/5, limit_coarse*4/5)  #outer rectangle
    femm.mi_setblockprop('seawater', 0, 10*GridSize, '<None>', 0, 0, 0)

if burial_depth!=0 and burial_depth>limit_fine:
    
    for i in range(2):    
        femm.mi_selectlabel(limit_fine*4/5, limit_fine*4/5)      #inner rectangle
        femm.mi_setblockprop('seabed', 0, 6*GridSize, '<None>', 0, 0, 0)
    for i in range(2): 
        femm.mi_selectlabel(limit_coarse*4/5, -limit_coarse*4/5)
        femm.mi_setblockprop('seabed', 0, 10*GridSize, '<None>', 0, 0, 0)
    
else:
    for i in range(2):    
        femm.mi_selectlabel(limit_fine*4/5, limit_fine*4/5)      #inner rectangle
        femm.mi_setblockprop('seawater', 0, 6*GridSize, '<None>', 0, 0, 0)
        
################
#Armour - 1st Layer 
################

# Apply the materials to the appropriate block labels
for i in range(1,2*NbrOfArmourElem+1):
#armour
    femm.mi_selectlabel(R_armour*sp.sin((i-1)*theta), R_armour*sp.cos((i-1)*theta))
    femm.mi_setblockprop('armour', 0, 0.5*GridSize, '<None>', 0, 0, 0)
    femm.mi_clearselected
    
################
# Area between armouring 
################
for i in range(2):
    femm.mi_selectlabel((R_armour-0.4*r_armour)*sp.sin((1-0.5)*theta), (R_armour-0.4*r_armour)*sp.cos((1-0.5)*theta))
    femm.mi_setblockprop('seawater', 0, GridSize, '<None>', 0, 0, 0)


if r_armour_2!=0:    # check if cable has a 2nd armour layer

    ################
    #Armour - 2nd Layer 
    ################    

    # Apply the materials to the appropriate block labels
    for i in range(1,2*NbrOfArmourElem2+1):
    #armour
        femm.mi_selectlabel(R_armour_2*sp.sin((i-1)*theta_2), R_armour_2*sp.cos((i-1)*theta_2))
        femm.mi_setblockprop('armour', 0, 0.5*GridSize, '<None>', 0, 0, 0)
        femm.mi_clearselected    
               
    ################
    #Over Sheath:
    ################
    
    # Apply the materials to the appropriate block labels
    for i in range(2):
        femm.mi_selectlabel(0, R_armour_2+r_armour_2+dist1+0.5*over_sheath)
        femm.mi_setblockprop('over', 0, GridSize, '<None>', 0, 0, 0)        

else:

    ################
    #Over Sheath:
    ################
    
    # Apply the materials to the appropriate block labels
    for i in range(2):
        femm.mi_selectlabel(0, R_armour+r_armour+dist1+0.5*over_sheath)
        femm.mi_setblockprop('over', 0, GridSize, '<None>', 0, 0, 0)
        
################
#Bedding
################

# Apply the materials to the appropriate block labels
for i in range(2):
    femm.mi_selectlabel(0,cond_center*sin60+r_cond_total-delta_y_triangle+0.5*bedding)
    femm.mi_setblockprop('bedding', 0, GridSize, '<None>', 0, 0, 0)

################
#Laying Up / Filling
################
for i in range(2):
    femm.mi_selectlabel(0, 0)
    femm.mi_setblockprop('bedding', 0, GridSize, '<None>', 0, 0, 0)

################
#Conductors 
################

for i in range(2):
    # Metallic Insulation Screen (e.g. lead)
    femm.mi_selectlabel(cond_center*cos60+r_cond_total-0.5*insul_screen_ME, -delta_y_triangle)
    # Sheath - Metallic 2
    femm.mi_selectlabel(0+r_cond_total-0.5*insul_screen_ME, cond_center*sin60-delta_y_triangle)
    # Sheath - Metallic 3
    femm.mi_selectlabel(-cond_center*cos60+r_cond_total-0.5*insul_screen_ME, -delta_y_triangle)
    # Apply the materials to the appropriate block labels
    femm.mi_setblockprop('M_screen', 0, GridSize, '<None>', 0, 0, 0)

for i in range(2):
    # Non Metallic Insulation Screen (semi-conductive tape)
    femm.mi_selectlabel(cond_center*cos60+r_cond_insu_screen_NM-0.5*insul_screen_NM, -delta_y_triangle)
    # Insulation Screen - Non-Metallic 2
    femm.mi_selectlabel(0+r_cond_insu_screen_NM-0.5*insul_screen_NM, cond_center*sin60-delta_y_triangle)
    # Insulation Screen - Non-Metallic 3
    femm.mi_selectlabel(-cond_center*cos60+r_cond_insu_screen_NM-0.5*insul_screen_NM, -delta_y_triangle)
    # Apply the materials to the appropriate block labels
    femm.mi_setblockprop('NM_screen', 0, GridSize, '<None>', 0, 0, 0)

for i in range(2):
    # Insulation 1
    femm.mi_selectlabel(cond_center*cos60+r_cond_insul-0.5*insulation, -delta_y_triangle)
    # Insulation 2
    femm.mi_selectlabel(0+r_cond_insul-0.5*insulation, cond_center*sin60-delta_y_triangle)
    # Insulation 3
    femm.mi_selectlabel(-cond_center*cos60+r_cond_insul-0.5*insulation, -delta_y_triangle)
    # Apply the materials to the appropriate block labels
    femm.mi_setblockprop('XLPE', 0, GridSize, '<None>', 0, 0, 0)

for i in range(2):
    # Conductor Screen 1
    femm.mi_selectlabel(cond_center*cos60+r_cond_screen-0.5*cond_screen, -delta_y_triangle)
    # Conductor Screen 2
    femm.mi_selectlabel(0+r_cond_screen-0.5*cond_screen, cond_center*sin60-delta_y_triangle)
    # Conductor Screen 3
    femm.mi_selectlabel(-cond_center*cos60+r_cond_screen-0.5*cond_screen, -delta_y_triangle)
    # Apply the materials to the appropriate block labels
    femm.mi_setblockprop('NM_screen', 0, GridSize, '<None>', 0, 0, 0)

for i in range(2):
    #Conductor 1
    femm.mi_selectlabel(cond_center*cos60, -delta_y_triangle)
    femm.mi_setblockprop('copper_conductors', 0, 0.5*GridSize, 'icoil1', 0, 0, 0)
    femm.mi_clearselected
    #Conductor 2
    femm.mi_selectlabel(0, cond_center*sin60-delta_y_triangle)
    femm.mi_setblockprop('copper_conductors', 0, 0.5*GridSize, 'icoil2', 0, 0, 0)
    femm.mi_clearselected
    #Conductor 3
    femm.mi_selectlabel(-cond_center*cos60, -delta_y_triangle);
    femm.mi_setblockprop('copper_conductors', 0, 0.5*GridSize, 'icoil3', 0, 0, 0)

# Add a "circuit property" so that we can calculate the properties of the
# coil as seen from the terminals.

femm.mi_addcircprop('icoil1', AMPS+0j, 1)
femm.mi_addcircprop('icoil2', -0.5*AMPS+AMPS*0.866j, 1)
femm.mi_addcircprop('icoil3', -0.5*AMPS-AMPS*0.866j, 1)


#Display
print('Objects properties defined')
    
#==============================================================================
# Analysis and Reporting
#==============================================================================

# We have to give the geometry a name before we can analyze it.
femm.mi_saveas('SubseaCable_model.fem');

# Run the magnetic solver (including mesh generation)
femm.mi_analyze()
# Visualize Solution in Femm
femm.mi_loadsolution()

point_value = femm.mo_getpointvalues(0,30)

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()
fig4, ax4 = plt.subplots()
fig5, ax5 = plt.subplots()
fig6, ax6 = plt.subplots()

for p in range(1,4):
    
    contour=[]
    b_value=[]
    e_value=[]
    b_value_far=[]
    e_value_far=[]
    
    for n in range(-500,500,1):
        b=femm.mo_getb(n,int(R_cable_total)+100*p)  # output B [T]
        e=femm.mo_getj(n,int(R_cable_total)+100*p)  # output J [MA/m^2]
        b_far=femm.mo_getb(n,int(R_cable_total)+1000*p)
        e_far=femm.mo_getj(n,int(R_cable_total)+1000*p) 
        
        _b_= np.sqrt(np.abs(b[0])**2+np.abs(b[1])**2)*10**6
        if burial_depth!=0 and (int(R_cable_total)+100*p)<=burial_depth:
            _e_= (np.abs(e)*10**6/seabed_conductivity)*10**6
        else:
            _e_= (np.abs(e)*10**6/seawater_conductivity)*10**6        
        
        _b_far= np.sqrt(np.abs(b_far[0])**2+np.abs(b_far[1])**2)*10**6
        if burial_depth!=0 and (int(R_cable_total)+1000*p)<=burial_depth:
            _e_far= (np.abs(e_far)*10**6/seabed_conductivity)*10**6
        else:
            _e_far= (np.abs(e_far)*10**6/seawater_conductivity)*10**6   
    
        contour.append(n)
    
        b_value.append(_b_)
        e_value.append(_e_)
        b_value_far.append(_b_far)
        e_value_far.append(_e_far)
          
    ax1.plot(contour,b_value)
    ax2.plot(contour,e_value)
    ax3.plot(contour,b_value_far)
    ax4.plot(contour,e_value_far)


contour3=[]
b_value3=[]
e_value3=[]

for n in range(int(R_cable_total)+100,3000,1):
    b=femm.mo_getb(0,n) # output B [T]
    e=femm.mo_getj(0,n) # output J [MA/m^2]
    
    _b_= np.sqrt(np.abs(b[0])**2+np.abs(b[1])**2)*10**6
    if burial_depth!=0 and n<=burial_depth:
        _e_= (np.abs(e)*10**6/seabed_conductivity)*10**6
    else:
        _e_= (np.abs(e)*10**6/seawater_conductivity)*10**6

    contour3.append(n)
    b_value3.append(_b_)
    e_value3.append(_e_)

ax5.plot(contour3,b_value3)
ax6.plot(contour3,e_value3)    
    

ax1.legend(['10cm', '20cm', '30cm'])
ax1.grid("on")
ax1.set_ylabel('Magnetic Flux Density |B|, uT')
ax1.set_xlabel('Distance along the x-axis, mm')
fig1.savefig("./magnetic_field_close.pdf")

ax2.legend(['10cm', '20cm', '30cm'])
ax2.grid("on")
ax2.set_ylabel('Electric Field |E|, uV.m')
ax2.set_xlabel('Distance along the x-axis, mm')
fig2.savefig("./electric_field_close.pdf")

ax3.legend(['1m', '2m', '3m'])
ax3.grid("on")
ax3.set_ylabel('Magnetic Flux Density |B|, uT')
ax3.set_xlabel('Distance along the x-axis, mm')
fig3.savefig("./magnetic_field_far.pdf")

ax4.legend(['1m', '2m', '3m'])
ax4.grid("on")
ax4.set_ylabel('Electric Field |E|, uV.m')
ax4.set_xlabel('Distance along the x-axis, mm')
fig4.savefig("./electric_field_far.pdf")

ax5.grid(True, which="both")
ax5.set_ylabel('Magnetic Flux Density |B|, uT')
ax5.set_xlabel('Radial distance from cable, mm')
ax5.set_yscale('log')
ax5.yaxis.set_major_formatter(mticker.ScalarFormatter())
fig5.savefig("./radial_magnetic_field.pdf")

ax6.grid(True, which="both")
ax6.set_ylabel('Electric Field |E|, uV.m')
ax6.set_xlabel('Radial distance from cable, mm')
ax6.set_yscale('log')
ax6.yaxis.set_major_formatter(mticker.ScalarFormatter())
ax6.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
fig6.savefig("./radial_electric_field.pdf")