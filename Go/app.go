package main

import (
	bt "./burn_test"
	. "./common"
	st "./speed_test"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"runtime"
	"strings"
	"time"
)

type baselineResult struct {
	//in seconds
	Duration int64
	// static set size, GB
	UnitSize int64
	// Allocation Speed
	AllocationSpeed float64
}

// This function checks the file
func checkFile(filename string) error {
	_, err := os.Stat(filename)
	if os.IsNotExist(err) {
		_, err := os.Create(filename)
		if err != nil {
			return err
		}
	}
	// If the file exists, return nil
	return nil
}

func append_json_baseline(filename string, newStruct *baselineResult) {
	err := checkFile(filename)
	// Initialize the struct

	data := []baselineResult{}
	if err == nil {
		// if err == nil which means this file already exists
		// read out the content from the file
		fmt.Println(data)
		file, err := os.ReadFile(filename)
		if err == nil {
			json.Unmarshal(file, &data)
		}
	}

	data = append(data, *newStruct)
	// marshal and write again the data
	dataBytes, err := json.Marshal(data)
	err = os.WriteFile(filename, dataBytes, 0644)

}

func append_json_gc(filename string, newStruct *bt.GcResult) {
	err := checkFile(filename)
	// Initialize the struct

	data := []bt.GcResult{}
	if err == nil {
		// if err == nil which means this file already exists
		// read out the content from the file
		fmt.Println(data)
		file, err := os.ReadFile(filename)
		if err == nil {
			json.Unmarshal(file, &data)
		}
	}

	data = append(data, *newStruct)
	// marshal and write again the data
	dataBytes, err := json.Marshal(data)
	err = os.WriteFile(filename, dataBytes, 0644)

}

// https://dev.to/evilcel3ri/append-data-to-json-in-go-5gbj
// Deal with json file in Golang

func main() {
	ramSizeGb := GetRamSize()
	var durationSecFlag = flag.Int64("d", 10, "Test pass duration, seconds")
	var staticSetSizeGbFlag = flag.String("m", "", "Static set size, GB")
	var threadCountFlag = flag.String("t", "", "Number of threads to use")
	var maxSizeFlag = flag.String("o", "", "Max. object size")
	var testsFlag = flag.String("r", "", "Tests to run (a = raw allocation, b = burn)")
	var outputModeFlag = flag.String("p", "", "Output mode (f = full, m = minimal)")
	var _ = flag.String("l", "", "Latency mode (ignored for Go)")

	var outputtoFileFlag = flag.String("dir", "outputfile.json", "Specify the output file location")
	var UnitSizeFlag = flag.Int64("u", 16, "Unit Size (B)")
	flag.Parse()
	bt.DefaultDuration = time.Duration(*durationSecFlag * int64(time.Second))
	st.DefaultDuration = time.Duration(*durationSecFlag * int64(time.Second))
	bt.DefaultMaxSize = ParseRelative(*maxSizeFlag, bt.DefaultMaxSize, true)
	ThreadCount = int(ParseRelative(*threadCountFlag, float64(ThreadCount), true))
	tests := strings.ToLower(*testsFlag)
	staticSetSizeGb := 0
	if *staticSetSizeGbFlag != "" {
		tests += "b"
		staticSetSizeGb = int(ParseRelative(*staticSetSizeGbFlag, float64(ramSizeGb), true))
	}
	st.DefaultUnitSize = *UnitSizeFlag
	outputMode := strings.ToLower(*outputModeFlag)

	// By default it is full
	if outputMode == "" {
		outputMode = "f"
	}

	var outputAddr = *outputtoFileFlag

	if strings.Contains(outputMode, "f") {
		args := fmt.Sprintf("%+v", os.Args[1:])
		fmt.Printf("Launch parameters: %v\n", args[1:len(args)-1])
		fmt.Printf("Software:\n")
		fmt.Printf("  Runtime:         Go\n")
		fmt.Printf("    Version:       %v\n", runtime.Version())
		fmt.Printf("  OS:              %v %v\n", GetOSVersion(), runtime.GOARCH)
		fmt.Printf("Hardware:\n")
		fmt.Printf("  CPU:             %v\n", GetCpuModelName())
		coreCountAddon := ""
		if runtime.NumCPU() != ThreadCount {
			coreCountAddon = fmt.Sprintf(", %v used by test", ThreadCount)
		}
		fmt.Printf("  CPU core count:  %v%v\n", runtime.NumCPU(), coreCountAddon)
		fmt.Printf("  RAM size:        %v GB\n", ramSizeGb)
		fmt.Println()
	}

	runWarmup()

	if tests == "" {
		runSpeedTest()
		runBurnTest("--- Stateless server (no static set) ---", 0)
		runBurnTest("--- Worker / typical server (static set = 20% RAM) ---", int64(ramSizeGb)*GB/5)
		runBurnTest("--- Caching / compute server (static set = 50% RAM) ---", int64(ramSizeGb)*GB/2)
		return
	}

	if strings.Contains(tests, "a") {

		var result = runSpeedTest()
		// Construction the json here
		newStruct := &baselineResult{
			Duration: *durationSecFlag,
			// static set size, GB
			UnitSize: *UnitSizeFlag,
			// Allocation Speed
			AllocationSpeed: result,
		}
		append_json_baseline(outputAddr, newStruct)
	}
	if strings.Contains(tests, "b") {
		title := fmt.Sprintf("--- Static set = %v GB (%.2f %% RAM) ---",
			staticSetSizeGb,
			float64(staticSetSizeGb)*100/float64(ramSizeGb))
		var newStruct = runBurnTest(title, int64(staticSetSizeGb)*GB)
		append_json_gc(outputAddr, newStruct)
	}
}

func runWarmup() {
	speedTester := st.NewWarmupSpeedTester()
	speedTester.Run()
	burnTester := bt.NewWarmupBurnTester(10 * int64(MB))
	burnTester.Run()
}

func runSpeedTest() float64 {
	fmt.Println("--- Raw allocation (w/o holding what's allocated) ---")
	fmt.Println()
	speedTester := st.NewSpeedTester()
	var result = speedTester.Run()
	return result
}

func runBurnTest(title string, staticSetSize int64) *bt.GcResult {
	fmt.Println(title)
	fmt.Println()
	burnTester := bt.NewBurnTester(staticSetSize)
	var result = burnTester.Run()
	return result
}
