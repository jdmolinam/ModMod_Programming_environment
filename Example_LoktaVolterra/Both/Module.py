#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 17:11:31 2019

@author: jac

Test of module.  This is module 1
"""

    
from ModMod import Module, Director
from RHSs.Prey_RHS import Prey_rhs_ins
from RHSs.Predator_RHS import Predator_rhs_ins


class Module1(Module):
    def __init__( self, Dt=0.1):
        """Models one part of the process, uses the shared variables
           from Director.
           Increases the temperature with an exponential law, increases the pressure
           accordingly to P = (k T)/V .
           Dt=0.1, default Time steping of module
        """
        super().__init__(Dt) #Time steping of module
        ### Always, use the super class __init__, theare are several otjer initializations

        ### Module specific constructors, add RHS's
        self.AddStateRHS( 'X', Prey_rhs_ins)
        self.AddStateRHS( 'Y', Predator_rhs_ins)
        #print("State Variables for this module:", self.S_RHS_ids)

    def Advance( self, t1):
        """Temperature T1 increases as \frac{dT}{dt} = (T_max-T) T_la; T(0) = T0.
           This is defined in the StateRHSs, which is only T1_rhs('T1') .
           Increase pressure as P = (k T)/V """
        
        self.AdvanceRungeKutta(t1)
        
        return 1


symb_time_units = Prey_rhs_ins.CheckSymbTimeUnits(Predator_rhs_ins)
### Will rise an error if it fails

### Start model with empty variables
Dir = Director( t0=0.0, time_unit=symb_time_units, Vars={}, Modules={} )

Dir.MergeVarsFromRHSs( [ Prey_rhs_ins, Predator_rhs_ins], call=__name__)

### Add an instance of Module 1:
Dir.AddModule( 'Module1', Module1() )
Dir.sch = [ 'Module1' ]


""" *************** Test run for this module only: ********** """

###### Test this Module
if __name__ == '__main__':


    ### Test Run it:
    print("\n\nTest run for Module 1:\n")
    
    Dir.Modules['Module1'].RHS_TestUnits()
    
    #Dir.PrintVars()
    ### Advance module 'Module1' with steps=10:
    Dir.Scheduler( t1=1, sch=Dir.sch )
    print("\n")
    Dir.PrintVars()

