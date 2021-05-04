"""Logging benchmarks for containerlog's proxy for the standard logger."""

import io

import pyperf

import containerlog.proxy.std
from containerlog import contextvars as logctx


class Custom:
    def __init__(self):
        self.val = 1

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<Custom Object: {self.val}>"


MSG_BASIC = "some message to log"
MSG_FORMAT_SHORT_SIMPLE = "a formatted message str=%s"
MSG_FORMAT_LONG_SIMPLE = "a formatted message bool=%s str=%s int=%d float=%d"
MSG_FORMAT_SHORT_COMPLEX = "a formatted message obj=%s"
MSG_FORMAT_LONG_COMPLEX = "a formatted message obj=%s list=%s dict=%s tuple=%s"

SHORT_ARGS_SIMPLE = ["example"]
LONG_ARGS_SIMPLE = [True, "example", 10, 0.131]
SHORT_ARGS_COMPLEX = [Custom()]
LONG_ARGS_COMPLEX = [
    Custom(),
    [Custom(), Custom()],
    {"a": Custom(), "b": Custom},
    (Custom(), Custom()),
]


def bench_baseline(loops, logger):
    # use fast local vars
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    for _ in range_loops:
        # pass-through: do nothing to get a baseline
        pass

    return pyperf.perf_counter() - t0


def bench_silent(loops, logger):
    # use fast local vars
    m = MSG_BASIC
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    for _ in range_loops:
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)

    return pyperf.perf_counter() - t0


def bench_basic(loops, logger):
    # use fast local vars
    m = MSG_BASIC
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    for _ in range_loops:
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)

    return pyperf.perf_counter() - t0


def bench_short_simple(loops, logger):
    # use fast local vars
    m = MSG_FORMAT_SHORT_SIMPLE
    args = SHORT_ARGS_SIMPLE
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    for _ in range_loops:
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)

    return pyperf.perf_counter() - t0


def bench_long_simple(loops, logger):
    # use fast local vars
    m = MSG_FORMAT_LONG_SIMPLE
    args = LONG_ARGS_SIMPLE
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    for _ in range_loops:
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)

    return pyperf.perf_counter() - t0


def bench_short_complex(loops, logger):
    # use fast local vars
    m = MSG_FORMAT_SHORT_COMPLEX
    args = SHORT_ARGS_COMPLEX
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    for _ in range_loops:
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)

    return pyperf.perf_counter() - t0


def bench_long_complex(loops, logger):
    # use fast local vars
    m = MSG_FORMAT_LONG_COMPLEX
    args = LONG_ARGS_COMPLEX
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    for _ in range_loops:
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)

    return pyperf.perf_counter() - t0


def bench_exception(loops, logger):
    # use fast local vars
    m = MSG_BASIC
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    for _ in range_loops:
        logger.exception(m)
        logger.exception(m)
        logger.exception(m)
        logger.exception(m)
        logger.exception(m)
        logger.exception(m)
        logger.exception(m)
        logger.exception(m)
        logger.exception(m)
        logger.exception(m)

    return pyperf.perf_counter() - t0


def bench_async_context(loops, logger):
    # use fast local vars
    m = MSG_FORMAT_LONG_SIMPLE
    args = LONG_ARGS_SIMPLE
    range_loops = range(loops)
    t0 = pyperf.perf_counter()

    logctx.bind(testing=True, value="foo")

    for _ in range_loops:
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)
        logger.warning(m, *args)

    logctx.clear()

    return pyperf.perf_counter() - t0


BENCHMARKS = {
    "baseline": bench_baseline,
    "silent": bench_silent,
    "basic": bench_basic,
    "short-simple": bench_short_simple,
    "long-simple": bench_long_simple,
    "short-complex": bench_short_complex,
    "long-complex": bench_long_complex,
    "exception": bench_exception,
    "async-context": bench_async_context,
}


if __name__ == "__main__":
    runner = pyperf.Runner()
    runner.metadata["description"] = "Test the performance of Python standard logger."

    # Note: StringIO performance will impact the results
    stream = io.StringIO()

    # Setup the logger
    proxy_log = containerlog.proxy.std.StdLoggerProxy("bench-std-proxy")
    proxy_log.level = containerlog.WARN
    proxy_log.writeout = stream.write
    proxy_log.writeerr = stream.write

    for name, fn in BENCHMARKS.items():
        # Truncate the stream before each benchmark.
        stream.seek(0)
        stream.truncate()

        runner.bench_time_func(
            name,
            fn,
            proxy_log,
            inner_loops=25,
        )
