import const
import garbage_holder
import time

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


class AllocationInfo:
    def __init__(self, ArraySize, BucketIndex, GenerationIndex):
        self.ArraySize = ArraySize
        self.BucketIndex = BucketIndex
        self.GenerationIndex = GenerationIndex

def create_garbage():

def run_garbage_allocator(GarbageAllocator):
    allocations = GarbageAllocator.Allocations
    gh = GarbageAllocator.GarbageHolder
    gcPauses = GarbageAllocator.GCPauses
    allocationIndex = GarbageAllocator.StartIndex
    allocationIndexMask = len(allocations)- 1
    garbage_holder.Start(GarbageAllocator.GarbageHolder)

    lastTimestamp = time.time_ns()
    endTimestamp = lastTimestamp + GarbageAllocator.RunDuration.

