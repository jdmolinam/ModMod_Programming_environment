#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 17:14:34 2019

@author: jac

Test of module.  This is module 2
"""

from numpy import sin, pi, clip, Inf, append, arange
from sympy import symbols

from ModMod import StateRHS, Module, Director

C, g, m, d, MJ, n_f = symbols('C g m d MJ n_f') # Symbolic use of base phisical units
n_f, n_p = symbols('n_f n_p') # number of fruits, number of plants


#################################################################
##################### Temperature ###############################
#################################################################

def h1( T_max, T_sky, T_la, sinp, Q0, T, W):
    """Auxiliar function,."""
    return (T_sky + (T_max - T_sky)*sinp - T) *(T_la/(Q0+W))

class T_rhs(StateRHS):
    """No init, uses the parent class init."""
    
    def RHS( self, Dt):
        """RHS( Dt, k) = \kappa_1^{-1} F_1( t+Dt, X+k) where X is the current value of
           all state variables.  k is a simple dictionary { 'v1':k1, 'v2':k2 ... etc}
           
           ************* JUST CALL STATE VARIABLES WITH self.Vk ******************
        """
        sinp = clip( sin( self.V('omega')*Dt * (2*pi)), 0, Inf)
        
        ### Direct usage, NB: State variables need to used Vk, so that X+k is evaluated.
        ### This can be done with TranslateArgNames(h1)
        ### Once defined h1 in your terminal run TranslateArgNames(h1)
        ### and follow the instrucions
        
        ### Note that W is a State variable but not moved in this module:
        return h1( T_max=self.V('T_max'), T_sky=self.V('T_sky'), T_la=self.V('T_la'),\
                  sinp=sinp, Q0=self.V('Q0'), T=self.Vk('T'), W=self.V('W'))
    
T_rhs_ins = T_rhs()

T_rhs_ins.SetSymbTimeUnits(d) # days

T_rhs_ins.AddVar( typ='State', varid='T', prn=r'$T$',\
            desc="Temperature", units= C, val=15.0, rec=24*60)

T_rhs_ins.AddVar( typ='State', varid='W', prn=r'$W$',\
            desc="Total weight of fruits", units= g, val=0.0)


T_rhs_ins.AddVar( typ='State', varid='T_max', prn=r'$T_m$',\
            desc="Max 'sun' temperature", units= C, val=30.0)

T_rhs_ins.AddVar( typ='State', varid='T_sky', prn=r'$T_s$',\
            desc="Temperature of sky.", units= C, val=10.0)

T_rhs_ins.AddVar( typ='Cnts', varid='T_la', prn=r'$T_\lambda$',\
            desc="Parameter in h1", units= g/d, val=10**4)

T_rhs_ins.AddVar( typ='Cnts', varid='omega', prn=r'$\omega$',\
            desc="Frequecy of sun in days", units= d**-1, val=1.0)


T_rhs_ins.AddVar( typ='Cnts', varid='Q0', prn=r'$T$',\
            desc="Fix mass (no fruits).", units= g, val=30.0)

T_rhs_ins.AddVarLocal( typ='Aux', varid='sinp', prn=r'$sin^+$',\
            desc="Auxiliar", units= 1, val=1.0)


#################################################################
##################### Radiation #################################
#################################################################

def h2( PA_max, sinp):
    return PA_max * sinp

class PA_rhs(StateRHS):
    """No init, uses the parent class init."""
    
    def RHS( self, Dt):
        """RHS( Dt ) = 
           
           ************* IN ASSIGMENT RHSs WE DON'T NEED TO CALL STATE VARS WITH self.Vk ******************
        """
        sinp = clip( sin( self.V('omega')*Dt * (2*pi)), 0, Inf)
        
        ### Direct usage, NB: State variables need to used Vk, so that X+k is evaluated.
        ### This can be done with TranslateArgNames(h1)
        ### Once defined h1 in your terminal run TranslateArgNames(h1)
        ### and follow the instrucions
        return h2( PA_max=self.V('PA_max'), sinp=sinp)
    
PA_rhs_ins = PA_rhs()

PA_rhs_ins.SetSymbTimeUnits(d)

PA_rhs_ins.AddVar( typ='State', varid='PA', prn=r'$P^A$',\
                desc="PAR", units= MJ * m**-2, val=300.00, rec=24*60)

PA_rhs_ins.AddVar( typ='Cnts', varid='PA_max', prn=r'$P^A_m$',\
                desc="Maximum PAR", units= MJ * m**-2, val=300.00)

PA_rhs_ins.AddVar( typ='Cnts', varid='omega', prn=r'$\omega$',\
            desc="Frequecy of sun in days", units= d**-1, val=1.0)

PA_rhs_ins.AddVarLocal( typ='Aux', varid='sinp', prn=r'$sin^+$',\
            desc="Auxiliar", units= 1, val=1.0)


class PA_mean_rhs(StateRHS):
    def RHS( self, DT):
        return self.V_Mean('PA')

PA_mean_rhs_ins = PA_mean_rhs()
PA_mean_rhs_ins.AddVar( typ='State', varid='PA_mean', prn=r'$P^A_m$',\
                    desc="Average PAR", units= MJ * m**-2 * d**-1, val=150.00)
 
class T_mean_rhs(StateRHS):
    def RHS( self, DT):
        return self.V_Mean('T')
    
T_mean_rhs_ins = T_mean_rhs()
T_mean_rhs_ins.AddVar( typ='State', varid='T_mean', prn=r'$T_m$',\
            desc="Average Temperature", units= C * d**-1, val=15.0)



class Climate(Module):
    def __init__( self, Dt=1/(24*60) ):
        """Climate model."""
        super().__init__( Dt ) #Time steping of module
        ### Always, use the super class __init__, theare are several other initializations
        ### Dt is 1 min

        self.AddStateRHS( 'T', T_rhs_ins)
        self.AddAssigmentStateRHS( 'PA', PA_rhs_ins)
        self.AddAssigmentStateRHS( 'PA_mean', PA_mean_rhs_ins)
        self.AddAssigmentStateRHS( 'T_mean', T_mean_rhs_ins)

    def Advance(self, t1):
        """Advance the module from the current time to time t1.
           Return 1 if succesful.
           Same as in ModMod:
        """

        self.AdvanceRungeKutta(t1)
        tt = append( arange( self.t(), t1, step=self.Dt), [t1]) # tt = array([t, t+Dt, t+2Dt, ... , t1])
        for t in tt:
            self.AdvanceAssigment(t1)
        
        return 1



    

""" *************** Test run for this module only: ********** """
###### Test this Module
if __name__ == '__main__':


    ### Start model with empty variables
    Dir = Director( t0=0.0, time_unit="", Vars=dict(), Modules=dict() )

    symb_time_units = T_rhs_ins.CheckSymbTimeUnits(PA_rhs_ins)
    ### Will rise an error if it fails

    ### Start model with empty variables
    Dir = Director( t0=0.0, time_unit=symb_time_units, Vars={}, Modules={} )

    Dir.MergeVarsFromRHSs( [ T_rhs_ins, PA_rhs_ins, PA_mean_rhs_ins, T_mean_rhs_ins], call=__name__)

    Climate_ins = Climate()

    ### Add an instance of Module 1:
    Dir.AddModule( 'Climate', Climate_ins )
    Dir.sch = [ 'Climate' ]



    ### Add an instance of this:
    #Dir.AddModule( 'Climate', Climate() )

    from sympy import sin, pi
    clip = lambda x, a, b: 1 #Use the identity for unit testing purposes
    #T_rhs_ins.TU_IA()
    T_rhs_ins.TestUnits( lhs='T' )
    PA_rhs_ins.TestUnits( lhs='PA', assigm=True )
    Climate_ins.RHS_TestUnits

    from numpy import sin, pi, clip, linspace
    from pylab import plot, subplot, tight_layout, figure, xlabel, ylabel
    
    tt = linspace( 0, 20, num=1000)
    pa = [PA_rhs_ins.RHS(t) for t in tt]
    #plot( tt, pa, '-')

    ### Test run it:

    Dir.PrintVars()
    ### Advance module 'Module2' with no parameters:
    Dir.Scheduler( t1=1/24, sch= Dir.sch )
    print("\n")
    Dir.PrintVars()

    Dir.Run( Dt=1/24, n=20*24, sch= Dir.sch)
    

    figure(1)
    subplot(211)
    Dir.PlotVar('PA_mean')
    subplot(212)
    Dir.PlotVar('T_mean')
    tight_layout()


