# Getting started

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
