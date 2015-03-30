# test for array equality - in terms of elements - order doesn't matter
def arraysAreEqual(one, two):
    for item in one:
        if not item in two:
            print "item not in two:", item
            return False
        two.remove(item)
    print "left over: ", two
    return len(two) == 0

# return unique elements from list a
def unique(a):
    n = []
    for item in a:
        if not item in n:
            n.append(item)
    return n
