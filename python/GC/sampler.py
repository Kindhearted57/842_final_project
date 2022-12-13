import common.distribution as cd
def CreateStandardSizeSampler (rnd):
    dTypical = cd.NewNormalDistribution(rnd, 32 ,64)
    dLarge = Transform(cd.NewNormalDistribution(rnd, 11,1))
    dxLarge = Transform(cd.NewNormalDistribution(rnd, 16, 1))
    combined = cd.CombinedDistribution([0.99,0.0099,0.0001],
    cd.Distribution(dTypical, dLarge, dxLarge),
    rnd)

    return combined
    

def CreateStandardTimeSampler() :
    dMethod = ReflectNegatives(cd.NewNormalDistribution(rnd, 0, 0.1))
    dRequest = ReflectNegatives(cd.NewNormalmDistribution(rnd, 0, 1e5))
    dLongLiving = NewNormalDistribution(rnd, 1e7, 1e7)
    combined = cd.CombinedDistribution(
        [0.95, 0.049, 0.001]
        [dMethod, dRequest, dLongLiving],
        rnd
    )
    return TruncateMin(combined, 0)
