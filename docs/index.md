# containerlog

## Overview

A lightweight, optimized, and opinionated structured logging library for Python, intended for containerized applications.

`containerlog` was created out of a desire to have structured logging for containerized web applications (e.g. microservices) without having to compromise between the detail provided with structured logging and logger performance.

The current de-facto structured logging library for Python is [`structlog`](https://www.structlog.org/en/stable/); it is a great, general-purpose structured logging library, but its generalization and configurability can create a [noticeable impact in latency](https://github.com/vapor-ware/synse-server/issues/384).

`containerlog` is not for everyone. To squeeze out as much performance as it can and be as low-impact to application latency as possible, it is highly opinionated, minimally configurable, and intentionally feature sparse. In doing so, it can achieve better performance than the Python standard logger.

## Format

```
timestamp='2020-07-23T13:11:28.009804Z' logger='my-logger' level='debug' event='loading configuration' path='./config.yaml'
timestamp='2020-07-23T13:11:28.010137Z' logger='my-logger' level='info' event='starting application'
timestamp='2020-07-23T13:11:28.010158Z' logger='my-logger' level='warn' event='having too much fun' countdown=[3, 2, 1]
```

The logs emitted by `containerlog` will look similar to the above snippet. They include:

- An RFC3339-formatted timestamp, under the `timestamp` key. This key will always be first.
- The name of the logger under the `logger` key. This key will always be second.
- The level that the message was logged at under the `level` key. This key will always be third.
- The message that was logged under the `event` key. This key will always be fourth.
- Any keyword arguments (structured data) logged with the message will follow.

!!! Important
    When passing keyword arguments to the logger for structured data, the above keywords (`timestamp`, `logger`, `level`, and `event`) are reserved. If they are found in the log function's keyword args, they will be modified and be prepended with an underscore (`_`).

This format is opinionated and may not contain all information that some may want, but its static nature provides performance improvements to `containerlog`.
