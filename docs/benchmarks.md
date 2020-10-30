# Benchmarks

This page summarizes some basic benchmarks for various versions of `containerlog`. Each new major and minor (but not necessarily patch) release should have benchmarks run and should have this page subsequently updated.

## Running

Benchmarking scripts are found in the project's [benchmarks](https://github.com/vapor-ware/containerlog/tree/master/benchmarks) directory. To run them,

```
$ cd benchmarks
$ ./run.sh
```

This will run benchmarks the Python standard logger and for `containerlog`. The results are kept in the `benchmarks/results` subdirectory.

## Results

Benchmarks are measured using Python 3.8.0 on macOS 10.15.1 with a 2.9 GHz 6-Core Intel Core i9 processor and 16 GB 2400 MHz DDR4 memory.

Results are measured in nanoseconds. The smaller number is better.

Note that in the results below:
!!! note
    In the results below:
    
    - *"std logger"* refers to the Python standard logger (`import logging`)
    - *"std proxy"* refers to the containerlog proxy for the Python standard logger (`import containerlog.proxy.std`)
    - *"containerlog"* refers to the core containerlog logger implementation (`import containerlog`)

The proxy logger uses the core containerlog logger under the covers, so their benchmarks should be relatively similar.

### v0.2.0

| Benchmark | std logger (ns) | std proxy (ns) | containerlog (ns) |
| --------- | --------------- | -------------- | ----------------- |
| baseline | **0.64** +/- 0.01 | **0.64** +/- 0.01 | 0.65 +/- 0.01 |
| silent | 102.0 +/- 3.0 | 1120.0 +/- 40.0 | **56.2** +/- 1.3 |
| basic | 4550.0 +/- 160.0 | 1130.0 +/- 40.0 | **1030.0** +/- 30.0 |
| short-simple | 5090.0 +/- 120.0 | 1300.0 +/- 60.0 | **1250.0** +/- 70.0 |
| long-simple | 5040.0 +/- 170.0 | **1440.0** +/- 60.0 | 2020.0 +/- 70.0 |
| short-complex | 5430.0 +/- 200.0 | 1450.0 +/- 60.0 | **1370.0** +/- 50.0 |
| long-complex | 6590.0 +/- 140.0 | **2770.0** +/- 60.0 | 3160.0 +/- 100.0 |
| exception | 10000.0 +/- 400.0 | 4330.0 +/- 120.0 | **4050.0** +/- 170.0 |

