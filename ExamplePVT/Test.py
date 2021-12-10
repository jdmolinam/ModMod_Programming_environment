#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 17:23:27 2019

@author: jac


Tests for modular models:
"""



### Imported instances of Director DO have instances of their Modules
### Import instances ONLY: 
from Temperature.Module import Dir as Dir1

from Volumen.Module import Dir as Dir2

from ModMod import Director

### Start model with empty varoables
Model = Director( t0=0.0, time_unit="", Vars={}, Modules={} )

### Merge all global vars from other directories
Model.MergeVars( [ Dir1, Dir2], call=__name__)

### Add the corresponding time unit, most be the same in both
Model.AddTimeUnit(Dir1.symb_time_unit)
Model.CheckSymbTimeUnits(Dir2)


### Add the instance of Module 1:
#Model.AddModule( 'Module1', Dir1.Modules['Module1'] )
### Or add Dir1 directly, Dir1.sch has been already defined in Temperature.Module
Model.AddDirectorAsModule( 'Module1', Dir1)

### Add the instance of Module 2:
#Model.AddModule( 'Module2', Dir2.Modules['Module2'] )
### Or add Dir2 directly, Dir2.sch has been already defined in Temperature.Module
Model.AddDirectorAsModule( 'Module2', Dir2)



### Run:

Model.PrintVars()

"""If Module1 was add directly we can do this
   If Dir1 was add as a Module, the we cannot do it!"""
### As default, Module1 uses the approximate RK Advance method
#Model.Modules['Module1'].Advance = Model.Modules['Module1'].AdvanceRK

### Re run with the analytic method
#Model.Modules['Module1'].Advance = Model.Modules['Module1'].AdvanceAnalytic


### Advance modules to time t1=1
#Model.Scheduler( t1=1, sch=[ 'Module1',  'Module2' ] )
#print("\n")
#Model.PrintVars()

Model.Run( Dt=1, n=100, sch=[ 'Module1',  'Module2' ] )
Model.PrintVars()

from pylab import subplot, subplots_adjust
subplot(311)
Model.PlotVar('P1')
subplot(312)
Model.PlotVar('V1')
subplot(313)
Model.PlotVar('T1')
subplots_adjust(hspace=1) # This line gives a horizontal space between the plots
