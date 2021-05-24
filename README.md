# Web Traversal Library
> The Web Traversal Library (WTL) is a Python library for abstracting web interactions on top of a base execution layer such as Selenium.

[![Developed at Klarna][klarna-image]][klarna-url]
[![Build Status][ci-image]][ci-url]
[![License][license-image]][license-url]
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
[klarna-image]: https://shields.io/badge/Developed%20at%20Klarna-black?logo=klarna
[klarna-url]: https://github.com/klarna-incubator
