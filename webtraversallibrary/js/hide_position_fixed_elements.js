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

class Rectangle {
    constructor(x1, y1, x2, y2) {
        this.minX = Math.min(x1, x2);
        this.maxX = Math.max(x1, x2);
        this.minY = Math.min(y1, y2);
        this.maxY = Math.max(y1, y2);
    }
    get area() {
        return (this.maxX - this.minX) * (this.maxY - this.minY);
    }
    get isDegenerate() {
        return this.area === 0;
    }
    get isEmpty() {
        return Object.is(this, Rectangle.EMPTY);
    }
    equals(other) {
        if (other instanceof Rectangle) {
            return other.minX === this.minX && other.maxX === this.maxX && other.minY === this.minY && other.maxY === this.maxY;
        }
        return false;
    }
    static intersection(p, q) {
        const maxX = Math.min(p.maxX, q.maxX);
        const minX = Math.max(p.minX, q.minX);
        const maxY = Math.min(p.maxY, q.maxY);
        const minY = Math.max(p.minY, q.minY);
        if (maxX < minX || maxY < minY) {
            return Rectangle.EMPTY;
        }
        return new Rectangle(minX, minY, maxX, maxY);
    }
    static fromDOMRect(domRect) {
        return new Rectangle(domRect.top, domRect.right, domRect.bottom, domRect.left);
    }
}

Rectangle.EMPTY = new Rectangle(0, 0, 0, 0);

class UidGenerator {
    constructor() {
        this.currentUid = 0;
    }
    next() {
        return this.currentUid++;
    }
}

let uidGenerator = new UidGenerator();

let hideAllObstructingElements = (interestingElements) => {
    let hiddenElementStates = {};
    Array.from(document.documentElement.querySelectorAll("*"))
        .filter(element => {
            return interestingElements.some(interestingElement => {
                if (!(element instanceof HTMLElement)) {
                    return false;
                }
                let fstRect = Rectangle.fromDOMRect(element.getBoundingClientRect());
                let sndRect = Rectangle.fromDOMRect(interestingElement.getBoundingClientRect());
                const isConflicting = !Rectangle.intersection(fstRect, sndRect).isDegenerate;
                // don't hide element if it contains an interesting element
                return isConflicting && !interestingElements.some(interEl => Array.from(element.querySelectorAll("*")).filter(x => x instanceof HTMLElement).includes(interEl)) && element !== interestingElement;
            });
        })
        .forEach(element => {
            if (element.getAttribute("wtl-hidden-uid") === null) {
                element.setAttribute("wtl-hidden-uid", uidGenerator.next());
            }
            const uid = element.getAttribute("wtl-hidden-uid");
            hiddenElementStates[uid] = element.hidden;
            element.hidden = true;
        });
    return hiddenElementStates;
};

let hideFixedElements = (interestingElementSelectors = []) => {
    let interestingElements = Array.from(interestingElementSelectors)
        .map(css => document.querySelector(css))
        .filter(x => x instanceof HTMLElement);
    return hideAllObstructingElements(interestingElements);
};

return hideFixedElements(arguments[0]);
