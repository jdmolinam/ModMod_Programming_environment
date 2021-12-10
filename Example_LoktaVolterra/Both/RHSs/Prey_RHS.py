#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 14:24:32 2019

@author: jac
"""


from ModMod import StateRHS
from sympy import symbols


def h1( al, be, X, Y):
    return al*X - be*X*Y



class Prey_rhs(StateRHS):
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
        return h1( al=self.V('al'), be=self.V('be'), X=self.Vk('X'), Y=self.Vk('Y'))

Prey_rhs_ins = Prey_rhs() ## Make an instance of rhs


### Define the units to be used, as sympy symbols
n, d = symbols('n d') # n-number of specimens, d - days

Prey_rhs_ins.SetSymbTimeUnits(d) # days

### Define the State variables needed to test the module:
Prey_rhs_ins.AddVar( 'State', varid='X', desc="Number of specimens of prey.",\
                   units = n, val=10.0, rec=20)

Prey_rhs_ins.AddVar( 'State', varid='Y', desc="Number of specimens of predator.",\
                   units = n, val=10.0, rec=20)

Prey_rhs_ins.AddVarLocal( 'Cnts', varid='al', desc="Alpha parameter in ODE",\
                     units = d**-1, val=2/3, prn=r'$\alpha$')

Prey_rhs_ins.AddVarLocal( 'Cnts', varid='be', desc="Beta parameter in ODE",\
                     units = n**-1 * d**-1, val=4/3, prn=r'$\beta$')



###### Test this Module
if __name__ == '__main__':
    ### Test the auxiliar functions
    from numpy import linspace
    from pylab import plot
    X = linspace( 0.0, 50, num=100)
    Y = linspace( 0.0, 50, num=5)
    for y in Y:
        plot( X, (lambda x: h1( al=2/3, be=4/3, X=x, Y=y))(X), '-')
    
    

    ### Test run RHS:
    units = Prey_rhs_ins.TestUnits('X')
    

    
    
