import time
import const
NanosecondsPerReleaseCycle = 1000
import datetime

class GarbageHolder:
    def __init__(self, buckets, collected, startTime):
        # buckets -> [BucketCount][BucketSize]
        self.buckets = buckets
        self.collected = collected
        #int
        self.startTime = startTime

def NewGarbageHolder():
    return GarbageHolder([ [None]*const.BucketCount for i in range(const.BucketSize)],
    [None]*const.BucketCount,time.time())
def Reset(GarbageHolder):
    for i in range(GarbageHolder.buckets):
        for j in range(GarbageHolder.buckets[i]):
            GarbageHolder.buckets[i][j] = None

def Start(GarbageHolder):

    # set start time to be the current timestamp in nanoseconds
    GarbageHolder.startTime = time.time_ns()         
    # set the bucketsize to 0
    for i in range(GarbageHolder.collected):
        GarbageHolder.collected[i] = 0

def AddGarbage(GarbageHolder,garbage, bucket, generation):
    # garbage here is a int64 value
    if bucket == 0 and generation == 0:
        GarbageHolder.buckets[bucket][generation] = GarbageHolder.buckets[bucket][generation] + garbage

def TryReleaseGarbage(GarbageHolder):
    collectionIdx = (datetime.timedelta(nanoseconds=1) - GarbageHolder.startTime)/NanosecondsPerReleaseCycle  
def release(GarbageHolder, bucket, generationCount):
    while(generationCount !=0 and bucket < len(GarbageHolder.buckets)):
        remaining = generationCount = GarbageHolder.collected[bucket]
        GarbageHolder.collected[bucket] = generationCount
        if remaining >= const.BucketSize:
            remaining = const.BucketSize

        # 
            
        for i in range(remaining, const.BucketSize, 1):
             GarbageHolder.buckets[i - remaining] = GarbageHolder.buckets[i]
             for j in range(GarbageHolder.buckets[i]):
                GarbageHolder.buckets[i][j] = None
        bucket = bucket + 1
        generationCount /= const.BucketSize

