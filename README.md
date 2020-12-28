# Web Traversal Library
> The Web Traversal Library (WTL) is a Python library for abstracting web interactions on top of a base execution layer such as Selenium.

[![Build Status][ci-image]][ci-url]
[![License][license-image]][license-url]
[![Developed at Klarna][klarna-image]][klarna-url]
[![Documentation Status](https://readthedocs.org/projects/webtraversallibrary/badge/?version=latest)](https://webtraversallibrary.readthedocs.io/en/latest/?badge=latest)

## Installation

Run `pip install webtraversallibrary`. That's it.

## Usage example

### Glossary
You will find more information in the API docs. As a high-level overview, common terms in the documentation are:

- *Workflow:* The main orhcestrating class handling the main "event loop". Sometimes "schema" is also used for the specification of a certain workflow.

- *View:* A static snapshot of a current website in a tab, with metadata associated to the page and its elements, possibly augmented with certain ML classifiers.

- *Policy:* WTL is based on principles of reinforcement learning, where a policy is a function of the current state (here, the snapshots of current open tabs) to a set of actions.

- *Classifier:* These, along with `preload_callbacks` and `postload_callbacks` are arbitray code that is executed on each workflow iteration. A classifier takes a set of elements and returns either a subset or a mapping from elements to numeric scores.

- *Config:* A helper class containing string, numeric, or boolean values for a number of configurations related to WTL. Some are pregrouped under certain umbrella names, such as `desktop` (running as a Desktop browser, the default is mobile emulation), but all values can be arbitrarily set. See the documentation for the `Config` class for more information.

### Getting started
See the documentation at [webtraversallibrary.readthedocs.io](https://webtraversallibrary.readthedocs.io/)!

Also watch ["Machine Learning to Auto-Navigate Websites"](https://www.youtube.com/watch?v=X0414BC6Q2I) given at PyCon SE 2020 for an introduction and examples.

### General architecture

The flow in a workflow is as follows:

1) Initialize the workflow with given config
2) Navigate to given URLs
3) Snapshot the pages
4) Run all classifiers
5) Check if the goal is fulfilled, if so exit
6) Call policy with the current view(s)
7) Execute the returned action(s)
8) Goto 3


_For more examples and usage, please run `make docs` and look at `docs/build/html/index.html`._

## Development setup

All development requirements are in requirements.txt. Install the packages from pip. Helper commands are available to create a virtual environment - `make env-create` and `make env-update`.

To lint the JavaScript files (not required unless you're editing them) you need `jshint` which is available from npm.

## How to contribute

See our guide on [contributing](.github/CONTRIBUTING.md).

## Release History

See our [changelog](CHANGELOG.md).

## License

Copyright © 2020 Klarna Bank AB

For license details, see the [LICENSE](LICENSE) file in the root of this project.


<!-- Markdown link & img dfn's -->
[ci-image]: https://img.shields.io/badge/build-passing-brightgreen?style=flat-square
[ci-url]: https://github.com/klarna-incubator/webtraversallibrary
[license-image]: https://img.shields.io/badge/license-Apache%202-blue?style=flat-square
[license-url]: http://www.apache.org/licenses/LICENSE-2.0
[klarna-image]: https://img.shields.io/badge/%20-Developed%20at%20Klarna-black?labelColor=ffb3c7&style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAOCAYAAAAmL5yKAAAAAXNSR0IArs4c6QAAAIRlWElmTU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAALQAAAAAQAAAtAAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAAABCgAwAEAAAAAQAAAA4AAAAA0LMKiwAAAAlwSFlzAABuugAAbroB1t6xFwAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAAAVBJREFUKBVtkz0vREEUhsdXgo5qJXohkUgQ0fgFNFpR2V5ClP6CQu9PiB6lEL1I7B9A4/treZ47c252s97k2ffMmZkz5869m1JKL/AFbzAHaiRbmsIf4BdaMAZqMFsOXNxXkroKbxCPV5l8yHOJLVipn9/vEreLa7FguSN3S2ynA/ATeQuI8tTY6OOY34DQaQnq9mPCDtxoBwuRxPfAvPMWnARlB12KAi6eLTPruOOP4gcl33O6+Sjgc83DJkRH+h2MgorLzaPy68W48BG2S+xYnmAa1L+nOxEduMH3fgjGFvZeVkANZau68B6CrgJxWosFFpF7iG+h5wKZqwt42qIJtARu/ix+gqsosEq8D35o6R3c7OL4lAnTDljEe9B3Qa2BYzmHemDCt6Diwo6JY7E+A82OnN9HuoBruAQvUQ1nSxP4GVzBDRyBfygf6RW2/gD3NmEv+K/DZgAAAABJRU5ErkJggg==
[klarna-url]: https://github.com/klarna-incubator
