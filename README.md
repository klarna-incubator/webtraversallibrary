# Project Name
> The Web Traversal Library (WTL) is a Python library for abstracting web interactions on top of a base execution layer such as Selenium.

[![Build Status][ci-image]][ci-url]
[![License][license-image]][license-url]
[![Developed at Klarna][klarna-image]][klarna-url]


One to two paragraph statement about your project and what it does.

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
It's super easy! Create an empty policy, a `Workflow` object, and call run.

```py
import webtraversallibrary as wtl

def policy(workflow, view):
    return {}

workflow = wtl.Workflow(
    url='www.concernsofadataguy.com',
    policy=policy
)

workflow.run()
```

The above will go to your URL and not do anything, forever. Good stuff.

The input to the policy is a reference to the `Workflow` object as well as snapshots of all open tabs (one, in this case), called `View`(s).

You can improve upon this in the following ways:

- Have the policy actually do something by returning an action or a list of actions. Actions are divided into `ElementAction` and `ViewAction`. Examples of the former are `Click` and `FillText`. Examples of the latter are `Navigate` and `Refresh`.

```py
@wtl.single_tab
def policy(workflow, view):
    return wtl.actions.Click(wtl.Selector('#next'))
)
```

The single_tab decorator simplifies policies for you if you have only one tab. Instead of getting a dictionary of tab name to View, you will only get the single View. There are also decorators that facilitate using coroutines, see the examples for details.

- Specify a `goal` function that returns a boolean on whether the target has been reached. If this returns `True`, the workflow ends. This function takes the same parameters as the policy.

```py
@wtl.single_tab
def goal(workflow, view):
    return view.snapshot.page_metadata['url'] == 'www.goal.com'

workflow = wtl.Workflow(
    ...
    goal=goal
)
```

- Add element and view classifiers. These will run before the policy is executed and supply scores to all or a subset of the elements located on the page. There is also API for running a classifier on request, and enabling/disabling recurring classifiers. An action is either created on the fly or picked from the list of available actions, populated by a prior classifier (below, all links will be considered clickable).

```py
def link_classifier_func(elements, workflow):
    # The condition here is completely hard-coded for the given page.
    return [elem for elem in elements if elem.metadata["tag"] == "a"]

workflow.classifiers.add(
    wtl.ElementClassifier(
        name="link",
        action=wtl.actions.Click,
        highlight=True,
        callback=link_classifier_func,
    )
)
```

- Alter default configuration values by creating a new `Config` object and supplying it to the `workflow` initializer. Some configurations are grouped into predefined sets, such as `desktop`, but all values can be set manually. See documentation for the `Config` class for details.

```py
config = wtl.Config.default(["desktop"])
config.browser.height = 2000

workflow = wtl.Workflow(
    ...
    config=config
)
```

- Use multiple tabs and windows by supplying a dictionary to the url parameter. Each element is the name of a tab or a window. The policy should then return a dictionary of tab name to action (or list of actions).

```py

workflow = wtl.Workflow(
    ...
    url={
        "window_1": {
            "tab_1": "url_1",
            "tab_2": "url_2",
        },
        "window_2": {
            "tab_3": "url_3"
        }
    }
)
```

- Provide an output directory (needed if configured with `config.debug.save: true`). The folder will be created if it does not exist and populated with enumerated (0, 1, 2, ...) subfolders, one for each invocation of the workflow policy. Inside each snapshot for all open tabs will be saved.

```py
workflow = wtl.Workflow(
    ...
    output=Path("my_output/")
)
```

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


_For more examples and usage, please refer to the [Docs](TODO)._

## Development setup

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
make install
npm test
```

## How to contribute

See our guide on [contributing](.github/CONTRIBUTING.md).

## Release History

See our [changelog](CHANGELOG.md).

## License

Copyright © 2020 Klarna Bank AB

For license details, see the [LICENSE](LICENSE) file in the root of this project.


<!-- Markdown link & img dfn's -->
[ci-image]: https://img.shields.io/badge/build-passing-brightgreen?style=flat-square
[ci-url]: https://github.com/klarna-incubator/TODO
[license-image]: https://img.shields.io/badge/license-Apache%202-blue?style=flat-square
[license-url]: http://www.apache.org/licenses/LICENSE-2.0
[klarna-image]: https://img.shields.io/badge/%20-Developed%20at%20Klarna-black?labelColor=ffb3c7&style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAOCAYAAAAmL5yKAAAAAXNSR0IArs4c6QAAAIRlWElmTU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAALQAAAAAQAAAtAAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAAABCgAwAEAAAAAQAAAA4AAAAA0LMKiwAAAAlwSFlzAABuugAAbroB1t6xFwAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAAAVBJREFUKBVtkz0vREEUhsdXgo5qJXohkUgQ0fgFNFpR2V5ClP6CQu9PiB6lEL1I7B9A4/treZ47c252s97k2ffMmZkz5869m1JKL/AFbzAHaiRbmsIf4BdaMAZqMFsOXNxXkroKbxCPV5l8yHOJLVipn9/vEreLa7FguSN3S2ynA/ATeQuI8tTY6OOY34DQaQnq9mPCDtxoBwuRxPfAvPMWnARlB12KAi6eLTPruOOP4gcl33O6+Sjgc83DJkRH+h2MgorLzaPy68W48BG2S+xYnmAa1L+nOxEduMH3fgjGFvZeVkANZau68B6CrgJxWosFFpF7iG+h5wKZqwt42qIJtARu/ix+gqsosEq8D35o6R3c7OL4lAnTDljEe9B3Qa2BYzmHemDCt6Diwo6JY7E+A82OnN9HuoBruAQvUQ1nSxP4GVzBDRyBfygf6RW2/gD3NmEv+K/DZgAAAABJRU5ErkJggg==
[klarna-url]: https://github.com/klarna-incubator
