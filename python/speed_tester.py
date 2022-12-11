import datetime
import threading
import const
import baseline_test
import time


results = [None]*const.PassCount

class SpeedTester:
    def __init__(self, NoOutput, Duration, AllocationCount):
        self.NoOutput = NoOutput
        self.Duration = Duration
        self.AllocationCount = AllocationCount

def NewSpeedTester():
    return SpeedTester(False, const.DefaultDuration, 0 )

def NewWarmupSpeedTester():
    tester = NewSpeedTester()
    tester.NoOutput = True
    tester.Duration = 5 * const.DefaultDuration
    return tester

def _AllocatorThread(tester,index):
     global results
     results[index] = baseline_test.run_baseline(baseline_test.NewUnitAllocator(tester.Duration))
def run_speed_tester (tester):
    duration = tester.Duration.total_seconds()
    if not tester.NoOutput:
        print("Test settings: \n")
        print("Duration {duration} s \n".format(duration=duration))
        print("Thread Count {thread_count} \n".format(thread_count=threading.active_count()))
        print("Unit Size {} \n")
    totalCount = 0
    
    
    for pass_num in range(const.PassCount):
        threads = [
                threading.Thread(target=_AllocatorThread, args=(tester, pass_num),daemon=True)
                for i in range(const.PassCount)
                ]
        for t in threads:
            t.start()
    
    tc = 0
    
    for allocator in results:
        tc += allocator.AllocationCount

    if totalCount < tc:
        totalCount = tc


    if not tester.NoOutput:
        print("Allocation speed \n")
        print("Operation per second {operation_num}".format(operation_num = totalCount/duration/10**6))
    
    return totalCount/duration/10**6
