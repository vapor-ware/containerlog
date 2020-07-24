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

The API for `containerlog` is sparse, thus simple. There are generally two things you will
ever need to do with it:

### 1. Creating/Configuring a Logger

Similar to the Python standard logger, a logger should in initialized in a module using `get_logger`

```python
# Logger using module as name
logger = containerlog.get_logger()

# Logger with explicit name set
logger = containerlog.get_logger('my-logger')
```

If `get_logger` is not given a name, it will use the name of the module.

There are only a handful of things which can be configured:

* The logger name
  ```python
  # Set name via `get_logger`
  logger = containerlog.get_logger('my-logger')
  ```
* The log level
  ```python
  # Set log level on a single logger
  logger.level = containerlog.INFO

  # Set log level for all loggers
  containerlog.set_level(containerlog.INFO)
  ```
* Where logs are written to. Generally this shouldn't need to be configured,
  though it may be useful when writing tests. `containerlog` writes to stdout and
  stderr by default.
  ```python
  # Set write target for non-error logs
  out_stream = io.StringIO()
  logger.writeout = out_stream.write

  # Set write target for error logs
  err_stream = io.StringIO()
  logger.writerr = err_stream.write
  ```

By default, `containerlog` logs at `DEBUG` level. This is an opinionated decision
with the thought that using this out of the box, its better to capture more logs than
fewer logs, though the appropriate log level should be set by the application. 

### 2. Logging a message

Once you have a logger, you can log a message at `trace`, `debug`, `info`, `warn`, `error`, or `critical` level.

```python
# Log at trace level
logger.trace('message to log')

# Log at debug level
logger.debug('message to log')

# Log at info level
logger.info('message to log')

# Log at warn level
logger.warn('message to log')
logger.warning('message to log')

# Log at error level
logger.error('message to log')

# Log at critical level
logger.critical('message to log')
```

Data passed in as keyword arguments to any of the logging methods gets rendered as
key-value pairs for the structured log.

```python
logger.info('connected to remote server', ip=server_ip, port=server_port)
```

> **Note**: Since this library is intended to be used for structured logging, avoid
> logging formatted message to avoid a performance penalty.
>
> If logging at INFO level,
>
> ```python
> logger.debug(f'got a new value: {value}')
> ```
>
> would not get logged, but the string formatting would still happen since it is being
> done upfront, not within the log function. Instead, pass it as a kwarg:
>
> ```python
> logger.debug('got a new value', value=value)
> ```

Log levels are modeled as integers internally. Logging can be disabled for a logger either
by calling `disable` on the logger, or by setting the level above `containerlog.CRITICAL`.

```python
# Disable via method
logger.disable()

# Disable via log level
logger.level = 99
```

## Advanced Usage

There may be times when your application relies on a framework, e.g. `uvicorn` and `fastapi`,
and you want log output to be consistent between your application logs and those third-party
libraries.

For libraries which use Python's built-in logging library, functionality exists to patch
the `logging.Logger` instances used by third party libraries so they instead use a
`containerlog.proxy.std.StdLoggerProxy`, which has the same interface as the `logging.Logger`,
but uses a `containerlog.Logger` to do the actual logging.

To use it, you should call `patch` as early on in your application as possible. Passing no arguments
to `patch` will update the `logging.Manager` so all existing instances of `logging.Logger` get replaced
and sets the `loggerClass` on the manager so all future loggers get initialized as a `StdLoggerProxy` from
the start.

If you do provide args, it will only replace the loggger(s) which match the name globs provided. Not only
does it update the references in the `logging.Manager`, but it also traverses all imported modules and replaces
the logger if it is defined in the module's global scope.

> **Note**: Once you do this, you've allowed containerlog to go and modify things at Runtime. There are
> no capabilities current or planned to enable rolling back these modifications, so use at your own
> risk/convenience.

### Example

Given a simple file, `main.py` defining a FastAPI app, e.g.

```python
from fastapi import FastAPI

app = FastAPI(
    title='test application',
)
```

and running it with

```bash
uvicorn main:app --host 0.0.0.0
```

You'd get output similar to:

```
INFO:     Started server process [99362]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Using `containerlog`, you can patch the standard logger for `fastapi` and `uvicorn`, e.g.

```python
from fastapi import FastAPI
from containerlog.proxy.std import patch

patch('fastapi', 'uvicorn*', 'websockets*')

app = FastAPI(
    title='test application',
)
```

Re-running the same command as before, you should now see log output similar to:

```
timestamp='2020-07-24T15:36:00.981228Z' logger='uvicorn.error' level='info' event='Started server process [99395]' color_message='Started server process [%d]'
timestamp='2020-07-24T15:36:00.981435Z' logger='uvicorn.error' level='info' event='Waiting for application startup.' 
timestamp='2020-07-24T15:36:00.981634Z' logger='uvicorn.error' level='info' event='Application startup complete.' 
timestamp='2020-07-24T15:36:00.982344Z' logger='uvicorn.error' level='info' event='Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)' color_message='Uvicorn running on %s://%s:%d (Press CTRL+C to quit)'
```


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

![containerlog 0.2.0](benchmarks/results/benchmark-containerlog-0.2.0.png)

| Benchmark | std logger (ns) | std proxy (ns) | containerlog (ns) |
| --------- | --------------- | -------------- | ----------------- |
| baseline | 0.64 +/- 0.01 | 0.64 +/- 0.01 | 0.65 +/- 0.01 |
| silent | 102.0 +/- 3.0 | 1120.0 +/- 40.0 | 56.2 +/- 1.3 |
| basic | 4550.0 +/- 160.0 | 1130.0 +/- 40.0 | 1030.0 +/- 30.0 |
| short-simple | 5090.0 +/- 120.0 | 1300.0 +/- 60.0 | 1250.0 +/- 70.0 |
| long-simple | 5040.0 +/- 170.0 | 1440.0 +/- 60.0 | 2020.0 +/- 70.0 |
| short-complex | 5430.0 +/- 200.0 | 1450.0 +/- 60.0 | 1370.0 +/- 50.0 |
| long-complex | 6590.0 +/- 140.0 | 2770.0 +/- 60.0 | 3160.0 +/- 100.0 |
| exception | 10000.0 +/- 400.0 | 4330.0 +/- 120.0 | 4050.0 +/- 170.0 |

## Contribute

While `containerlog` is intentionally feature-sparse, feature requests are welcome. Additionally,
if you can find any other ways to micro-optimize the codebase, pull requests are very much
appreciated.

