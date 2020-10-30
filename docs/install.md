# Install

containerlog is hosted on [pypi.org](https://pypi.org/project/containerlog/), so it can simply be installed via `pip`

```
pip install containerlog
```

or whichever dependency management tool you prefer

```
poetry add containerlog
```

containerlog does not have any external dependencies, so all you need is a supported version of Python (3.6, 3.7, 3.8, 3.9).

## Future Work

* Enable [cython](https://cython.org/) support for containerlog. This section will be updated with relevant documentation once this work is complete. ([vapor-ware/containerlog#3](https://github.com/vapor-ware/containerlog/issues/3))
* Implement basic logging middleware, requiring optional package dependencies to be set up ([vapor-ware/containerlog#15](https://github.com/vapor-ware/containerlog/issues/15))
