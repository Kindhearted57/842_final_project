import math
class Interval:
    def __init__(self, Start, End):
        self.Start = Start
        self.End = End

def IsEmpty(i):
    return (i.End - i.start ==0)

def UnionsWith(i,j):
    if i.Start <= j.Start and j.Start <= i.End:
        return True
    if j.Start <= i.Start and i.Start <= j.End:
        return True

    return False

def UnionExtend(i,j):
    return Interval(math.Min(i.Start, j.Start), math.Max(i.End, j.End))
def ToCanonicalSorted(IntervalList):
    last = IntervalList[0]
    result = []
    for i in IntervalList:
        if last.Start > i.Start and not IsEmpty(last) and not IsEmpty(i):
            raise RuntimeError("The sequence is expected to be sorted")
        if UnionsWith(last,i):
            last = last.UnionExtend(last, i)
        elif not IsEmpty(last):
            result.append(last)
            last = i
        
    if not IsEmpty(last):
        result.append(last)
    
    return result

def IntersectSortedPairs(a, b):
    result = []
    i = 0
    j = 0
    while(True):
        if i >= len(a) or j >= len(b):
            break
        intersection = a[i].Intersect(b[j])
        if not IsEmpty(intersection):
            result.append(intersection)
        if a[i].End < b[j].End:
            i = i + 1
        else:
            j = j + 1
    return result