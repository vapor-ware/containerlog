# Proxying a Standard logger to `containerlog

There may be times when your application relies on a framework, e.g. `uvicorn` and `fastapi`, and you want log output to be consistent between your application logs and those third-party libraries.

For libraries which use Python's built-in logging library, functionality exists to patch the `logging.Logger` instances used by third party libraries so they instead use a `containerlog.proxy.std.StdLoggerProxy`, which has the same interface as the `logging.Logger`, but uses a `containerlog.Logger` to do the actual logging.

To use it, you should call `patch` as early on in your application as possible. Passing no arguments to `patch` will update the `logging.Manager` so all existing instances of `logging.Logger` get replaced and sets the `loggerClass` on the manager so all future loggers get initialized as a `StdLoggerProxy` from the start.

If you do provide args, it will only replace the loggger(s) which match the name globs provided. Not only does it update the references in the `logging.Manager`, but it also traverses all imported modules and replaces the logger if it is defined in the module's global scope.

!!! Note
    Once you do this, you've allowed containerlog to go and modify things at Runtime. There are no capabilities current or planned to enable rolling back these modifications, so use at your own risk/convenience.

## Example

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
