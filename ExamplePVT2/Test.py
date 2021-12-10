#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 17:23:27 2019

@author: jac


Tests for modular models:
"""



### Imported instances of Models DO have instances of their Modules
### Comment the lines after testing the modules
from Both.Module import Dir


from ModMod import Director
### Start model containing the two Modules variables
### Reapeated variables are overwritten, the lastone defined remains. 

Model = Director(  t0=0.0, time_unit="", Vars={}, Modules={} )

Model.MergeVars( Dir, call=__name__)
Model.AddTimeUnit(Dir.symb_time_unit)



### Add the instance of Module 1, from Dir:
### This does not work since Model does not have any local variables
### for example 'V_max'
#Model.AddModule( 'Module1', Dir.Modules['Module1'] )

### We need to add Dir as a slave director:
Model.AddDirectorAsModule( 'Module1', Dir)

### Note that Model does not have the local Var's in Dir

## Advance will call Module1 with the scheduling self.sch



### Run:

print("\nInitial values:")
Model.PrintVars()

### Advance module to time t1=1
#Model.Scheduler( t1=1, sch=[ 'Module1' ] )
#print("\n")
#Model.PrintVars()

Model.Run( Dt=1, n=100, sch=[ 'Module1' ] )

print("\nFinal values:")
Model.PrintVars()

from pylab import subplot, subplots_adjust
subplot(311)
Model.PlotVar('P1')
subplot(312)
Model.PlotVar('V1')
subplot(313)
Model.PlotVar('T1')
subplots_adjust(hspace=1) # This line gives a horizontal space between the plots