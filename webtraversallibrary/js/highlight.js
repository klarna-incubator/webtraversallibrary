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

function findBbox(tag, onViewport) {
  let bbox = tag.getBoundingClientRect();
  if (bbox.width * bbox.height > 0) {
    return new DOMRect(
      bbox.x,
      bbox.y + (onViewport ? 0 : window.scrollY),
      bbox.width,
      bbox.height
    );
  }
  return findBbox(tag.parentElement);
}

function highlight(tag, color, intensity, canvas, fill, onViewport) {
  let bbox = findBbox(tag, onViewport);
  let ctx = canvas.getContext('2d');
  ctx.globalAlpha = intensity;
  if (fill === true) {
    ctx.fillRect(bbox.x, bbox.y, bbox.width, bbox.height);
  } else {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 5 * intensity;
    ctx.rect(bbox.x, bbox.y, bbox.width, bbox.height);
    ctx.stroke();
    ctx.closePath();
  }
  ctx.globalAlpha = 1.0;
}

const [selector, color, intensity, fill, onViewport] = arguments;
const canvas_selector = onViewport ? 'canvas#webtraversallibrary-viewport' : 'canvas#webtraversallibrary-page';
let canvas = document.querySelector(canvas_selector);

let element = document.querySelector(selector);
if (element !== null) {
    highlight(element, color, intensity, canvas, fill, onViewport);
} else {
    console.error('Element not found with selector: ', selector);
}
