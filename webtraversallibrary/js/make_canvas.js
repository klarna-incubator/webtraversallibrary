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

function makeCanvas(onViewport) {
    let canvas = document.createElement('canvas');

    if (onViewport) {
        canvas.style.position = 'fixed';
        canvas.style.zIndex = 999999;
        canvas.id = 'webtraversallibrary-viewport';
    } else {
        canvas.style.position = 'absolute';
        canvas.style.zIndex = 999998;
        canvas.id = 'webtraversallibrary-page';
    }

    canvas.style.pointerEvents = 'none';
    canvas.style.left = 0;
    canvas.style.top = 0;
    canvas.width = window.innerWidth;
    canvas.height = Math.max(
        document.documentElement.clientHeight,
        document.documentElement.offsetHeight,
        document.documentElement.scrollHeight
    );

    return canvas;
}

let pageCanvas = document.querySelector('canvas#webtraversallibrary-page');
if (pageCanvas === null) {
    pageCanvas = makeCanvas(onViewport=false);
    document.body.append(pageCanvas);
}

let viewportCanvas = document.querySelector('canvas#webtraversallibrary-viewport');
if (viewportCanvas === null) {
    viewportCanvas = makeCanvas(onViewport=true);
    document.body.append(viewportCanvas);
}
