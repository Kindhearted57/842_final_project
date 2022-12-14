package burn_test

import (
	. "../common"
	. "../common/nanotime"
	"fmt"
	"math"
	"runtime"
	"strconv"
	"time"
)

const ArrayItemSize = 8
const ArrayItemSizeLog2 = 3

var MinArraySize = int32(24)
var MinAllocationSize = int32(MinArraySize + 8)

const TimeSamplerFrequency = 1000000
const AllocationSequenceLength = 1 << 20 // 2^20, i.e. ~ 1M items; must be a power of 2!

var MinGCPause = time.Duration(10 * time.Microsecond).Nanoseconds()
var DefaultDuration = time.Duration(10 * time.Second)
var DefaultMaxTime = float64(1000) * TimeSamplerFrequency // 1000 seconds
var DefaultMaxSize = float64(1 << 17)                     // 128KB
var releaseCycleTimeInSeconds = NanosecondsPerReleaseCycle * Nano
var TimeFactorFactor = float64(1)
var TimeFactor = ((1.0 / TimeSamplerFrequency) / releaseCycleTimeInSeconds) * TimeFactorFactor

type GcResult struct {
	//in seconds
	Duration float64
	// static set size, GB
	staticSetSize float64
	// Allocation Speed, operation per second
	AllocationSpeed float64
	// Thread Count
	ThreadCount int
	//Maxsize
	MaxSize int32
	MaxTime float64
	// Operationpersecond
	OperationperSecond float64
	// RAM used
	RAMUseBefore float64
	RAMUseAfter  float64
	GCrate       float64
	globalPauses float64
}
type BurnTester struct {
	NoOutput       bool
	Duration       time.Duration
	MaxTime        float64
	MaxSize        float64
	StaticSetSize  int64
	Allocations    []AllocationInfo
	StartIndexes   []int32
	StaticSet      [][][]int64
	StaticSetCount int64
	Random         *StdRandom
	isInitialized  bool
}

func NewBurnTester(staticSetSize int64) *BurnTester {
	t := &BurnTester{
		NoOutput:       false,
		Duration:       DefaultDuration,
		MaxTime:        DefaultMaxTime,
		MaxSize:        DefaultMaxSize,
		StaticSetSize:  staticSetSize,
		Allocations:    make([]AllocationInfo, AllocationSequenceLength),
		StartIndexes:   make([]int32, AllocationSequenceLength),
		StaticSet:      make([][][]int64, 0),
		StaticSetCount: 0,
		Random:         NewStdRandom(123),
	}
	return t
}

func NewWarmupBurnTester(staticSetSize int64) *BurnTester {
	t := NewBurnTester(staticSetSize)
	t.NoOutput = true
	t.Duration = time.Duration(1 * time.Second)
	return t
}

func (t *BurnTester) TryInitialize() float64 {
	if t.isInitialized {
		return 0
	}
	// sizeSampler is a transformeddistribution
	//transformedDistribution.sample ->

	// Truncate ->
	// TransformedDistribution(
	// createstandardsizesampler_result,
	// func(x float64) float64 {return math.Max(min, math.Min(max, x))}
	//)

	// I guess this will work as a recursion

	// Therefore it will first do max()

	// The return value of CreateStandardSizeSampler
	// TruncateMin(combinedDistribution,
	// func(x float64) float64 {return math.Max(x. 0)})
	sizeSampler := Truncate(CreateStandardSizeSampler(t.Random), 1, t.MaxSize)
	timeSampler := Truncate(CreateStandardTimeSampler(t.Random), 0, t.MaxTime)

	for i := 0; i < AllocationSequenceLength; i++ {
		// math.Max(min, math.Min(max, createstandardsizesampler.sample()))
		size := int32(sizeSampler.Sample())

		arraySize := ByteSizeToArraySize(size)
		// TransformedDistribution.sample -> t.transform(t.d.sample())
		_time := timeSampler.Sample()
		//Itoa int to string
		_timeStr := strconv.Itoa(int(_time * TimeFactor))
		bucketIndex := int8(len(_timeStr) - 1)
		generationIndex := int8(_timeStr[0] - '0')

		t.Allocations[i] = AllocationInfo{arraySize, bucketIndex, generationIndex}
	}

	for i := 0; i < ThreadCount; i++ {
		t.StartIndexes[i] = int32(t.Random.Next()) % AllocationSequenceLength
	}

	startOffset := int32(t.Random.Next()) % AllocationSequenceLength
	runner := NewParallelRunner(func(i int) IActivity {
		return NewSetAllocator(
			t.StaticSetSize/int64(ThreadCount),
			t.Allocations,
			(startOffset+t.StartIndexes[i])%AllocationSequenceLength)
	})

	// Set allocator here is used to allocate static set

	activities := runner.Run()
	for _, a := range activities {
		allocator := a.(*SetAllocator)
		t.StaticSet = append(t.StaticSet, allocator.Set)
		t.StaticSetCount += int64(len(allocator.Set))
	}

	runtime.GC()

	t.isInitialized = true
	return TimeFactor
}

func (t *BurnTester) Run() *GcResult {
	var timefactor = t.TryInitialize()
	// In this try initialize process, allocation[] is filled with the randomization result

	// This variable here does not work
	testDuration := t.Duration.Seconds()
	if !t.NoOutput {
		fmt.Printf("Test settings:\n")
		fmt.Printf("  Duration:          %v s\n", int(testDuration))
		fmt.Printf("  Thread count:      %v\n", ThreadCount)
		fmt.Printf("  Static set:\n")
		fmt.Printf("    Total size:      %.3f GB\n", float64(t.StaticSetSize)/GB)
		fmt.Printf("    Object count:    %.3f M\n", float64(t.StaticSetCount)/Mega)
		fmt.Println()
	}

	runner := NewParallelRunner(func(i int) IActivity { return NewGarbageAllocator(t.Duration, t.Allocations, t.StartIndexes[i]) })

	msPre := new(runtime.MemStats)
	runtime.ReadMemStats(msPre)
	startTime := float64(Nanotime().Nanoseconds())
	activities := runner.Run()
	msPost := new(runtime.MemStats)
	runtime.ReadMemStats(msPost)

	// Slice item casting
	allocators := make([]*GarbageAllocator, 0)
	for _, a := range activities {
		allocators = append(allocators, a.(*GarbageAllocator))
	}

	const NanoToMilliseconds = 1000 / Giga // ns to ms
	const NanoToSeconds = 1 / Giga         // ns to ms

	// Normalizing GCPauses; nanoseconds to milliseconds and a bit more
	var pauses [][]Interval
	var duration float64
	for _, a := range allocators {
		d := (float64(a.EndTimestamp) - startTime) * NanoToSeconds
		if duration < d {
			duration = d
		}
		for j := range a.GCPauses {
			a.GCPauses[j].Start = (a.GCPauses[j].Start - startTime) * NanoToMilliseconds
			a.GCPauses[j].End = (a.GCPauses[j].End - startTime - 0.5) * NanoToMilliseconds
		}
		a.GCPauses = ToCanonicalSorted(a.GCPauses)
		pauses = append(pauses, a.GCPauses)
	}
	var intersections = pauses[0]
	for _, p := range pauses {
		intersections = IntersectSortedPairs(intersections, p)
	}
	var globalPauses []float64
	var globalPausesSum float64
	for _, p := range intersections {
		globalPauses = append(globalPauses, p.End-p.Start)
		globalPausesSum += p.End - p.Start
	}
	var allocationSizes []float64
	var allocationHoldDurations []float64
	for _, a := range allocators {
		for _, ai := range a.Allocations {
			t := math.Pow(10, float64(ai.BucketIndex)) * float64(ai.GenerationIndex) * NanosecondsPerReleaseCycle * NanoToMilliseconds
			allocationHoldDurations = append(allocationHoldDurations, t)
			allocationSizes = append(allocationSizes, float64(ArraySizeToByteSize(ai.ArraySize)))
		}
	}

	fmt.Printf("Actual duration:         %.3f s\n", duration)
	fmt.Printf("Allocation speed:\n")
	var ops, bytes int64
	for _, a := range allocators {
		ops += a.AllocationCount
		bytes += a.ByteCount
	}
	fmt.Printf("  Operations per second: %.2f M/s\n", float64(ops)/duration/Mega)
	fmt.Printf("  Bytes per second:      %.2f GB/s\n", float64(bytes)/duration/GB)
	fmt.Printf("  Allocation stats:\n")
	fmt.Printf("    Size:\n")
	DumpArrayStats(allocationSizes, "B", "      ", true)
	fmt.Printf("    Hold duration:\n")
	DumpArrayStats(allocationHoldDurations, "ms", "      ", true)
	fmt.Println()
	fmt.Printf("GC stats:\n")
	fmt.Printf("  RAM used:              %.3f -> %.3f GB\n", float64(msPre.HeapAlloc)/GB, float64(msPost.HeapAlloc)/GB)
	fmt.Printf("  GC rate:               %.3f /s\n", float64(msPost.NumGC-msPre.NumGC)/duration)
	fmt.Printf("  Allocation rate:\n")
	fmt.Printf("    Objects:             %.3f M/s, %.3f M/s freed\n",
		float64(msPost.Mallocs-msPre.Mallocs)/duration/Mega,
		float64(msPost.Frees-msPre.Frees)/duration/Mega)
	fmt.Printf("    Bytes:               %.3f GB/s\n", float64(msPost.TotalAlloc-msPre.TotalAlloc)/duration/GB)
	fmt.Printf("  Global pauses:\n")
	fmt.Printf("    %% of time frozen:    %.3f %%, %.3f %% as reported by runtime\n",
		globalPausesSum/1000/duration*100,
		float64(msPost.PauseTotalNs-msPre.PauseTotalNs)/Giga/duration*100)
	fmt.Printf("    # per second:        %.3f /s\n", float64(len(globalPauses))/duration)
	fmt.Printf("    Pause duration:\n")
	DumpArrayStats(globalPauses, "ms", "      ", true)
	fmt.Println()

	var staticsetsize = t.StaticSetSize
	return &GcResult{
		Duration:           duration,
		staticSetSize:      float64(staticsetsize) / GB,
		AllocationSpeed:    float64(msPost.Mallocs-msPre.Mallocs) / duration / Mega,
		ThreadCount:        ThreadCount,
		MaxSize:            MinArraySize,
		MaxTime:            timefactor,
		OperationperSecond: float64(ops) / duration / Mega,
		RAMUseBefore:       float64(msPre.HeapAlloc) / GB,
		RAMUseAfter:        float64(msPost.HeapAlloc) / GB,
		GCrate:             float64(msPost.NumGC-msPre.NumGC) / duration,
		globalPauses:       globalPausesSum / 1000 / duration * 100,
	}
}
