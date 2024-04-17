
def acceptOnlyBetter(oldCost, newCost):
    return newCost < oldCost


def acceptAll(*_):
    return True


def acceptSameOrBetter(oldCost, newCost):
    return newCost <= oldCost


def acceptPrctWorst(oldCost, newCost, prct=0.1):
    return newCost <= oldCost or newCost < prct * oldCost + oldCost
