package speed_test

import (
	. "../common"
	"fmt"
	"time"
)

const PassCount = 100

var DefaultDuration = time.Duration(time.Millisecond)
var DefaultUnitSize int64 = 16

type SpeedTester struct {
	NoOutput        bool
	Duration        time.Duration
	AllocationCount int64
	UnitSize        int64
}

func NewSpeedTester() *SpeedTester {
	t := &SpeedTester{
		NoOutput: false,
		Duration: DefaultDuration,
		UnitSize: DefaultUnitSize,
	}
	return t
}

func NewWarmupSpeedTester() *SpeedTester {
	t := NewSpeedTester()
	t.NoOutput = true
	t.Duration = time.Duration(5 * time.Millisecond)
	return t
}

func (t *SpeedTester) Run() float64 {
	duration := t.Duration.Seconds()
	if !t.NoOutput {
		fmt.Printf("Test settings:\n")
		fmt.Printf("  Duration:     %v ms\n", int64(t.Duration.Seconds()/Milli))
		fmt.Printf("  Thread count: %v\n", ThreadCount)
		fmt.Printf("  Unit size:    %v B\n", t.UnitSize)
		fmt.Println()
	}

	totalCount := int64(0)
	for pass := 0; pass < PassCount; pass++ {
		runner := NewParallelRunner(func(i int) IActivity { return NewUnitAllocator(t.Duration, t.UnitSize) })

		// runner.Run here will run the Run function in unit_allocator
		// in this function:

		// Within the given duration, allocate as StepSize * AllocationUnit as many times as possible

		activities := runner.Run()

		// Count the total number of allocationCount calculated by adding up the allocationcount in each thread
		allocators := make([]*UnitAllocator, 0)
		for _, a := range activities {
			allocators = append(allocators, a.(*UnitAllocator))
		}

		tc := int64(0)
		for _, a := range allocators {
			tc += a.AllocationCount
		}
		if totalCount < tc {
			totalCount = tc
		}
	}

	fmt.Printf("Allocation speed:\n")
	fmt.Printf("  Operations per second: %.3f M/s\n", float64(totalCount)/duration/Mega)
	//fmt.Printf("  Bytes per second:      %.3f GB/s\n", float64(totalCount * UnitSize)/duration/GB)
	fmt.Println()
	return float64(totalCount) / duration / Mega
}
