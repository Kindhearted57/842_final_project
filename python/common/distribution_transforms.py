import distribution
import math

#
def Truncate(x, min, max):
    return math.Max(min, math.Min(max, x))

def TruncateMin(x, min):
    return math.Max(x, min)
