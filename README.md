# containerlog

A lightweight, optimized, and opinionated structured logging library for Python, intended for containerized applications.

`containerlog` was born out of a desire to have high-quality structured logging for
containerized applications (e.g. microservices) without having to compromise detailed
logging for application/request latency.

[`structlog`](https://www.structlog.org/en/stable/) is a great general-purpose structured
logging library for Python, but being general-purpose means that there is additional overhead
when logging messages.

When [we](https://github.com/vapor-ware) updated a microservice to use structured logging,
we found that [request latency went up](https://github.com/vapor-ware/synse-server/issues/384),
seemingly due to the transition to use `structlog`.

`containerlog` is not for everyone. It is highly opinionated, minimally configurable,
and intentionally feature-sparse so that it can achieve [better performance](#benchmarks) than
the Python standard logger

Not every application needs optimized logging, but where latency and performance matters,
`containerlog` could work for you.

```
timestamp='2020-07-23T13:11:28.009804Z' logger='my-logger' level='debug' event='loading configuration' path='./config.yaml'
timestamp='2020-07-23T13:11:28.010137Z' logger='my-logger' level='info' event='starting application' 
timestamp='2020-07-23T13:11:28.010158Z' logger='my-logger' level='warn' event='having too much fun' countdown=[3, 2, 1]
```

## Installation

`containerlog` can be installed with pip:

```
pip install containerlog
```

It is only intended to work for Python 3.6+.

## Usage

See the documentation at https://containerlog.readthedocs.io/en/docs/

## Optimizations

There are numerous sources discussion micro-optimizations in Python. This project probably
does not implement them all, so there is room for improvement. Current optimization work has
leveraged:

* [`dis`](https://docs.python.org/3/library/dis.html): to disassemble python bytecode for analysis 
* [`timeit`](https://docs.python.org/3/library/timeit.html): to measure execution time of code snippets

If you wish to contribute optimizations and use other libraries, tools, or sources, open a PR to add
them to this list.

## Benchmarks

Benchmarking scripts can be found in the [benchmarks](benchmarks) directory. To run,

```
$ cd benchmarks
$ ./run.sh
```

This will run benchmarks the Python standard logger and for `containerlog`. The latest results
can be found below.

### Results

Benchmarks were measured using Python 3.8.0 on macOS 10.15.1 with a 2.9 GHz 6-Core Intel Core i9
processor and 16 GB 2400 MHz DDR4 memory.

![containerlog 0.3.0](benchmarks/results/benchmark-containerlog-0.3.0.png)

| Benchmark | std logger (ns) | std proxy (ns) | containerlog (ns) |
| --------- | --------------- | -------------- | ----------------- |
| baseline | 0.68 +/- 0.02 | 0.69 +/- 0.01 | 0.7 +/- 0.02 |
| silent | 108.0 +/- 6.0 | 1140.0 +/- 50.0 | 51.7 +/- 1.7 |
| basic | 4750.0 +/- 160.0 | 1140.0 +/- 60.0 | 1070.0 +/- 50.0 |
| short-simple | 5370.0 +/- 160.0 | 1280.0 +/- 60.0 | 1330.0 +/- 60.0 |
| long-simple | 5280.0 +/- 180.0 | 1480.0 +/- 70.0 | 2120.0 +/- 60.0 |
| short-complex | 5630.0 +/- 170.0 | 1500.0 +/- 150.0 | 1480.0 +/- 80.0 |
| long-complex | 6900.0 +/- 190.0 | 2870.0 +/- 80.0 | 3260.0 +/- 80.0 |
| exception | 10400.0 +/- 300.0 | 4440.0 +/- 150.0 | 4370.0 +/- 500.0 |

## Contribute

While `containerlog` is intentionally feature-sparse, feature requests are welcome. Additionally,
if you can find any other ways to micro-optimize the codebase, pull requests are very much
appreciated.

