import const
import GC.garbage_holder as gh
import time
import datetime 
import common.interval

class GarbageAllocator:
    def __init__(self, 
        RunDuration, 
        Allocations, 
        StartIndex, 
        GarbageHolder,
        AllocationCount,
        ByteCount,
        GCPauses,
        EndTimestamp):
        self.RunDuration = RunDuration
        self.Allocations = Allocations
        self.StartIndex = StartIndex
        self.GarbageHolder = GarbageHolder
        self.AllocationCount = AllocationCount
        self.ByteCount = ByteCount
        self.GCPauses = GCPauses
        self.EndTimestamp = EndTimestamp

# Since some parameters are fixed and others 

def NewGabageAllocator(runDuration, allocations, startIndex):
    return GarbageAllocator(runDuration, 
    allocations, 
    startIndex, 

    gh.GarbageHolder())

class AllocationInfo:
    def __init__(self,
    ArraySize,
    BucketIndex,
    Generation):
        self.ArraySize = ArraySize
        self.BucketIndex = BucketIndex
        self.Generation = Generation



class AllocationInfo:
    def __init__(self, ArraySize, BucketIndex, GenerationIndex):
        self.ArraySize = ArraySize
        self.BucketIndex = BucketIndex
        self.GenerationIndex = GenerationIndex

def create_garbage(arraySize):
    # Here we return an array of size arraySize
    return [0]*arraySize
def run_garbage_allocator(GarbageAllocator):
    allocations = GarbageAllocator.Allocations
    gh = GarbageAllocator.GarbageHolder
    gcPauses = GarbageAllocator.GCPauses
    allocationIndex = GarbageAllocator.StartIndex
    allocationIndexMask = len(allocations)- 1
    gh.Start(GarbageAllocator.GarbageHolder)

    lastTimestamp = time.time_ns()
    endTimestamp = lastTimestamp + GarbageAllocator.RunDuration
    while(lastTimestamp < endTimestamp):
        allocation_index = allocations[allocationIndex]
        allocationIndex = (allocationIndex+1) & allocationIndexMask

        # Allocation
        garbage = gh.CreateGarbage(allocation_index.ArraySize)
        gh.AddGarbage(garbage, allocation_index.BucketIndex, allocation_index.GenerationIndex)
        GarbageAllocator.AllocationCount = GarbageAllocator.AllocationCount +1
        GarbageAllocator.ByteCount = GarbageAllocator.ByteCount

        # Release %15 content
        if(allocationIndex % 15) == 10:
            gh.TryReleaseGarbage()

        # GC check
        # This elapsed time should be in nanoseconds
        elapsed = time.time()
        diff = elapsed - lastTimestamp
        if diff >= const.MinGCPause:
            GCPauses = gcPauses.append(common.interval.Interval(lastTimestamp,elapsed))
        lastTimestamp = elapsed
    
    GarbageAllocator.EndTimestamp = datetime.datetime.now()
    GarbageAllocator.GCPauses = GCPauses

def ByteSizeToArraySize(byteSize):
    s = (byteSize - const.MinAllocationSize+const.ArrayItemSize - 1) /const.ArrayItemSize
    if s < 0:
        return 0
    return s

def ArraySizeToByteSize(arraySize):
    return const.MinAllocationSize + arraySize << const.ArrayItemSizeLog2