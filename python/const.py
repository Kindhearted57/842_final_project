import datetime


PassCount = 30
UnitSize = 16
DefaultDuration = datetime.timedelta(milliseconds=1)
StepSize = 50


# GC const

ArrayItemSize = 8
ArrayItemSizeLog2 = 3
MinArraySize = 24
MinAllocationSize = MinArraySize + 8
TimeSamplerFrequency = 1000000
AllocationSequenceLength = 2**20

MinGCPause = datetime.timedelta(microseconds = 10)
DefaultDuration = datetime.timedelta(seconds = 10)
DefaultMaxTime = 1000  
DefaultMaxSize = 2 ** 17

AvgPauseFrequency = 12000