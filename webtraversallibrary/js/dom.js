// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

// The following code is taken from https://github.com/testing-library/user-event
// and its dependency https://github.com/testing-library/dom-testing-library

 /*jshint -W030 */
const eventMap = {
    // Clipboard Events
    copy: {
      EventType: 'ClipboardEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    cut: {
      EventType: 'ClipboardEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    paste: {
      EventType: 'ClipboardEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    // Composition Events
    compositionEnd: {
      EventType: 'CompositionEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    compositionStart: {
      EventType: 'CompositionEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    compositionUpdate: {
      EventType: 'CompositionEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    // Keyboard Events
    keyDown: {
      EventType: 'KeyboardEvent',
      defaultInit: {bubbles: true, cancelable: true, charCode: 0},
    },
    keyPress: {
      EventType: 'KeyboardEvent',
      defaultInit: {bubbles: true, cancelable: true, charCode: 0},
    },
    keyUp: {
      EventType: 'KeyboardEvent',
      defaultInit: {bubbles: true, cancelable: true, charCode: 0},
    },
    // Focus Events
    focus: {
      EventType: 'FocusEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    blur: {
      EventType: 'FocusEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    focusIn: {
      EventType: 'FocusEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    focusOut: {
      EventType: 'FocusEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    // Form Events
    change: {
      EventType: 'Event',
      defaultInit: {bubbles: true, cancelable: false},
    },
    input: {
      EventType: 'InputEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    invalid: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: true},
    },
    submit: {
      EventType: 'Event',
      defaultInit: {bubbles: true, cancelable: true},
    },
    reset: {
      EventType: 'Event',
      defaultInit: {bubbles: true, cancelable: true},
    },
    // Mouse Events
    click: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: true, cancelable: true, button: 0},
    },
    contextMenu: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    dblClick: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    drag: {
      EventType: 'DragEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    dragEnd: {
      EventType: 'DragEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    dragEnter: {
      EventType: 'DragEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    dragExit: {
      EventType: 'DragEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    dragLeave: {
      EventType: 'DragEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    dragOver: {
      EventType: 'DragEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    dragStart: {
      EventType: 'DragEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    drop: {
      EventType: 'DragEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    mouseDown: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    mouseEnter: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    mouseLeave: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    mouseMove: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    mouseOut: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    mouseOver: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    mouseUp: {
      EventType: 'MouseEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    // Selection Events
    select: {
      EventType: 'Event',
      defaultInit: {bubbles: true, cancelable: false},
    },
    // Touch Events
    touchCancel: {
      EventType: 'TouchEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    touchEnd: {
      EventType: 'TouchEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    touchMove: {
      EventType: 'TouchEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    touchStart: {
      EventType: 'TouchEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    // UI Events
    scroll: {
      EventType: 'UIEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    // Wheel Events
    wheel: {
      EventType: 'WheelEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    // Media Events
    abort: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    canPlay: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    canPlayThrough: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    durationChange: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    emptied: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    encrypted: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    ended: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    // error: {
    //   EventType: Event,
    //   defaultInit: {bubbles: false, cancelable: false},
    // },
    loadedData: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    loadedMetadata: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    loadStart: {
      EventType: 'ProgressEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    pause: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    play: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    playing: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    progress: {
      EventType: 'ProgressEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    rateChange: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    seeked: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    seeking: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    stalled: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    suspend: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    timeUpdate: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    volumeChange: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    waiting: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    // Image Events
    load: {
      EventType: 'UIEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    error: {
      EventType: 'Event',
      defaultInit: {bubbles: false, cancelable: false},
    },
    // Animation Events
    animationStart: {
      EventType: 'AnimationEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    animationEnd: {
      EventType: 'AnimationEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    animationIteration: {
      EventType: 'AnimationEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    // Transition Events
    transitionEnd: {
      EventType: 'TransitionEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    // pointer events
    pointerOver: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    pointerEnter: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    pointerDown: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    pointerMove: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    pointerUp: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    pointerCancel: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: true, cancelable: false},
    },
    pointerOut: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: true, cancelable: true},
    },
    pointerLeave: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    gotPointerCapture: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
    lostPointerCapture: {
      EventType: 'PointerEvent',
      defaultInit: {bubbles: false, cancelable: false},
    },
  };

  const eventAliasMap = {
    doubleClick: 'dblClick',
  };

  function fireEvent(element, event) {
    if (!event) {
      throw new Error(`Unable to fire an event - please provide an event object.`);
    }
    if (!element) {
      throw new Error(
        `Unable to fire a "${event.type}" event - please provide a DOM element.`
      );
    }
    return element.dispatchEvent(event);
  }

  const createEvent = {};

  Object.keys(eventMap).forEach(key => {
    const {EventType, defaultInit} = eventMap[key];
    const eventName = key.toLowerCase();

    createEvent[key] = (node, init) => {
      if (!node) {
        throw new Error(
          `Unable to fire a "${key}" event - please provide a DOM element.`
        );
      }
      const eventInit = {...defaultInit, ...init};
      const {target: {value, files, ...targetProperties} = {}} = eventInit;
      if (value !== undefined) {
        setNativeValue(node, value);
      }
      if (files !== undefined) {
        // input.files is a read-only property so this is not allowed:
        // input.files = [file]
        // so we have to use this workaround to set the property
        Object.defineProperty(node, 'files', {
          configurable: true,
          enumerable: true,
          writable: true,
          value: files,
        });
      }
      Object.assign(node, targetProperties);
      const window = getWindowFromNode(node);
      const EventConstructor = window[EventType] || window.Event;
      return new EventConstructor(eventName, eventInit);
    };

    fireEvent[key] = (node, init) => fireEvent(node, createEvent[key](node, init));
  });

  function getWindowFromNode(node) {
    // istanbul ignore next I'm not sure what could cause the final else so we'll leave it uncovered.
    if (node.defaultView) {
      // node is document
      return node.defaultView;
    } else if (node.ownerDocument && node.ownerDocument.defaultView) {
      // node is a DOM node
      return node.ownerDocument.defaultView;
    } else if (node.window) {
      // node is window
      return node.window;
    } else {
      // no idea...
      throw new Error(
        `Unable to find the "window" object for the given node. fireEvent currently supports firing events on DOM nodes, document, and window. Please file an issue with the code that's causing you to see this error: https://github.com/testing-library/dom-testing-library/issues/new`
      );
    }
  }

  // function written after some investigation here:
  // https://github.com/facebook/react/issues/10135#issuecomment-401496776
  function setNativeValue(element, value) {
    const {set: valueSetter} =
      Object.getOwnPropertyDescriptor(element, 'value') || {};
    const prototype = Object.getPrototypeOf(element);
    const {set: prototypeValueSetter} =
      Object.getOwnPropertyDescriptor(prototype, 'value') || {};
    if (prototypeValueSetter && valueSetter !== prototypeValueSetter) {
      prototypeValueSetter.call(element, value);
    } /* istanbul ignore next (I don't want to bother) */ else if (valueSetter) {
      valueSetter.call(element, value);
    } else {
      throw new Error('The given element does not have a value setter');
    }
  }

  Object.keys(eventAliasMap).forEach(aliasKey => {
    const key = eventAliasMap[aliasKey];
    fireEvent[aliasKey] = (...args) => fireEvent[key](...args);
  });


  function wait(time) {
    return new Promise(function (resolve) {
      setTimeout(() => resolve(), time);
    });
  }

  function findTagInParents(element, tagName) {
    if (element.parentNode == null) return undefined;
    if (element.parentNode.tagName === tagName) return element.parentNode;
    return findTagInParents(element.parentNode, tagName);
  }

  function clickLabel(label) {
    fireEvent.mouseOver(label);
    fireEvent.mouseMove(label);
    fireEvent.mouseDown(label);
    fireEvent.mouseUp(label);

    if (label.htmlFor) {
      const input = document.getElementById(label.htmlFor);
      input.focus();
      fireEvent.click(label);
    } else {
      const input = label.querySelector("input,textarea,select");
      input.focus();
      label.focus();
      fireEvent.click(label);
    }
  }

  function clickBooleanElement(element) {
    if (element.disabled) return;

    fireEvent.mouseOver(element);
    fireEvent.mouseMove(element);
    fireEvent.mouseDown(element);
    fireEvent.mouseUp(element);
    fireEvent.click(element);
  }

  function clickElement(element) {
    fireEvent.mouseOver(element);
    fireEvent.mouseMove(element);
    fireEvent.mouseDown(element);
    element.focus();
    fireEvent.mouseUp(element);
    fireEvent.click(element);

    const labelAncestor = findTagInParents(element, "LABEL");
    labelAncestor && clickLabel(labelAncestor);
  }

  function dblClickElement(element) {
    fireEvent.mouseOver(element);
    fireEvent.mouseMove(element);
    fireEvent.mouseDown(element);
    element.focus();
    fireEvent.mouseUp(element);
    fireEvent.click(element);
    fireEvent.mouseDown(element);
    fireEvent.mouseUp(element);
    fireEvent.click(element);
    fireEvent.dblClick(element);

    const labelAncestor = findTagInParents(element, "LABEL");
    labelAncestor && clickLabel(labelAncestor);
  }

  function dblClickCheckbox(checkbox) {
    fireEvent.mouseOver(checkbox);
    fireEvent.mouseMove(checkbox);
    fireEvent.mouseDown(checkbox);
    fireEvent.mouseUp(checkbox);
    fireEvent.click(checkbox);
    fireEvent.mouseDown(checkbox);
    fireEvent.mouseUp(checkbox);
    fireEvent.click(checkbox);
  }

  function selectOption(select, option) {
    fireEvent.mouseOver(option);
    fireEvent.mouseMove(option);
    fireEvent.mouseDown(option);
    fireEvent.focus(option);
    fireEvent.mouseUp(option);
    fireEvent.click(option);

    option.selected = true;

    fireEvent.change(select);
  }

  function fireChangeEvent(event) {
    fireEvent.change(event.target);
    event.target.removeEventListener("blur", fireChangeEvent);
  }

 /* jshint -W034 */


  const userEvent = {
    click(element) {
      const focusedElement = element.ownerDocument.activeElement;
      const wasAnotherElementFocused =
        focusedElement !== element.ownerDocument.body &&
        focusedElement !== element;
      if (wasAnotherElementFocused) {
        fireEvent.mouseMove(focusedElement);
        fireEvent.mouseLeave(focusedElement);
      }

      switch (element.tagName) {
        case "LABEL":
          clickLabel(element);
          break;
        case "INPUT":
          if (element.type === "checkbox" || element.type === "radio") {
            clickBooleanElement(element);
            break;
          } /* falls through */
        default:
          clickElement(element);
      }

      wasAnotherElementFocused && focusedElement.blur();
    },

    dblClick(element) {
      const focusedElement = document.activeElement;
      const wasAnotherElementFocused =
        focusedElement !== document.body && focusedElement !== element;
      if (wasAnotherElementFocused) {
        fireEvent.mouseMove(focusedElement);
        fireEvent.mouseLeave(focusedElement);
      }

      switch (element.tagName) {
        case "INPUT":
          if (element.type === "checkbox") {
            dblClickCheckbox(element);
            break;
          } /* falls through */
        default:
          dblClickElement(element);
      }

      wasAnotherElementFocused && focusedElement.blur();
    },

    selectOptions(element, values) {
      const focusedElement = document.activeElement;
      const wasAnotherElementFocused =
        focusedElement !== document.body && focusedElement !== element;
      if (wasAnotherElementFocused) {
        fireEvent.mouseMove(focusedElement);
        fireEvent.mouseLeave(focusedElement);
      }

      clickElement(element);

      const valArray = Array.isArray(values) ? values : [values];
      const selectedOptions = Array.from(element.children).filter(
        opt => opt.tagName === "OPTION" && valArray.includes(opt.value)
      );

      if (selectedOptions.length > 0) {
        if (element.multiple) {
          selectedOptions.forEach(option => selectOption(element, option));
        } else {
          selectOption(element, selectedOptions[0]);
        }
      }

      wasAnotherElementFocused && focusedElement.blur();
    },

    async type(element, text, userOpts = {}) {
      if (element.disabled) return;
      const defaultOpts = {
        allAtOnce: false,
        delay: 0
      };
      const opts = Object.assign(defaultOpts, userOpts);
      if (opts.allAtOnce) {
        if (element.readOnly) return;
        fireEvent.input(element, { target: { value: text } });
      } else {
        let actuallyTyped = "";
        for (let index = 0; index < text.length; index++) {
          const char = text[index];
          const key = char;
          const keyCode = char.charCodeAt(0);

          if (opts.delay > 0) await wait(opts.delay);

          const downEvent = fireEvent.keyDown(element, {
            key: key,
            keyCode: keyCode,
            which: keyCode
          });
          if (downEvent) {
            const pressEvent = fireEvent.keyPress(element, {
              key: key,
              keyCode,
              charCode: keyCode
            });
            if (pressEvent) {
              actuallyTyped += key;
              if (!element.readOnly)
                fireEvent.input(element, {
                  target: {
                    value: actuallyTyped
                  },
                  bubbles: true,
                  cancelable: true
                });
            }
          }

          fireEvent.keyUp(element, {
            key: key,
            keyCode: keyCode,
            which: keyCode
          });
        }
      }
      element.addEventListener("blur", fireChangeEvent);
    },

    tab({ shift = false } = {}) {
      const focusableElements = document.querySelectorAll(
        "input, button, select, textarea, a[href], [tabindex]"
      );
      const list = Array.prototype.filter
        .call(focusableElements, function (item) {
          return item.getAttribute("tabindex") !== "-1";
        })
        .sort((a, b) => {
          const tabIndexA = a.getAttribute("tabindex");
          const tabIndexB = b.getAttribute("tabindex");
          return tabIndexA < tabIndexB ? -1 : tabIndexA > tabIndexB ? 1 : 0;
        });
      const index = list.indexOf(document.activeElement);

      let nextIndex = shift ? index - 1 : index + 1;
      let defaultIndex = shift ? list.length - 1 : 0;

      const next = list[nextIndex] || list[defaultIndex];

      if (next.getAttribute("tabindex") === null) {
        next.setAttribute("tabindex", "0"); // jsdom requires tabIndex=0 for an item to become 'document.activeElement' (the browser does not)
        next.focus();
        next.removeAttribute("tabindex"); // leave no trace. :)
      } else {
        next.focus();
      }
    }
  };
