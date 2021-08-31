"""
Author: David Bianchi

A file to define all of the reactions in the Lipid Module
"""

import numpy as np
import pandas as pd
from collections import defaultdict, OrderedDict

import odecell

from in_out import calcCellVolume
import defMetRxns as defLipCentNucTransMetRxns
import lipid_patch as lipid_patch
import PPP_patch as ppp_patch

### Constants
NA = 6.022e23 # Avogadro's
r_cell = 200e-9 # 200 nm radius, 400 nm diameter
V = ((4/3)*np.pi*(r_cell)**3)*(1000) # for a spherical cell

countToMiliMol = 1000/(NA*V)

def partTomM(particles,pmap):
    """
    Convert particle counts to mM concentrations for the ODE Solver

    Parameters:
    particles (int): The number of particles for a given chemical species

    Returns:
    conc (float): The concentration of the chemical species in mM
    """

    ### Constants
    NA = 6.022e23 # Avogadro's
    r_cell = 200e-9 # 200 nm radius, 400 nm diameter
    V = ((4/3)*np.pi*(r_cell)**3)*(1000) # for a spherical cell
    
    cellVolume = calcCellVolume(pmap)

    conc = (particles*1000.0)/(NA*cellVolume)

    return conc


def reptModel(model):
    """
    Report on the constructed hybrid model - but probably would only want to do after the first time step

    Arguments: 
    model (model obj.): The ODE Kinetic Model

    Returns:

    None
    """

    dictTypes = defaultdict(int)
    typeList = ["Transcription","Translation","Degradation"]

    for rxn in model.getRxnList():
        
        if rxn.getResult():
            # If an explicit result has been set, this is a dependent reaction.
            dictTypes["Dependent reactions"] += 1
            continue
        
        for rxntype in typeList:
            if rxntype in rxn.getID():
                dictTypes[rxntype] += 1

                
    #print( "There are {} ODEs in the model:".format(len(model.getRxnList())) )

    outList = list(dictTypes.items())
    outList.sort(key=lambda x: x[1], reverse=True)
    for key,val in outList:
        print("{:>20} :   {}".format(key,val) )
        return 0
    
    return


# Rather than using the rate forms in the SBML for the metabolism, this allows us to
# use forward and reverse kcats rather than the geometric mean form.

def Enzymatic(subs,prods):
        
    def numerator(subs,prods):
        
        subterm = [ '( $Sub' + str(i) + ' / $KmSub' + str(i) + ' )' for i in range(1,subs+1)]
        subNumer = ' * '.join(subterm)
        
        prodterm = [ '( $Prod' + str(i) + ' / $KmProd' + str(i) + ' )' for i in range(1,prods+1)]
        prodNumer = ' * '.join(prodterm)
        
        numerator = '( ' + '$kcatF * ' + subNumer + ' - ' + '$kcatR * ' + prodNumer + ' )'
        return numerator
    
    def denominator(subs,prods):
        
        subterm = [ '( 1 + $Sub' + str(i) + ' / $KmSub' + str(i) + ' )' for i in range(1,subs+1)]
        subDenom = ' * '.join(subterm)
        
        prodterm = [ '( 1 + $Prod' + str(i) + ' / $KmProd' + str(i) + ' )' for i in range(1,prods+1)]
        prodDenom = ' * '.join(prodterm)
        
        denominator = '( ' + subDenom + ' + ' + prodDenom + ' - 1 )'
        return denominator
        
    rate = '$onoff * $Enzyme * ( ' + numerator(subs,prods) + ' / ' + denominator(subs,prods) + ' )'
    
    return rate


def defineRxns(model,pmap):
    """
    Define all of the reactions and rateforms needed for the current module to an existing module.

    """

    ### Add Metabolic Reactions and specific parameter patches
    defLipCentNucTransMetRxns.addReactionsToModel(model,pmap)
    lipid_patch.main(model,pmap)
    ppp_patch.main(model,pmap)
    print("Reactions defined")

    ### Report on the model reactions added
    reptModel(model)

    return model

#def main():
    #__init__
