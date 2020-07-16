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

const [x, rawY, color, size, text, background, backgroundAlpha, onViewport] = arguments;

const canvas_selector = onViewport ? 'canvas#webtraversallibrary-viewport' : 'canvas#webtraversallibrary-page';
let canvas = document.querySelector(canvas_selector);
let ctx = canvas.getContext("2d");
ctx.save();
ctx.font = size + "px sans-serif";
ctx.textBaseline = 'top';

const padding = 15;
const y = rawY + (onViewport ? 0 : window.scrollY);
const width = ctx.measureText(text).width;
const height = parseInt(ctx.font, 10);

// Draw shadow
ctx.globalAlpha = 0.25 * backgroundAlpha;
ctx.fillStyle = '#000';
ctx.fillRect(
    x + 5 - padding,
    y + 5 - padding,
    width + 2 * padding,
    height + 2 * padding
);

// Draw box
ctx.globalAlpha = backgroundAlpha;
ctx.fillStyle = background;
ctx.fillRect(
    x - padding,
    y - padding,
    width + 2 * padding,
    height + 2 * padding
);

// Draw border
ctx.fillStyle = '#000';
ctx.strokeRect(
    x - padding,
    y - padding,
    width + 2 * padding,
    height + 2 * padding
);

// Draw text
ctx.globalAlpha = 1.0;
ctx.fillStyle = color;
ctx.fillText(text, x, y);
ctx.restore();
