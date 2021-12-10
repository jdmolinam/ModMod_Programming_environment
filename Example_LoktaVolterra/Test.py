#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 17:23:27 2019

@author: jac


Tests for modular models:
"""



### Imported instances of Models do not have instances of their Modules
### Comment the lines after testing the modules
from Both.Module import Dir


from ModMod import Director
### Start model containing the two Modules variables
### Reapeated variables are overwritten, the lastone defined remains. 

Model = Director(  t0=0.0, time_unit="", Vars={}, Modules={} )

Model.MergeVars( Dir, call=__name__)
Model.AddTimeUnit(Dir.symb_time_unit)



### Add an instance of Module 1:
#Model.AddModule( 'Module1', Dir['Module1'] )

### Add Director as Modlue:
Model.AddDirectorAsModule( 'Module1', Dir )


### Run:

print("\nInitial values:")
Model.PrintVars()

### Advance module to time t1=1
Model.Scheduler( t1=1, sch=[ 'Module1' ] )
#print("\n")
#Model.PrintVars()

Model.Run( Dt=1, n=365*3, sch=[ 'Module1' ] )

print("\nFinal values:")
Model.PrintVars()

from pylab import plot, subplot, tight_layout, figure, xlabel, ylabel

figure(1)
subplot(211)
Model.PlotVar('X')
subplot(212)
Model.PlotVar('Y')
tight_layout()

#figure(2)
#plot( Model.Output[:,1], Model.Output[:,2], '-')
#xlabel(Model.save[0])
#ylabel(Model.save[1])


