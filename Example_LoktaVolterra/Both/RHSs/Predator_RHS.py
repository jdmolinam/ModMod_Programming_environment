#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 14:24:32 2019

@author: jac
"""


from ModMod import StateRHS
from sympy import symbols

def o1( de, X, Y):
    return de*X*Y

def o2( ga, Y):
    return -ga*Y



class Predator_rhs(StateRHS):
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
        o_1 = o1( de=self.V('de'), X=self.Vk('X'), Y=self.Vk('Y') )
        o_2 = o2( ga=self.V('ga'), Y=self.Vk('Y'))
        return o_1 + o_2

Predator_rhs_ins = Predator_rhs() ## Make an instance of rhs


### Define the units to be used, as sympy symbols
n, d = symbols('n d') # n-number of specimens, d - days


Predator_rhs_ins.SetSymbTimeUnits(d) # days


### Define the State variables needed to test the module:
Predator_rhs_ins.AddVar( 'State', varid='X', desc="Number of specimens of prey.",\
                   units = n, val=10.0, rec=20)

Predator_rhs_ins.AddVar( 'State', varid='Y', desc="Number of specimens of predator.",\
                   units = n, val=10.0, rec=20)

Predator_rhs_ins.AddVarLocal( 'Cnts', varid='ga', desc="Gamma parameter in ODE",\
                     units = d**-1, val=1, prn=r'$\gamma$')

Predator_rhs_ins.AddVarLocal( 'Cnts', varid='de', desc="Delta parameter in ODE",\
                     units = n**-1 * d**-1, val=1, prn=r'$\delta$')



###### Test this Module
if __name__ == '__main__':
    ### Test the auxiliar functions
    #from numpy import linspace
    #from pylab import plot
    #X = linspace( 0.0, 50, num=5)
    #Y = linspace( 0.0, 50, num=100)
    #for x in X:
        #plot( Y, (lambda y: o2( ga=1, de=1, X=x, Y=y))(Y), '-')
    
    

    ### Test run RHS:
    print("Units of o1:", Predator_rhs_ins.GetFuncUnits(o1))
    print("Units of o2:", Predator_rhs_ins.GetFuncUnits(o2))
    units = Predator_rhs_ins.TestUnits('Y')
    

    
    
