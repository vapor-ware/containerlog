"""A basic example of a FastAPI + uvicorn application using containerlog.

To run, simply:

  uvicorn main:app --reload

This has the log level set to TRACE to showcase that custom logging levels
may also be proxied from the standard logger. Uvicorn has some trace-level
logging for h11 connections, where the trace level is custom and not a default
part of the standard logging library.

Once a request is made to the application, e.g. `curl localhost:8000/`, you
should see logs similar to the following, which includes the trace-level logging:

    $ uvicorn main:app --reload
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [37068] using statreload
    INFO:     Started server process [37085]
    timestamp='2020-12-16T13:08:54.706188Z' logger='uvicorn.error' level='info' event='Waiting for application startup.'
    timestamp='2020-12-16T13:08:54.706650Z' logger='uvicorn.error' level='info' event='Application startup complete.'
    timestamp='2020-12-16T13:09:00.198539Z' logger='uvicorn.error' level='trace' event='127.0.0.1:56623 - Connection made'
    timestamp='2020-12-16T13:09:00.200692Z' logger='main' level='info' event='processing request' method='GET' url=http://localhost:8000/
    timestamp='2020-12-16T13:09:00.202050Z' logger='uvicorn.error' level='trace' event='127.0.0.1:56623 - Connection lost'
"""

import containerlog
from containerlog.proxy.std import patch
from fastapi import FastAPI, Request

logger = containerlog.get_logger()
containerlog.set_level(containerlog.TRACE)

app = FastAPI()

# Globally patch all standard loggers to use containerlog.
patch()


@app.get('/')
async def root(request: Request):
    logger.info('processing request', method=request.method, url=request.url)
    return {'status': 'ok'}
