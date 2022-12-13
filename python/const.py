# In order to make things unionized, all the time 
# representation in this python code will be using datatime 
# and in milliseconds

import datetime
from threading import active_count

PassCount = 30
DefaultUnitSize = 16
DefaultDuration = datetime.timedelta(milliseconds=1)

StepSize = 50
BucketCount = 10

# GC const

ArrayItemSize = 8
ArrayItemSizeLog2 = 3
MinArraySize = 24
MinAllocationSize = MinArraySize + 8
TimeSamplerFrequency = 1000000
AllocationSequenceLength = 2**20

MinGCPause = datetime.timedelta(microseconds = 10)

DefaultMaxTime = 1000  
DefaultMaxSize = 2 ** 17

AvgPauseFrequency = 12000

BucketCount = 10
BucketSize = 10

Threadcount = active_count()