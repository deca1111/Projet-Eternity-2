
def acceptOnlyBetter(oldCost, newCost):
    return newCost < oldCost


def acceptAll(*_):
    return True


def acceptSameOrBetter(oldCost, newCost):
    return newCost <= oldCost