#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 17:11:31 2019

@authors: jac and jdmolina

Test of module.  This is module 1
"""


from numpy import exp, floor, linspace, clip, arange, append
from sympy import symbols
C, g, m, d, MJ, n_f = symbols('C g m d MJ n_f') # Symbolic use of base phisical units
n_f, n_p = symbols('n_f n_p') # number of fruits, number of plants

kg = 10**3 * g
s  = d / (60*60*24) ###seconds
#J  = kg * m**2 * s**-2 ###Joules 
#MJ = 10**6 * J ### Mega Joules

from ModMod import Module, StateRHS, Director

Inf = exp(300)


"""
*******  Note, the original TF is quite unsensitive to PA_mean ******
def TF( k1_TF, k2_TF, k3_TF, PA_mean, T_mean, Dt):
    ### ORIGINAL Floration rate. DOES NOT DEPEND MUCH ON PA_MEAN!!
    return (-0.75*k2_TF + 0.09*T_mean)*(1-exp(-(1*k1_TF+PA_mean)/(2*k1_TF)))*k3_TF * Dt
"""

def TF( k1_TF, k2_TF, k3_TF, PA_mean, T_mean, Dt):
    """Floration rate. TEMPORARY ... k1_TF = 150"""
    return (-0.75*k2_TF + 0.09*T_mean)*(1-exp(-PA_mean/k1_TF))*k3_TF * Dt

def TF( k1_TF, k2_TF, k3_TF, PA_mean, T_mean, Dt):
    ### ORIGINAL Floration rate. DOES NOT DEPEND MUCH ON PA_MEAN!!
    return (-0.75*k2_TF + 0.09*T_mean)*(1-exp(-(1*k1_TF+PA_mean)/(2*k1_TF)))*k3_TF * Dt

def f( k1_TF, k2_TF, PA_mean, T_mean, Dt):
    return -(1*k1_TF+PA_mean)/(2*k1_TF)

def Y_pot(k2_TF, C_t, B, D, M, X, T_mean):
    """Growth potential of each fruit."""
    return (T_mean - 10*k2_TF) *\
        B * M * exp(B * ( X - C_t))/(1 + D * exp(B * (X - C_t)))**( 1 + 1/D)

def Y_pot_veg(k2_TF, a, b, T_mean):
    """Growth potencial of the vegetative part"""
    return a*k2_TF + b*T_mean
        
def t_wg( dw_ef, A, f_wg):
    """Growth rate."""
    return f_wg * A / dw_ef

def f_wg( Y_pot, Y_sum):
    """Sink stregth, without kmj."""
    return Y_pot / Y_sum  ### No units

    
class Q_rhs(StateRHS):
    """
    Q is the weight of all fruits for plant
    """
    def __init__( self ):
        """Define a RHS, ***this an assigment RHS***, V1 = h2(...), NO ODE."""
        ### uses the super class __init__
        super().__init__()
        
        ### Define variables here.  Each fruit will have repeated variables.
        ### Later some will be shared and the Local variable swill be exclusive
        ### of each fruit.

        self.SetSymbTimeUnits(d) # days

        ### State variables coming from the climate model
        self.AddVar( typ='State', varid='T_mean', prn=r'$T_m$',\
            desc="Average Temperature", units= C * d**-1, val=15.0)

        self.AddVar( typ='State', varid='PA_mean', prn=r'$P^A_m$',\
                desc="Average PAR", units= MJ * m**-2 * d**-1, val=150.00)

        ### Local variables, separate for each plant
        self.AddVarLocal( typ='State', varid='A', prn=r'$A$',\
           desc="Total assimilates per plant.", units= g / d, val=30.0)
        
        self.AddVarLocal( typ='StatePartial', varid='Q', prn=r'$Q$',\
           desc="Weight of all fruits for plant", units= g, val=0.0)

        self.AddVarLocal( typ='StatePartial', varid='Q_h', prn=r'$W1$',\
           desc="Historic weight of all harvested fruits for plant", units= g, val=0.0)

        self.AddVarLocal( typ='StatePartial', varid='Y_sum', prn=r'$Y_{sum}$',\
           desc="Sum of all potential growths", units= g/d**2, val=0.0)


        ### Canstants, shared by all plants.  Shared Cnts cannot be local
        self.AddVar( typ='Cnts', varid='k1_TF', prn=r'$k1_TF$',\
           desc="Aux in function TF", units= MJ * m**-2 * d**-1, val=300.0)

        self.AddVar( typ='Cnts', varid='k2_TF', prn=r'$k2_TF$',\
           desc="Aux in function TF", units= C * d**-1, val=1.0)

        self.AddVarLocal( typ='Cnts', varid='k3_TF', prn=r'$k3_TF$',\
           desc="Aux in function TF", units= n_f * C**-1, val=1.0)


        self.AddVarLocal( typ='Cnts', varid='dw_ef', prn=r'$dw_{efficacy}$',\
           desc="Constant in t_wg for fruits", units= 1, val=1.3)
        
        self.AddVarLocal( typ='Cnts', varid='dw_ef_veg', prn=r'$dw_{efficacy}$',\
           desc="Constant in t_wg for vegetative part", units= 1, val=1.15)

        self.AddVarLocal( typ='Cnts', varid='C_t', prn=r'$C_t$',\
           desc="Constant in Y_pot", units= C * d, val=131.0)

        self.AddVarLocal( typ='Cnts', varid='B', prn=r'$B$',\
           desc="Constant in Y_pot", units= (C * d)**-1, val=0.017)

        self.AddVarLocal( typ='Cnts', varid='D', prn=r'$D$',\
           desc="Constant in Y_pot", units= 1, val=0.011)

        self.AddVarLocal( typ='Cnts', varid='M', prn=r'$M$',\
           desc="Constant in Y_pot", units= g, val=60.7)
        
        self.AddVarLocal( typ='Cnts', varid='a', prn=r'$a$',\
           desc="Constant in Y_pot_veg", units= 1, val=3.3)
        
        self.AddVarLocal( typ='Cnts', varid='b', prn=r'$b$',\
           desc="Constant in Y_pot_veg", units= 1, val=0.25)


    def RHS( self, Dt):
        """RHS( Dt ) = 
           
           ************* IN ASSIGMENT RHSs WE DON'T NEED TO CALL STATE VARS WITH self.Vk ******************
        """
        ### The assigment is the total weight of the fuits
        return self.V('Q')



class Plant(Module):
    def __init__( self, beta, Q_rhs_ins, Dt=1):
        """Models one plant growth, with a variable number of fruits."""

        super().__init__(Dt) #Time steping of module, days
        ### Always, use the super class __init__, there are several other initializations
        
        self.beta = beta ## most be in (0,1]
    
        ### Time units= hours

        ### Vegetative part
        self.veget = [0.0 , 0.0] ## characteristics for vegetative part: Weight and growth potential 

        ### Fruist
        self.fruits = [] # No fruits
        self.n_fruits = 0 ## Current number of fruits
        self.new_fruit = 0  ## Cummulative number of fruits
        self.m = 4 ## Number of characteristics for each fruit: thermic age, weight, growth potential and Michaelis-Menten constant
        ### Module specific constructors, add RHS's

        self.AddStateRHS( 'Q', Q_rhs_ins)

    def Advance( self, t1):
        """Update the plant/fruit growth. Update global variables, to time t1."""
        
        ### This creates a set of times knots, that terminates in t1 with
        ### a Deltat <= self.Dt
        tt = append( arange( self.t(), t1, step=self.Dt), [t1])
        #print(tt)
        steps = len(tt)
        for i in range( 1, steps):
            ### Check if a fruit has reached is maximum thermic age, then harvest it
            harvest = []
            for h, fruit in enumerate(self.fruits): # h is the indice and fruit is the object
                if fruit[0] > 275: # It is harvested when a fruit reaches a thermic age of 275 °C
                    harvest += [h]
                    self.n_fruits -= 1
                    w = self.V( 'Q_h') + fruit[1]
                    self.V_Set( 'Q_h', w)
            [self.fruits.pop(i) for i in harvest]# Harvest
            
            ### With the Floration Rate, create new fruits
            PA_mean_i = self.beta * self.V('PA_mean')
            self.new_fruit += TF( k1_TF=self.V('k1_TF'), k2_TF=self.V('k2_TF'), k3_TF=self.V('k3_TF'),\
                    PA_mean=PA_mean_i, T_mean=self.V('T_mean'), Dt=tt[i]-tt[i-1])
            new_fruit_n = self.new_fruit 
            if new_fruit_n >= 1:
                #nw = new_fruit_n
                nw = int(floor(self.new_fruit))
                for nf in range(nw):
                    ### Add new fruit
                    self.fruits += [[ 0.0, 0.0, 0.0, 0.0]]  
                    self.n_fruits += 1 
                ### Leave the rational part of new_fruit
                self.new_fruit = max( 0, self.new_fruit - nw)
            ### Update thermic age of all fruits
            for fruit in self.fruits:
                fruit[0] += ( max( 0 , self.V('T_mean') - 10 ) )* (tt[i]-tt[i-1]) ## Thermic age never decreases
            ### Update growth potencial for vegetative part
            self.veget[1] = self.V('a') + self.V('b')*self.V('T_mean') 
            ### Update Growth potential and Michaelis-Menten constants of all fruits
            tmp = 0.0
            tmp1 = self.veget[1] / self.V('A') # start with the growth potencial of vegetative part
            for fruit in self.fruits:
                x = fruit[0] ## Thermic age
                ### Michaelis-Menten constants 
                if x <= self.V('C_t') :
                    fruit[3] = 0.05*tmp*(self.V('C_t') - x) / self.V('C_t')
                ### Growth potential
                fruit[2] = clip( Y_pot( k2_TF=self.V('k2_TF'), C_t=self.V('C_t'),\
                     B=self.V('B'), D=self.V('D'), M=self.V('M'), X=x, T_mean=self.V('T_mean')),\
                     a_min=0, a_max=exp(300))
                tmp += fruit[2]
                tmp1 += fruit[2] / ( fruit[3] + self.V('A') )
            #self.V_Set( 'Y_sum', tmp)
            ### Update weight of vegetative part
            f_wg_veg =  self.veget[1] / ( self.V('A') * tmp1 ) # The sink strentgh of vegetative part
            self.veget[0] += t_wg( dw_ef=self.V('dw_ef_veg'), A=self.V('A'), f_wg=f_wg_veg) * (tt[i]-tt[i-1])
            #### Update weight of all fruits
            tmp2 = 0.0
            for fruit in self.fruits:
                f_wg =  fruit[2] / ( ( fruit[3] + self.V('A') ) * tmp1 ) # The sink strentgh of the fruit
                fruit[1] += t_wg( dw_ef=self.V('dw_ef'), A=self.V('A'), f_wg=f_wg) * (tt[i]-tt[i-1])
                tmp2 += fruit[1] #Total weight
            self.V_Set( 'Q', tmp2)
            self.AdvanceAssigment(t1) # Set Q
        return 1


def PlantDirector( beta, return_Q_rhs_ins=False):
    """Build a Director to hold a Plant, with beta PAR parameter."""


    ### Start model with empty variables
    Dir = Director( t0=0.0, time_unit="", Vars={}, Modules={} )
    
    ### Start new plant  rhs
    Q_rhs_ins = Q_rhs()

    """
        #### Additional variables for testig
        Q_rhs_ins.AddVarLocal( typ='StatePartial', varid='X', prn=r'$C_t$',\
            desc="Thermic age of a fruit, auxiliar variable for testing", units= C * d, val=1.0)

        Q_rhs_ins.AddVarLocal( typ='StatePartial', varid='f_wg', prn=r'$f_{wg}$',\
            desc="Sink strength, auxiliar variable for testing", units= 1, val=1.0)
    """

    Dir.AddTimeUnit( Q_rhs_ins.GetTimeUnits())

    Dir.MergeVarsFromRHSs( Q_rhs_ins, call=__name__)

    ### Add an instance of Module 1:
    Dir.AddModule( "Plant", Plant( beta, Q_rhs_ins) )
    Dir.sch = [ "Plant" ]

    if return_Q_rhs_ins:
        return Dir, Q_rhs_ins
    else:
        return Dir


""" *************** Test run for this module only: ********** """

###### Test this Module
if __name__ == '__main__':
    
    Dir, Q_rhs_ins = PlantDirector( beta=0.1, return_Q_rhs_ins=True)
    
    Q_rhs_ins.AddVarLocal( typ='StatePartial', varid='X', prn=r'$C_t$',\
            desc="Thermic age of a fruit, auxiliar variable for testing", units= C * d, val=1.0)

    Q_rhs_ins.AddVarLocal( typ='StatePartial', varid='f_wg', prn=r'$f_{wg}$',\
            desc="Sink strength, auxiliar variable for testing", units= 1, val=1.0)

    ### Test RHS
    from sympy import exp #symbilic evaluations for testing units


    ### Test run RHSs:

    
    look_up_func_list = Q_rhs_ins.TU_look_up_func

    units1 = Q_rhs_ins.TestUnits( lhs='Q', assigm=True)
    
    Q_rhs_ins.GetFuncUnits(TF)
    Q_rhs_ins.GetFuncUnits(f)
    Q_rhs_ins.GetFuncUnits(Y_pot)


    X = linspace( 0, 500, num=100)
    Yp = [Y_pot( k2_TF=Q_rhs_ins.V('k2_TF'), C_t=Q_rhs_ins.V('C_t'), B=Q_rhs_ins.V('B'), D=Q_rhs_ins.V('D'), M=Q_rhs_ins.V('M'), X=x, T_mean=Q_rhs_ins.V('T_mean'))\
           for x in X]
    #plot( X, Yp, '-')

    ### Test expession interactively: DOES NOT WORK, exp not recognized
    #Q_rhs_ins.TU_IA()
    """
    del Dir
    del Q_rhs_ins
    
    from numpy import exp # Return to numeric evaluations
        
    Dir = PlantDirector( beta=0.1 )
    
    ### Test Module
    
    from pylab import plot
    for days in range(70):
        Dir.Scheduler( t1=days, sch=Dir.sch )
        for fr in range(Dir.Modules['Plant'].n_fruits):
            plot( days, Dir.Modules['Plant'].fruits[fr][1], 'bo')
        print( Dir.Modules['Plant'].n_fruits, Dir.V('Q'))
    print(Dir.V('Q_h'))
    """
