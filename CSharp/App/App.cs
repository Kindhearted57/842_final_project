using System;
using System.CodeDom.Compiler;
using System.Linq;
using System.Runtime;
using System.Runtime.InteropServices;
using CommandLine;
using Benchmarking.Common;
using GCBurn.BurnTest;
using GCBurn.SpeedTest;

using System.Text.Json;
using System.Text.Json.Serialization;
using System.IO;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace GCBurn 
{
    public class report
    {
        // duration
        public System.TimeSpan Duration {get; set;}
        // StaticSetSize
        public long UnitSize {get; set;}
        // result
        public double AllocationSpeed {get; set;}
    }
    public class App
    {
        public class Options 
        {
            [Option('d', "duration", Required = false, HelpText = "Test pass duration, seconds",
                Default = 10)]
            public int? Duration { get; set; }

            [Option('m', "staticSetSize", Required = false, HelpText = "Static set size, GB",
                Default = null)] // null = same as physical RAM amount
            public string StaticSetSize { get; set; }

            [Option('t', "threads", Required = false, HelpText = "Number of threads to use",
                Default = null)]
            public string ThreadCount { get; set; }

            [Option('o', "maxSize", Required = false, HelpText = "Max. object size", 
                Default = null)] // null = don't change what's on start
            public string MaxSize { get; set; }
            
            [Option('r', "runTests", Required = false, HelpText = "Tests to run (a = raw allocation, b = burn)", 
                Default = null)] // null = don't change what's on start
            public string Tests { get; set; }
            
            [Option('l', "gcLatencyMode", Required = false, HelpText = "Latency mode", 
                Default = null)] // null = don't change what's on start
            public string GCLatencyMode { get; set; }
            
            [Option('p', "outputMode", Required = false, HelpText = "Output mode (f = full, m = minimal)", 
                Default = null)] // null = don't change what's on start
            public string OutputMode { get; set; }
            [Option('f', "outputFileAddr", Required = false, HelpText = "Specify the output file location")]
            public string OutputAddr {get; set;}
            [Option('u', "UnitSize", Required = = false, HelpText = "Specify the allocation size")]
            public long? UnitSize{get; set;}
        }
        
        public IndentedTextWriter Writer = new IndentedTextWriter(Console.Out, "  ");
        
        static int Main(string[] args)
        {
            try {
                Parser.Default.ParseArguments<Options>(args)
                    .WithParsed(options => new App().Run(options))
                    .WithNotParsed(errors => {}); // Parse errors are printed by default
                return 0;
            }                                  
            catch (Exception e) {
                Console.WriteLine();
                Console.WriteLine($"Error: {e.Message}");
                return 1;
            }
        }

        public void append_json(string filename, report obj)
        {
            // First check wether this file exists
            List<report> _data = new List<report>();
            
            if (File.Exists(filename)){
                // if file exists, read out the file
                using (StreamReader r = new StreamReader(filename)){
                    string json_content = r.ReadToEnd();
                    _data = JsonSerializer.Deserialize<List<report>>(json_content);
                }
            }

            // if file does not exist, do nothing
            // append the new report
            _data.Add(obj);
            // dump the new json to 
            string json = JsonSerializer.Serialize(_data);
            File.WriteAllText(filename, json);
        }        
        public void Run(Options options)
        {
            // Applying options
            if (!string.IsNullOrEmpty(options.GCLatencyMode))
                GCSettings.LatencyMode = Enum.Parse<GCLatencyMode>(options.GCLatencyMode);
            if (options.UnitSize.HasValue)
                UnitAllocator.UnitSize = options.UnitSize.Value;
            if (options.Duration.HasValue)
                BurnTester.DefaultDuration = TimeSpan.FromSeconds(options.Duration.Value);
                SpeedTester.DefaultDuration = TimeSpan.FromSeconds(options.Duration.Value);
            BurnTester.DefaultMaxSize = ArgumentHelper.ParseRelativeValue(
                options.MaxSize, BurnTester.DefaultMaxSize, true);
            ParallelRunner.ThreadCount = (int) ArgumentHelper.ParseRelativeValue(
                options.ThreadCount, ParallelRunner.ThreadCount, true);
            var tests = options.Tests?.ToLowerInvariant() ?? "";
            var ramSizeGb = HardwareInfo.GetRamSize() ?? 4;
            var staticSetSizeGb = 0;
            if (!string.IsNullOrEmpty(options.StaticSetSize)) {
                tests += "b";
                staticSetSizeGb = (int) ArgumentHelper.ParseRelativeValue(options.StaticSetSize, ramSizeGb, true);
            }
            // ?? operator returns the value of the left-hand operand if it isn't null
            // Otherwise, it evaluaates the right-hand operand and returns 
            var outputMode = options.OutputMode ?? "f";
            var outputAddr = options.OutputAddr ?? "result.json";
            if (outputMode == "f") {
                // Dumping environment info
                Writer.AppendValue("Launch parameters", string.Join(" ", Environment.GetCommandLineArgs().Skip(1)));
                using (Writer.Section("Software:")) {
                    Writer.AppendValue("Runtime", ".NET Core");
                    using (Writer.Indent()) {
                        Writer.AppendValue("Version", RuntimeInformation.FrameworkDescription);
                        Writer.AppendValue("GC mode", GCInfo.GetGCMode());
                    }

                    Writer.AppendValue("OS",
                        $"{RuntimeInformation.OSDescription.Trim()} ({RuntimeInformation.OSArchitecture})");
                }

                using (Writer.Section("Hardware:")) {
                    var coreCountAddon = ParallelRunner.ThreadCount != Environment.ProcessorCount
                        ? $", {ParallelRunner.ThreadCount} used by test"
                        : "";
                    Writer.AppendValue("CPU", HardwareInfo.GetCpuModelName());
                    Writer.AppendValue("CPU core count", $"{Environment.ProcessorCount}{coreCountAddon}");
                    Writer.AppendValue("RAM size", $"{ramSizeGb:N0} GB");
                }
                Writer.AppendLine();
            }
            
            RunWarmup();

            if (tests == "") {
                RunSpeedTest();
                RunBurnTest("--- Stateless server (no static set) ---", 0);
                RunBurnTest("--- Worker / typical server (static set = 20% RAM) ---", (long) (ramSizeGb * Sizes.GB / 5));
                RunBurnTest("--- Caching / compute server (static set = 50% RAM) ---", (long) (ramSizeGb * Sizes.GB / 2));
                return;
            }

            if (tests.Contains("a")) {
                var result = RunSpeedTest();
                report baseline_result = new report{
                    Duration = BurnTester.DefaultDuration,
                    UnitSize = UnitAllocator.UnitSize,
                    AllocationSpeed = result,

                };
                append_json(outputAddr, baseline_result);
            }
            if (tests.Contains("b")) {
                var title = $"--- Static set = {staticSetSizeGb} GB ({staticSetSizeGb * 100.0 / ramSizeGb:0.##} % RAM) ---";
                RunBurnTest(title, (long) (staticSetSizeGb * Sizes.GB));
            }
        }

        public void RunWarmup() 
        {
            var speedTester = SpeedTester.NewWarmup();
            speedTester.Run();
            var burnTester = BurnTester.NewWarmup(10 * (long) Sizes.MB);
            burnTester.Run();
        }

        public double RunSpeedTest()
        {
            Writer.AppendLine("--- Raw allocation (w/o holding what's allocated) ---");
            Writer.AppendLine();
            var speedTester = SpeedTester.New();
            var result = speedTester.Run();
            return result;
        }

        public void RunBurnTest(string title, long staticSetSize)
        {
            Writer.AppendLine(title);
            Writer.AppendLine();
            var burnTester = BurnTester.New(staticSetSize);
            burnTester.Run();
        }
    }
}
