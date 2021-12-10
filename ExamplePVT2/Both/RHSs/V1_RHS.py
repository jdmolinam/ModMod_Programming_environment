#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 14:15:57 2019

@author: jac
"""



from ModMod import StateRHS
from sympy import symbols


def h2( V_max, V_la, k1, T_max, T_la, V1, T1):
    return (V_max - V1)* V_la * k1 * ((T_max - T1) * T_la)/V1


class V1_rhs(StateRHS):
    """Define a RHS, this is the rhs for volumen:
        (V_max - V) V_la k1 ( (T_max - T) T_la V - T (V_max - V) V_la )/V^2 .
    """
    ### No __init__, uses the super class __init__

    def RHS( self, Dt):
        """RHS( Dt, k) = \kappa_1^{-1} F_1( t+Dt, X+k) where X is the current value of
           all state variables.  k is set in the module class.
           To access a state variable one MOST use self.Sk(varid).  One gets the state
           variable value + its corresponding k.
           
           ************* JUST CALL STATE VARIABLES WITH self.Vk ******************
        """
        ### Direct usage, NB: State variables need to used Vk, so that X+k is evaluated.
        ### This can be done with TranslateArgNames(h2)
        return h2( V_max=self.V('V_max'), V_la=self.V('V_la'), k1=self.V('k1'),\
                   T_max=self.V('T_max'), T_la=self.V('T_la'),\
                   V1=self.Vk('V1'), T1=self.Vk('T1'))
 
V1_rhs_ins = V1_rhs() ## Make an instance of rhs      




### Define the units to be used, as sympy symbols
C, s, g, cm = symbols('C s g cm')

V1_rhs_ins.SetSymbTimeUnits(s) # Seconds

V1_rhs_ins.AddVar( 'State', varid='T1', desc="Temperature of the gas in chamber",\
                   units = C, val=10.0, rec=20)

V1_rhs_ins.AddVar( 'State', varid='P1', desc="Pressure of gas in chamber",\
                   units= g / cm**2 , val=1.0, rec=20)

V1_rhs_ins.AddVar( 'State', varid='V1', desc="Volumen of chamber",\
                   units= cm**3, val=1e3, rec=20)


### Define the constants needed to test the module:
V1_rhs_ins.AddVarLocal( 'Cnts', 'k1', desc="Constant PV/T = k",\
                  units= (g * cm)/C,\
                  val=(V1_rhs_ins.V('P1') * V1_rhs_ins.V('V1'))/V1_rhs_ins.V('T1') )
### Acces to State variable value: Model.S('P1') short for Model.State['P1'].val

V1_rhs_ins.AddVarLocal( 'Cnts', 'V_max', desc="Limit volumen in exponential",\
                     units= cm**3 , val=3e3)

V1_rhs_ins.AddVarLocal( 'Cnts', 'V_la', desc="Lambda in exponential",\
                     units= cm**2 / g, val=1/60)

### These are not local constant variables, since they are also used in V1_RHS
V1_rhs_ins.AddVar( 'Cnts', 'T_max', desc="Limit temperature in exponential",\
                     units = C, val=90.0)

V1_rhs_ins.AddVar( 'Cnts', 'T_la', desc="Lambda in exponential",\
                     units = s**-1, val=0.1)



###### Test this Module
if __name__ == '__main__':
    ### Test the auxiliar functions and RHS
    print(V1_rhs_ins.RHS(0.0))

    

    ### Test run RHS:
    units = V1_rhs_ins.TestUnits('V1')
    

