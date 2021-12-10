#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 17:14:34 2019

@author: jac

Test of module.  This is module 2
"""

from numpy import exp
from sympy import symbols
C, g, cm, s = symbols('C g cm s') # Symbolic use of units

from ModMod import Module, Director, StateRHS


def h2( V1_init, P1_init, V_max, V_la, P1):
    """Auxiliar function, how volumen increases with pressure."""
    return V1_init + (V_max-V1_init) * (1 - exp(- (P1 - P1_init) * V_la))

class V1_rhs_asigment(StateRHS):
    """Define a RHS, ***this an assigment RHS***, V1 = h2(...), NO ODE."""
    ### No __init__, uses the super class __init__
    
    def RHS( self, Dt):
        """RHS( Dt ) = 
           
           ************* IN ASSIGMENT RHSs WE DON'T NEED TO CALL STATE VARS WITH self.Vk ******************
        """
        ### 'V1_init' and 'P1_init' are local variables with the initail values of V1 and P1
        
        return h2( V1_init=self.V('V1_init'), P1_init=self.V('P1_init'), V_max=self.V('V_max'),\
                   V_la=self.V('V_la'),  P1=self.V('P1'))

V1_rhs_asigment_ins = V1_rhs_asigment()

V1_rhs_asigment_ins.AddVar( 'State', varid='V1', prn=r"$V_1$",\
    desc="Volumen of chamber", units= cm**3, val=1e3, rec=20)

V1_rhs_asigment_ins.AddVar( 'State', varid='P1', prn=r"$P_1$", desc="Pressure of gas in chamber",\
                   units= g/cm**2, val=1.0, rec=20)

V1_rhs_asigment_ins.AddVarLocal( 'Cnts', varid='V_max', desc="Limit volumen in exponential",\
                     units= cm**3, val=3e3)

V1_rhs_asigment_ins.AddVarLocal( 'Cnts', varid='V_la', desc="Lambda in exponential",\
                     units= cm**2/g, val=1/60) # Correct units! [1/P1]

V1_rhs_asigment_ins.AddVarLocal( 'Aux', varid='V1_init', prn=r"$V_1(0)$",\
    desc=r"Initial value for $V_1(0)$", units= cm**3, val=1e3, rec=1)

V1_rhs_asigment_ins.AddVarLocal( 'Aux', varid='P1_init', prn=r"$P_1(0)$",\
    desc=r"Initial value for $P_1$", units= g/cm**2, val=V1_rhs_asigment_ins.V('P1'), rec=1)

V1_rhs_asigment_ins.SetSymbTimeUnits(s) # Seconds

   
def h3( k1, T1, V1):
    return k1*T1/V1

class P1_rhs_asigment(StateRHS):
    """Define a RHS, ***this an assigment RHS***, V1 = h2(...), NO ODE."""
    ### No __init__, uses the super class __init__
    
    def RHS( self, Dt):
        """RHS( Dt ) = 
           
           ************* IN ASSIGMENT RHSs WE DON'T NEED TO CALL STATE VARS WITH self.Vk ******************
        """
        
        return h3( k1=self.V('k1'), T1=self.V('T1'), V1=self.V('V1'))
        
P1_rhs_asigment_ins = P1_rhs_asigment()

P1_rhs_asigment_ins.AddVar( 'State', varid='P1', prn=r"$P_1$", desc="Pressure of gas in chamber",\
                   units= g/cm**2, val=1.0, rec=20)

P1_rhs_asigment_ins.AddVar( typ='State', varid='T1', prn=r"$T_1$",\
    desc="Temperature of the gas in chamber", units= C, val=10.0, rec=20)

P1_rhs_asigment_ins.AddVar( 'State', varid='V1', prn=r"$V_1$",\
    desc="Volumen of chamber", units= cm**3, val=1e3, rec=20)


P1_rhs_asigment_ins.AddVar( 'Cnts', varid='k1', desc="Constant PV/T = k",\
                  units=g * cm/C,\
                  val=(V1_rhs_asigment_ins.V('P1') * P1_rhs_asigment_ins.V('V1'))/P1_rhs_asigment_ins.V('T1') )

P1_rhs_asigment_ins.SetSymbTimeUnits(s) # Seconds


class Module2(Module):
    def __init__( self, Dt=None ):
        """Increases Volumen with pressure, with exp model."""
        super().__init__( Dt ) #Time steping of module
        ### Always, use the super class __init__, theare are several other initializations
    
        self.AddAssigmentStateRHS( 'V1', V1_rhs_asigment_ins )
        self.AddAssigmentStateRHS( 'P1', P1_rhs_asigment_ins )
    
    def Init(self):
        """Further initializations when the director has been set.
           Init is called by SetDirector method.
        """
        self.V_Set( 'V1_init', self.V('V1')) #Save initial value, only when director is established
        self.V_Set( 'P1_init', self.V('P1')) #Initial value

    def Advance( self, t1 ):
        """Volume V1 increases with pressure P1 as V1(0) + V_max*(1-exp(- (P(t)-P(0)) * V_la)).
           Update pressure as P = (k T)/V ... Does not steps in time only updates the variables."""
        ### Use ModMod.TranslateArgNames here, but no need to add k to state vars

        self.AdvanceAssigment(t1)

        return 1
    

""" *************** Test run for this module only: ********** """




### Start model with empty variables
Dir = Director( t0=0.0, time_unit= None, Vars={}, Modules={} )

Dir.MergeVarsFromRHSs( [ V1_rhs_asigment_ins, P1_rhs_asigment_ins], call=__name__)

symb_time_units = V1_rhs_asigment_ins.CheckSymbTimeUnits(P1_rhs_asigment_ins)

Dir.AddTimeUnit(symb_time_units)


### Add an instance of this:
Dir.AddModule( 'Module2', Module2() )
Dir.sch = [ 'Module2' ]

###### Test this Module
if __name__ == '__main__':

    print("Same time units? ",V1_rhs_asigment_ins.CheckSymbTimeUnits(P1_rhs_asigment_ins))
    print("\n\n")
    from sympy import exp ## Override exp function from numpy and import the sympy version
    ### Test run RHSs:
    units1 = V1_rhs_asigment_ins.TestUnits( lhs='V1', assigm=True)
    units2 = P1_rhs_asigment_ins.TestUnits( lhs='P1', assigm=True)
    from numpy import exp ## Return to the numpy version
    
    ### Test run for Module:

    print("\n\n")
    Dir.PrintVars()
    ### Advance module 'Module2' with no parameters:
    Dir.Scheduler( t1=1, sch= Dir.sch )
    print("\n")
    Dir.PrintVars()



