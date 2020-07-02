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

// Disable jQuery animation
if (document.jQuery) {
    $.fx.off = true;
}

// CSS to disable CSS animation
let disableAnimationCssStyles = `*, *:before, *:after {
    transition-property: none !important;
    transition-duration: 0s !important;
    
    transform: none !important;
    transform-duration: 0s !important;
    
    animation: none !important;
    animation-name: none !important;
    animation-duration: 0s !important;
}`;

// attach CSS to the page
let styleEl = document.createElement('style');
styleEl.type = 'text/css';
styleEl.textContent = disableAnimationCssStyles;
document.head.appendChild(styleEl);