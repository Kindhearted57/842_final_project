package speed_test

import (
	. "../common/nanotime"
	"time"
)

const StepSize = 50

type UnitAllocator struct {
	RunDuration time.Duration
	Last        *AllocationUnit
	// Statistics
	AllocationCount int64
	UnitSize        int64
}

type AllocationUnit struct {
	Field1 int64
	Field2 int64
}

func NewUnitAllocator(runDuration time.Duration, unitSize int64) *UnitAllocator {
	a := &UnitAllocator{
		RunDuration: runDuration,
		UnitSize:    unitSize,
	}
	return a
}

func (a *UnitAllocator) Run() {
	lastTimestamp := Nanotime().Nanoseconds()
	endTimestamp := lastTimestamp + a.RunDuration.Nanoseconds()
	last := &AllocationUnit{}

	for lastTimestamp < endTimestamp {
		for i := 0; i < StepSize; i++ {
			last = new(AllocationUnit) // Just to make sure there is a heap allocation
			// last = &AllocationUnit{} // This version runs with the same speed
		}
		a.AllocationCount += StepSize
		lastTimestamp = Nanotime().Nanoseconds()
	}
	a.Last = last // To suppress unused var error; changes nothing
}
