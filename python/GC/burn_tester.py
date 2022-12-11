import const
class GCTester:
    def __init__(self,
        NoOutput,
        Duration,
        MaxTime,
        MaxSize,
        StaticSetSize,
        Allocations,
        StartIndexes,
        StaticSet,
        StaticSetCount,
        Random,
        isInitialized 
         ):
        self.NoOutput = NoOutput
        self.Duration = Duration
        self.MaxTime = MaxTime
        self.MaxSize = MaxSize
        self.StaticSetSize = StaticSetSize
        self.Allocations = Allocations
        self.StartIndexes = StartIndexes
        self.StaticSet = StaticSet
        self.StaticSetCount = StaticSetCount
        self.Random = Random
        self.isInitialized = isInitialized

def NewGCTester (staticSetSize):
    return BurnTester(False, 
        DefaultDuration, 
        DefaultMaxTime, 
        DefaultMaxSize,
        staticSetSize,
        Allocations,
        StartIndexes,
        StaticSet,
        0,
        NewStdRandom(123)
          )