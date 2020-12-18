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

// setup
function asArray(something) {
    return [].slice.call(something);
}

let createCustomAttribute = (name, value) => {
    // Note: .setAttribute is cleaner but doesn't always work on iframe elements
    let attr = document.createAttribute(name);
    attr.value = value;
    return attr;
};

Array.prototype.flatMap = function (lambda) {
    return Array.prototype.concat.apply([], this.map(lambda));
};

function isFixedPos(el) {
    do {
        const computedStyle = window.getComputedStyle(el);
        const position = computedStyle.getPropertyValue('position');
        if (position === 'fixed' || position === 'sticky') return true;
        el = el.parentElement;
    } while (el);
    return false;
}

function extractMetadata(el) {
    const svgChildren = asArray(el.getElementsByTagName('svg'));
    const imgChildren = asArray(el.getElementsByTagName('img'));
    const imgSvgChildren = imgChildren.filter(ch => ch.src && ch.src.endsWith(".svg"));
    const computedStyle = window.getComputedStyle(el);
    const boundingBox = el.getBoundingClientRect();

    return {
        id: el.getAttribute('id'),
        tag: el.tagName.toLowerCase(),
        'class': el.getAttribute('class'),
        attributes: Object.fromEntries(Array.from(el.attributes).map(x => [x.name, x.value])),
        type: el.getAttribute('type'),
        href: el.getAttribute('href'),
        size: {
            width: boundingBox.width,
            height: boundingBox.height
        },
        location: {
            x: boundingBox.left + window.scrollX,
            y: boundingBox.top + window.scrollY
        },
        text: (el.tagName.toLowerCase() == 'input' ? el.value : el.innerText),
        text_local: Array.from(el.childNodes).filter(childEl => childEl instanceof Text).map(textEl=>textEl.textContent).join("").trim(),
        children_count: el.childElementCount,
        num_imgs: imgChildren.length - imgSvgChildren.length,
        num_svgs: svgChildren.length + imgSvgChildren.length + (el.tagName.toLowerCase() === 'svg'),
        background: computedStyle.getPropertyValue('background'),
        background_image: computedStyle.getPropertyValue('background-image'),
        // not enough to just check the computedStyle for "position" because it doesn't take into account
        // parent elements
        fixed_pos: isFixedPos(el),
        wtl_uid: parseInt(el.getAttribute('wtl-uid')),
        wtl_parent_uid: parseInt(el.getAttribute('wtl-parent-uid')),
        display: computedStyle.getPropertyValue("display"),
        visibility: computedStyle.getPropertyValue("visibility"),
        font_weight: computedStyle.getPropertyValue("font-weight"),
        font_size: computedStyle.getPropertyValue("font-size")
    };
}

document.body.setAttribute('wtl-uid', 0);
document.body.setAttribute('wtl-parent-uid', -1);

//Hack to make sure we do not assign a wtl-uid twice
let latestWTLUid = Math.max(
    ...asArray(document.querySelectorAll('*'))
        .map(element => element.hasAttribute('wtl-uid') ?
                        parseInt(element.getAttribute('wtl-uid')) :
                        0)
);

let res = [extractMetadata(document.body)];
let toVisit = asArray(document.body.children);

while (toVisit.length > 0) {
    const el = toVisit.pop();
    if (!el.hasAttribute('wtl-uid')) {
        el.attributes.setNamedItem(createCustomAttribute('wtl-uid', ++latestWTLUid));
        el.attributes.setNamedItem(createCustomAttribute('wtl-parent-uid', el.parentElement.getAttribute('wtl-uid')));
    }
    const elementMetadata = extractMetadata(el);
    res.push(elementMetadata);
    toVisit = asArray(el.children).reverse().concat(toVisit);
}

return res;
