import time 
import const

class UnitAllocator:
    def __init__(self, RunDuration, Last, AllocationCount):
        self.RunDuration = RunDuration
        self.Last = Last
        self.AllocationCount = AllocationCount

class AllocationUnit:
    def __init__(self, Field1, Field2):
        self.Field1 = Field1
        self.Field2 = Field2

def NewAllocationUnit():
    return AllocationUnit(1, 1)
def NewUnitAllocator(runDuration):
    return UnitAllocator(runDuration, NewAllocationUnit, 1)

def run_baseline (UnitAllocator):
    lastTimeStamp = time.time_ns()
    endTimeStamp = lastTimeStamp + UnitAllocator.RunDuration.microseconds
    last = AllocationUnit(1,1)
    while lastTimeStamp < endTimeStamp:
        for i in range(const.StepSize):
            last = AllocationUnit(1,1)
        UnitAllocator.AllocationCount += const.StepSize
        lastTimeStamp = time.time_ns()
    UnitAllocator.Last = last
    return UnitAllocator
    
