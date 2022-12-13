import random
import math
# single distribution
class Distribution:
    def __init__ (self, sample):
        self.sample = Sample()
    

class NormalDistribution:
    def __init__ (self, mean, stddev, rnd):
        self.mean = mean
        self.stddev = stddev
        self.rnd = rnd
    def Sample(self):
        (x,y,ok) = polarTransform(random.Next(self.rnd), random.Next(self.rnd))


class CombinedDistribution:
    def __init__ (self, weights, distributions, Rnd):
        # Here weights is a float64 list
        self.weights = weights
        # Here distributions is a Distribution list
        self.distributions = distributions
        self.Rnd = Rnd
    def Sample(self):
        expectedWeight = random.Next(self.Rnd)
        idx = 0
        weight = self.weights[0]
        while expectedWeight >= weight:
            idx = idx + 1
            weight = weight + self.weights[idx]
        
        if idx >= len(self.distributions):
            idx = len(self.distributions) - 1
        return Sample(self.distributions[idx])





def NewNormalDistribution(mean, stddev, r):
    return(NormalDistribution(mean, stddev, r))
# The parameter c here represents the 
def Sample(c):
    expectedWeight = c.Rnd
    idx = 0
    weight = c.Weights[0]
    while (expectedWeight >= weight):
        idx = idx +1
        weight = weight + c.Weights[idx]
    

    if idx >= len(c.Distributions):
        idx = len(c.Distributions) -1
    
    return c.Distributions[idx].Sample()
    

def polarTransform(x01, y01):
    xn11 = 2*x01 - 1
    yn11 = 2*y01 - 1  
    r2 = xn11*xn11 + yn11*yn11

    # Means this is not solvable
    if r2 >= 1 or r2 == 0:
        return (0, 0, False)
    
    factor = math.Sqrt(-2*math.Log(r2)/r2)
    x = xn11 * factor
    y = yn11 * factor 
    return (x, y, True)