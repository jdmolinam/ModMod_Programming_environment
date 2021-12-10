#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 17:23:27 2019

@author: jac


Tests for modular models:
"""

from numpy import floor, sin, pi
from scipy.stats import norm

### Imported instances of Director DO have instances of their Modules
### Import instances ONLY: 
from Fruit.Module import PlantDirector
from Climate.Module import Climate, T_rhs_ins, PA_rhs_ins, PA_mean_rhs_ins, T_mean_rhs_ins

from sympy import symbols
C, g, m, d, MJ, n_f = symbols('C g m d MJ n_f') # Symbolic use of base phisical units
n_f, n_p = symbols('n_f n_p') # number of fruits, number of plants

#from Climate.Module import ClimateDir_ins

from ModMod import Director

class GreenHouse(Director):
    def Scheduler( self, t1, sch):
        """Advance the modules to time t1. sch is a list of modules id's to run
           its Advance method to time t1.
           
           Advance is the same interface, either if single module or list of modules.
        """
        
        for mod in sch:
            if self.Modules[mod].Advance(t1) != 1:
                print("Director: Error in Advancing Module '%s' from time %f to time %f" % ( mod, self.t, t1))
        self.t = t1
        
        ### Update Total weight and total number of fruits
        t_w_current = 0.0
        t_w_hist = 0.0
        t_n_f = 0
        for p, plant in enumerate(Model.PlantList):
            t_w_current += Model.Modules[plant].Modules['Plant'].V('Q')
            t_w_hist += Model.Modules[plant].Modules['Plant'].V('Q_h')
            t_n_f += Model.Modules[plant].Modules['Plant'].n_fruits
        self.V_Set( 'W', t_w_current)
        self.V_Set( 'H', t_w_hist)
        self.V_Set( 'NF', t_n_f)
        
        if 0.0 < self.t - floor(self.t) < 1/24:
            self.V_Set( 'T_max', 25 + 5*sin(self.t/360 * 2*pi))
            self.V_Set( 'T_sky', 10 + 5*sin(self.t/360 * 2*pi))
            print("%5.2f, T_max: %4.1f T_sky: %4.1f" %\
                  ( self.t, self.V('T_max'), self.V('T_sky')))
            #T_max = input("%5.2f, T_max %f" % (self.t,self.V('T_max')))
            #if T_max != "":
            #    self.V_Set( 'T_max', float(T_max))
            
            
        
    

### Start model with empty varoables
Model = GreenHouse( t0=0.0, time_unit="", Vars={}, Modules={} )

### Create n_plants with beta coefficients:
beta_list = [1.0, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
Model.PlantList = []
for p, beta in enumerate(beta_list):
    ### Make and instance of a Plant
    Dir = PlantDirector(beta=beta)
    
    ### Merge all ***global*** vars from plant
    Model.MergeVars( [ Dir ], call=__name__)

    ### Add the corresponding time unit, most be the same in both
    Model.AddTimeUnit(Dir.symb_time_unit)
    #Model.CheckSymbTimeUnits, all repeated instances of the Plant Director-Module 

    ### Add Plant directly, Dir.sch has been already defined
    Model.AddDirectorAsModule( "Plant%d" % p, Dir)

    Model.PlantList +=["Plant%d" % p]

Model.sch = Model.PlantList.copy()

### Add the climate module:
symb_time_units = T_rhs_ins.CheckSymbTimeUnits(PA_rhs_ins)
### Will rise an error if it fails

Model.MergeVarsFromRHSs( [ T_rhs_ins, PA_rhs_ins, PA_mean_rhs_ins, T_mean_rhs_ins], call=__name__)

Climate_ins = Climate()

### Add an instance of Module 1:
Model.AddModule( 'Climate', Climate_ins )

Model.sch += ['Climate']

Model.AddVarLocal( typ='State', varid='H', prn=r'$H$',\
           desc="Histoiric weight of all harvested fruits.", units= g, val=0.0)

Model.AddVarLocal( typ='State', varid='NF', prn=r'$Q$',\
           desc="Current number fruits", units= n_f, val=0.0)



Model.PrintVars()


### Run:

from pylab import plot, subplot, figure, tight_layout


Model.Run( Dt=1/24, n=100*24, sch= Model.sch)
figure(2)
subplot(311)
Model.PlotVar('T_mean')
Model.PlotVar('T')
subplot(312)
Model.PlotVar('W')
subplot(313)
Model.PlotVar('H')

tight_layout()



     
