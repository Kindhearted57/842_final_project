import const
import threading
import const
import garbage_allocator
import set_allocator
import random
import baseline_test
import sampler
import datetime 
import common.distribution_transforms as cd
import gc
import time
import interval 
import math

results = [None]*const.Threadcount
NanosecondsPerReleaseCycle = 1000
TimeSamplerFrequency = 1000000
AllocationSequenceLength = 2**20

NanoToMilliseconds = 1000/ 1e9
NanoToseconds = 1 / 1e9

# Result container
class GcResult:
    def __init__(self,
    Duration,
    staticSetSize,
    AllocationSpeed,
    ThreadCount,
    MaxSize,
    MaxTime,
    OperationPerSecond,
    RAMUseBefore,
    RAMUseAfter,
    GCrate,
    globalPauses):
    self.Duration = Duration
    self.staticSetSize = staticSetSize
    self.AllocationSpeed = AllocationSpeed
    self.ThreadCount = ThreadCount
    self.MaxSize = MaxSize
    self.MaxTime = MaxTime
    self.OperationPerSecond = OperationPerSecond
    self.RAMUseBefore = RAMUseBefore
    self.RAMUseAfter = RAMUseAfter
    self.GCrate = GCrate
    self.globalPauses = globalPauses

class BurnTester:
    def __init__(self,
        # flag to signal whether to give output or not
        NoOutput,
        #
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


# In this thread we create GarbageAllocator
def _AllocatorThread(tester,index, startOffset):
     global results
     results[index] = set_allocator.NewSetAllocator((tester.StaticSetSIze)/const.Threadcount, 
     tester.Allocations, 
     (startOffset + tester.StartIndexes[index])%const.AllocationSequenceLength)
    
def _GarbageAllocatorThread(tester, index, ):
    results[index] = garbage_allocator.NewGabageAllocator(tester.Duration, tester.Allocations, tester.StartIndexes[index])

def NewGCTester (staticSetSize):
    return BurnTester(False, 
        const.DefaultDuration, 
        const.DefaultMaxTime, 
        const.DefaultMaxSize,
        staticSetSize,
        [garbage_allocator.AllocationInfo]*AllocationSequenceLength,
        # This actually should be int32 but i guess it is fine to do this for now since it is python..
        []*AllocationSequenceLength,
        [[[]]],
        0,
        random.NewStdRandom(123),
        False )

def NewWarmupGCTester (staticSetSize):
    t = NewGCTester(staticSetSize)
    t.NoOutput = True
    t.Duration = datetime.timedelta(second =1)


def TryInitialize(BurnTester):
    if BurnTester.isinitialized:
        return
    sizeSampler = sampler.CreateStandardSizeSampler(BurnTester.Random)
    
    timeSampler = sampler.CreateStandardTimeSampler(BurnTester.Random)
    releaseCycleTimeInSeconds = 1e-6
    timeFactor = 1 / TimeSamplerFrequency / releaseCycleTimeInSeconds
    for i in range(AllocationSequenceLength):
        size = cd.truncate(cd.truncateMin((sizeSampler.Sample(),0)),1,BurnTester.MaxSize)
        arraySize = ByteSizeToArraySize(size)
        _time = cd.truncate(cd.truncateMin((timeSampler.Sample(),0)),0,BurnTester.MaxSize)
        _timeStr = str(int(_time*timeFactor))
        bucketIndex = int(len(_timeStr) -1 )
        generationIndex = int(_timeStr[0]-'0')

        BurnTester.Allocations[i] = garbage_allocator.AllocationInfo(arraySize, bucketIndex, generationIndex)

    # Remember to deal with the thread information here
    for i in range(const.Threadcount):
        BurnTester.StartIndexes[i] = random.Next(BurnTester.Random) % AllocationSequenceLength
    
    startOffset = random.Next(BurnTester.Random) % AllocationSequenceLength

    
    # start the multithreading here
    threads = [
            threading.Thread(target=_AllocatorThread, args=(BurnTester, i, startOffset ),daemon=True)
            for i in range(const.Threadcount)
            ]
    for t in threads:
        t.start()

    for a in results:
        allocator = a.SetAllocator
        BurnTester.StaticSet.append(allocator.Set)
        BurnTester.StaticSetCount = BurnTester.StaticSetCount + len(allocator.Set)
    
    # Force to do a gc here
    gc.collect()
    BurnTester.isInitialized = True

def run_gc_tester(BurnTester):
    TryInitialize(BurnTester)
    
    # Normalize GCPause 
    allocators = []

    #
    for a in results:
        allocators.append(a.GarbageAllocator)
    
    for a in range(allocators):
        d = a.EndTimestamp- startTime
        if duration < d:
            duration = d
        
        for j in range(a.GCPauses):
            
    #
    threads = [
        threading.Thread(target=_GarbageAllocatorThread, args=(tester, i),daemon=True)
        for i in range(const.Treadcount)
        ]
    startTime = time.time()
    for t in threads:
        t.start()
    
    pauses = []
    duration = 0
    for a in results:

        d = (a.EndTimestamp-startTime) * NanoToseconds
        if duration < d:
            duration = d
        
        for j in range(a.GCPauses):
            a.GCPauses[j].Start = (a.GCPauses[j].Start - startTime) * NanoToMilliseconds
            a.GCPauses[j].End = (a.GCPauses[j].End - startTime - 0.5) * NanoToMilliseconds

        a.GCPauses = interval.ToCanonicalSorted(a.GCPauses)
        pauses.append(a.GCPauses)
    
    intersections = pauses[0]
    for p in pauses:
        intersections = interval.IntersectSortedPairs(intersections, p)
    
    globalPauses = []
    globalPausesSum = 0
    for p in intersections:
        globalPauses.append(p.End - p.Start)
        globalPausesSum = globalPausesSum + (p.End - p.Start)

    allocationSizes = []
    allocationHoldDuration = []
    for a in allocators:
        for ai in a.allocations:
            t = math.Pow(10, ai.BucketIndex)*ai.GenerationIndex * NanosecondsPerReleaseCycle * NanoToMilliseconds
            allocationHoldDuration.append(t)
            allocationSizes.append(garbage_allocator.ArraySizeToByteSize(ai.ArraySize))
    
    ops = 0
    bytes = 0
    for a in allocators:
        ops = a.AllocationCount + ops
        bytes = a.AllocationCOunt + ops
    # TODO: I cannot find an efficient way to find out the 