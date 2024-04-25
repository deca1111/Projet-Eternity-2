# Auteurs
# Armel Ngounou Tchawe - 2238017
# Léo Valette - 2307835


def acceptOnlyBetter(oldCost, newCost):
    return newCost < oldCost


def acceptAll(*_):
    return True


def acceptSameOrBetter(oldCost, newCost):
    return newCost <= oldCost


def acceptPrctWorst(oldCost, newCost, prct=0.1):
    return newCost <= oldCost or newCost < int(prct * oldCost) + oldCost
