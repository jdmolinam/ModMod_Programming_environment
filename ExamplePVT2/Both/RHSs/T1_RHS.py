#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 14:24:32 2019

@author: jac
"""


from ModMod import StateRHS
from sympy import symbols


def h1( T_max, T_la, T1):
    return (T_max - T1)*T_la



class T1_rhs(StateRHS):
    """Define a RHS, this is the rhs for temperature: (T_max-T) T_la."""
    ### No __init__, uses the super class __init__

    def RHS( self, Dt):
        """RHS( Dt, k) = \kappa_1^{-1} F_1( t+Dt, X+k) where X is the current value of
           all state variables.  k is a simple dictionary { 'v1':k1, 'v2':k2 ... etc}
           
           ************* JUST CALL STATE VARIABLES WITH self.Vk ******************
        """
        ### Direct usage, NB: State variables need to used Vk, so that X+k is evaluated.
        ### This can be done with TranslateArgNames(h1)
        ### Once defined h1 in your terminal run TranslateArgNames(h1)
        ### and follow the instrucions
        return h1( T_max=self.V('T_max'), T_la=self.V('T_la'), T1=self.Vk('T1'))

T1_rhs_ins = T1_rhs() ## Make an instance of rhs


### Define the units to be used, as sympy symbols
C, s = symbols('C s')

T1_rhs_ins.SetSymbTimeUnits(s) # Seconds

### Define the State variables needed to test the module:
T1_rhs_ins.AddVar( 'State', varid='T1', desc="Temperature of the gas in chamber",\
                   units = C, val=10.0, rec=20)

### These are not local constant variables, since they are also used in V1_RHS
T1_rhs_ins.AddVar( 'Cnts', varid='T_max', desc="Limit temperature in exponential",\
                     units = C, val=90.0)

T1_rhs_ins.AddVar( 'Cnts', varid='T_la', desc="Lambda in exponential",\
                     units = s**-1, val=0.1)



###### Test this Module
if __name__ == '__main__':
    ### Test the auxiliar functions
    from numpy import linspace
    from pylab import plot
    T1 = linspace( 10.0, 90, num=100)
    plot( T1, (lambda T1: h1( T_max=90, T_la=0.1, T1=T1))(T1), '-')
    
    

    ### Test run RHS:
    units = T1_rhs_ins.TestUnits('T1')
    

    
    
