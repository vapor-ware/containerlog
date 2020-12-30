# Basic Usage

The API for `containerlog` is fairly sparse and there is very little configuration that can be done for it. As such, it is simple to get started with and quickly integrate into your application.

## Create a Logger

Similar to the Python standard logger, a `containerlog` logger is initialized, typically at the module level, using `get_logger`.

The logger name can be passed in explicitly

```python
logger = containerlog.get_logger('my-logger')
```

or, it can use the module name if no name is explicitly provided.

```python
logger = containerlog.get_logger()
```

## Configuration

There are only a handful of options that can be configured for a logger.

### Log Level

Log levels are defined at the `containerlog` module level. The supported levels are:

- `containerlog.TRACE` (0)
- `containerlog.DEBUG` (1)
- `containerlog.INFO` (2)
- `containerlog.WARN` (3)
- `containerlog.ERROR` (4)
- `containerlog.CRITICAL` (5)

These are internally mapped as integers, so the corresponding int may also be used to designate the log level.

Log levels may be set on a single logger via the `level` attribute.

```python
logger.level = containerlog.INFO
```

Or, the log level can be set globally for all loggers

```python
containerlog.set_level(containerlog.INFO)
```

#### Design Choices

- If no logging level is set, it will default to `debug`. This does not follow other loggers which may choose to default to an `info` level. The rationale behind this is that for a default use case, it is better to display too much information rather than too little.

    As such, you may find yourself needing to configuring the log level in an inverse fashion from what you may be used to.

    ```python
    if not config.DEBUG:
      containerlog.set_level(containerlog.INFO)
    ```

### Log Output

Loggers can also be configured to change the location of where logs are written to. In general, this should not need to be configured, though it can be useful when writing tests and needing to capture log output.

By default, logs at level ERROR or greater are written to `stderr`, while logs at WARN or less are written to `stdout`.

The target for error output can be set via the `Logger`'s `writeerr` attribute, e.g.

```python
err_stream = io.StringIO()
logger.writeerr = err_stream.write
```

For normal output, set the `writeout` attribute.

```python
out_stream = io.StringIO()
logger.writeout = out_stream.write
```

!!! Optimization
    The `writeerr` and `writeout` attributes should reference the `write` function for an IO implementation, not the object which implements the IO interface itself. This is an optimization, as it localizes the function for faster loading.

If you do not wish to log to two different streams, you can set one stream equal to the other.

```python
logger.writeout = logger.writeerr
```

## Logging

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

Data passed in as keyword arguments to any of the logging methods gets rendered as key-value pairs for the structured log.

```python
logger.info('connected to remote server', ip=server_ip, port=server_port)
```

!!! Tip
    Since this library is intended to be used for structured logging, avoid logging formatted messages to minimize the performance penalty from the additional string format.

    If a logger is configured at `INFO` level, a debug message

    ```python
    logger.debug(f'got a value: {value}')
    ```

    would **not** get logged, but the string formatting woulds still happen since it is done upfront, not within the log function. Instead, pass values as keyword arguments.

    ```python
    logger.debug('got a value', value=value)
    ```

## Logger Behavior

### Disable a Logger

Internally, log levels are compared to determine what level something should be logged at. For example, if logging a message at debug (1) level, but the logger is configured at info (2) level, `1 < 2`, so the message does not get logged.

To disable a logger, the log level is just set to a value higher than any of the supported log levels. Canonically, this is `99`, but could be anything higher than `critical`.

To disable a logger, simply call the `disable()` method.

```python
logger.disable()
```

this will prevent it from emitting any logs.

To check whether a logger is disabled, check the `disabled` property.

```python
if logger.disabled:
    ...
```

### Enable a Logger

If a logger was previously disabled, it can be re-enabled by calling the Logger's `enable()` method.

```python
logger.enable()
```

This will restore its log level to its previously known level, prior to having `disable()` called.

If a logger is already enabled, this call will do nothing.

### Disable Loggers Globally

Instead of disabling a single logger, you may want to disable all loggers. This can be done be calling the package's `disable` function.

```python
containerlog.disable()
```

This could be useful in tests to suppress log output.

Disabling *all* loggers can be heavy-handed at times. For more granular control, you can pass the name(s) of the loggers to disable, globs to match against logger names, or a combination of both.

```python
containerlog.disable('my-app.secrets*', 'third-party-logger')
```

### Enable Loggers Globally

Calling the module level `enable` performs the inverse of the global disable. It can re-enable all loggers if no arguments are provided

```python
containerlog.enable()
```

Or it can selectively re-enable based on string or glob match to the logger name.

```python
containerlog.enable('my-app.secrets*', 'third-party-logger')
```
