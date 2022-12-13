import GC.garbage_allocator as gg
import const 

class SetAllocator:
    def __init__(self, MaxSetSize, Allocations, StartIndex, Set):
        self.MaxSetSize = MaxSetSize
        self.Allocations = Allocations
        self.StartIndex = StartIndex
        self.Set = Set
def NewSetAllocator(maxSize, allocations, startIndex):
    return SetAllocator(maxSize, allocations, startIndex)
def run_set_allocator(SetAllocator):
    maxSetSize = SetAllocator.MaxSetSize
    result = [[]]
    index = SetAllocator.StartIndex
    currentSize = 0
    while currentSize < maxSetSize:
        arraySize = SetAllocator.Allocations[index].ArraySize
        result = result.append(gg.create_garbage(arraySize))
        currentSize = currentSize + gg.ArraySizeToByteSize(arraySize)
        index = (index+ 1)% const.AllocationSequenceLength
    SetAllocator.Set = result
