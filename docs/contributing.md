# Contributing

While `containerlog` is intentionally kept relatively feature-sparse to keep it performant, feature requests are very welcome. In addition to any feature requests, we appreciate any enhancements, bug reporting, and additional optimizations.

## Workflow

For any feature requests, questions, bug reports, etc, please [open an issue](https://github.com/vapor-ware/containerlog/issues/new).

Particularly for bug reports, please be sure to include as much context as you can, including the version of `containerlog` which you are using, the OS, and the version of Python.

Pull requests should generally be tied to an issue. This allows all work to be tracked and enables any discussion or questions around the development.

!!! note
    Issues don't need to be created for trivial changes, such as minor updates to docs, fixing typos, formatting, etc.

## Developing

If you choose to help develop `containerlog`, its helpful to have `make` installed, as most of the developer workflow is encapsulated as make targets.

For a full accounting of available targets, see the `Makefile` or run `make help`.

The three targets to take note of:

* `make fmt`: Performs some basic automated code formatting
* `make lint`: Runs linting checks against the code base
* `make test`: Runs project unit tests

In order for any contribution to be accepted, it must pass CI checks, which means that it should be formatted and linted, unit tests should be passing, and there should be sufficient test coverage.
