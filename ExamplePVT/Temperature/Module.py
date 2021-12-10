#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 17:11:31 2019

@author: jac

Test of module.  This is module 1
"""

from numpy import exp
from sympy import symbols

from ModMod import Module, StateRHS, Director

def h1( T_max, T_la, T1):
    return (T_max - T1)*T_la

class T1_rhs(StateRHS):
    """Define a RHS, this is the rhs for temperature: (T_max-T) T_la."""
    ### No __init__, uses the super class __init__

    def RHS( self, Dt):
        """RHS( Dt ) = \kappa_1^{-1} F_1( t+Dt, X+k) where X is the current value of
           all state variables.  k is a simple dictionary { 'v1':k1, 'v2':k2 ... etc}
           
           ************* JUST CALL STATE VARIABLES WITH self.Vk ******************
        """
        return h1( T_max=self.V('T_max'), T_la=self.V('T_la'), T1=self.Vk('T1'))
        
    

class Module1(Module):
    def __init__( self, Dt=0.1):
        """Models one part of the process, uses the shared variables
           from Director.
           Increases the temperature with an exponential law, increases the pressure
           accordingly to P = (k T)/V .
           Dt=0.1, default Time steping of module
        """
        super().__init__(Dt) #Time steping of module
        ### Always, use the super class __init__, theare are several other initializations

        ### Module specific constructors, add RHS's
        self.AddStateRHS( 'T1', T1_rhs()) ## The the only one State RHS

    def Init(self):
        """Further initializations when the director has been set.
           Init is called by SetDirector method.
        """
        self.T0 = self.V('T1') #Initial value, only when director is established

    def AdvanceAnalytic( self, t1):
        """Temperature T1 increases as T1(0) + (T_max-T1(0))*(1-exp(-t*lambda)).
           Increase pressure as P = (k T)/V """
        self.V_Set( 'T1', self.T0 +\
                (self.V('T_max')-self.T0) * (1 - exp(-t1*self.V('T_la'))) )
        self.V_Set( 'P1', (self.V('k1') * self.V('T1'))/self.V('V1') )

        return 1

    def AdvanceRK( self, t1):
        """Temperature T1 increases as \frac{dT}{dt} = (T_max-T) T_la; T(0) = T0.
           This is defined in the StateRHSs, which is only T1_rhs('T1') .
           Increase pressure as P = (k T)/V """
        
        self.AdvanceRungeKutta(t1)
        
        self.V_Set( 'P1', (self.V('k1') * self.V('T1'))/self.V('V1') )

        return 1

""" *************** Test run for this module only: ********** """

C, g, cm, s = symbols('C g cm s') # Symbolic use of units

### Start model with empty variables
Dir = Director( t0=0.0, time_unit= s, Vars=dict(), Modules=dict() )

### Define the State variables needed to test the module:
Dir.AddVar( typ='State', varid='T1', desc="Temperature of the gas in chamber",\
           units= C, val=10.0, rec=20, prn=r'$T_1$')

Dir.AddVar( 'State', varid='P1', desc="Pressure of gas in chamber",\
                   units= g/cm**2, val=1.0, rec=20, prn=r'$P_1$')

Dir.AddVar( 'State', varid='V1', desc="Volumen of chamber",\
                   units= cm**3, val=1e3, rec=20, prn=r'$V_1$')


### Define the constants needed to test the module:
Dir.AddVar( 'Cnts', varid='k1', desc="Constant PV/T = k",\
                  units=g * cm/C,\
                  val=(Dir.V('P1') * Dir.V('V1'))/Dir.V('T1') )
### Acces to State variable value: Model.S('P1') short for Model.State['P1'].val

Dir.AddVarLocal( 'Cnts', varid='T_max', desc="Limit temperature in exponential",\
                     units= C, val=90.0)

Dir.AddVarLocal( 'Cnts', varid='T_la', desc="Lambda in exponential",\
                     units= s**-1, val=0.1)

### Add an instance of Module 1:
Dir.AddModule( 'Module1', Module1() )
### Set the type of Advance method
Dir.Modules['Module1'].Advance = Dir.Modules['Module1'].AdvanceRK
### And the scheduling:
Dir.sch = [ 'Module1' ]

###### Test this Module
if __name__ == '__main__':

    ### Test Run it:
    
    Dir.Modules['Module1'].RHS_TestUnits()
    
    ### Test for the Runge-Kutta evaluation
    #Dir.Modules['Module1'].Advance = Dir.Modules['Module1'].AdvanceRK
    ### Test for the Aanalytic evaluation
    Dir.Modules['Module1'].Advance = Dir.Modules['Module1'].AdvanceAnalytic

    print("Test run for Module 1:\n")
    Dir.PrintVars()
    ### Advance module 'Module1':
    Dir.Scheduler( t1=1, sch= Dir.sch )
    print("\n")
    Dir.PrintVars()

