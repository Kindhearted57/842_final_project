import time

NanosecondsPerReleaseCycle = 1000
BucketCount = 10
BucketSize = 10

class GarbageHolder:
    def __init__(self, buckets, collected, startTime):
        # buckets -> [BucketCount][BucketSize]
        self.buckets = buckets
        self.collected = collected
        #int
        self.startTime = startTime

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

def TryReleaseGarbage():
    collectionIdx =             
def release(GarbageHolder, bucket, generationCount):
    while(generationCount !=0 and bucket < len(GarbageHolder.buckets)):
        remaining = generationCount = GarbageHolder.collected[bucket]
        GarbageHolder.collected[bucket] = generationCount
        if remaining >= BucketSize:
            remaining = BucketSize

        # 
            
        for i in range(remaining, BucketSize, 1):
             GarbageHolder.buckets[i - remaining] = GarbageHolder.buckets[i]
             for j in range(GarbageHolder.buckets[i]):
                GarbageHolder.buckets[i][j] = None
        bucket = bucket + 1
        generationCount /= BucketSize
