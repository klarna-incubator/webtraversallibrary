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

let getEventListenerElements = function () {
    let allElements = document.querySelectorAll('*');
    return Array.prototype.slice.call(allElements)
        .filter(function (element) {
            return typeof (element.eventListenerList) !== 'undefined';
        });
};

let getHTMLInteractableElements = function () {
    let getElementsByTagName = function (tagName) {
        return Array.from(document.getElementsByTagName(tagName));
    };
    let interactableTagNames = [
        'a',
        'button',
        'select',
        'input',
        'label'
    ];
    let interactableElements = [];
    interactableTagNames.forEach(function (tagName) {
        interactableElements.push.apply(interactableElements, getElementsByTagName(tagName));
    });
    return interactableElements;
};

let inputButtons = ["button", "submit", "reset", "image"];
let unclickableTags = ["form", "body", "nav", "aside"];

function isHidden(element) {
    let rect = element.getBoundingClientRect();
    let style = window.getComputedStyle(element);

    return element.offsetParent == null ||
        element.offsetWidth === 0 ||
        element.offsetHeight === 0 ||
        rect.width === 0 ||
        rect.height === 0 ||
        style.visibility === "hidden" ||
        style.display === "none" ||
        element.hidden ||
        element.getAttribute("aria-hidden") === "true";
}

function isActive(element, input_fields, active_elements) {

    let tag = element.tagName.toLowerCase();

    // EXPLICIT EXCLUSION RULES

    // Invisible/inaccessible elements can't be clickable
    if (isHidden(element)) {
        return false;
    }

    // Can't have active elements with no ID!
    if (element.getAttribute("wtl-uid") == null) {
        return false;
    }

    if (active_elements.length === 0)
        return false;

    if (active_elements.includes(element) || input_fields.includes(element) ) {
        return true;
    }

    // Tag is explicitly prohibited to be selected
    if (unclickableTags.indexOf(tag) !== -1) {
        return false;
    }

    // Consciously exclude the non-button inputs (forms etc.)
    let typeAttr = element.getAttribute("type");
    if (tag === "input" && typeAttr != null && inputButtons.indexOf(typeAttr) === -1) {
        return false;
    }

    // ELEMENT INCLUSION RULES

    // Check for event listeners with jQuery (if it's available and can provide _data)
    if (window.jQuery && jQuery != null && jQuery._data != null && typeof(jQuery._data) === 'function') {
        let event_data = jQuery._data(element, "events");
        if (event_data != null && event_data.click) {
            return true;
        }
    }

    // Check for the normal onClick stuff
    if (typeof element.onclick === "function") {
        return true;
    }

    // Check for explicit buttons
    if (tag === "button") {
        return true;
    }

    // Check for button inputs
    if (tag === "input" && inputButtons.indexOf(element.getAttribute("type")) !== -1) {
        return true;
    }

    // Check for remaining "a" tags with href
    if (tag === "a" && element.getAttribute("href") != null) {
        return true;
    }

    return false;
}

let isHiddenByOverflow = function(child) {
    let parent = child.parentElement;

    if (child.offsetHeight == parent.offsetHeight && child.offsetWidth == parent.offsetWidth) {
        return false;
    }

    let style = window.getComputedStyle(parent);
    let rect = parent.getBoundingClientRect();

    return !((style.overflowX === 'visible' || child.offsetLeft < rect.width) &&
        (style.overflowY === 'visible' || child.offsetTop < rect.height));
};

// Recursively search for visible elements that are interactable
function findActiveElements(element, result, input_fields, clickable_elements) {
    if (!element.tagName) {
        // Skip strings, comments, cdatas etc.
        return;
    }

    // Only elements with wtl-uid are of interest
    let wtl_uid = parseInt(element.getAttribute('wtl-uid'));
    if (wtl_uid !== null && isActive(element, clickable_elements, input_fields) === true) {
        result.push(wtl_uid);
    }

    // "aria-hidden" indicates that the entire subtree should be hidden
    if (element.getAttribute("aria-hidden") === "true") {
        // Skip the whole subtree
        return;
    }

    // Another indirect way to hide child elements is by setting overflow to hidden or scroll
    // This seems to require more complicated logic to work in the general case; revisit later if needed

    element.childNodes.forEach(function(child) {
        if (!isHiddenByOverflow(child)) {
            findActiveElements(child, result, input_fields, clickable_elements);
        }
    });
}

let res = [];
let inputs = getHTMLInteractableElements();
let listen = getEventListenerElements();

findActiveElements(document.documentElement, res, inputs, listen);

return res;
