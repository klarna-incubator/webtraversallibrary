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

(function() {
    Element.prototype._addEventListener = Element.prototype.addEventListener;
    Element.prototype.addEventListener = function(a,b,c) {
        if(c==undefined)
            c=false;
        this._addEventListener(a,b,c);
        if(!this.eventListenerList)
            this.eventListenerList = {};
        if(!this.eventListenerList[a])
            this.eventListenerList[a] = [];
        this.eventListenerList[a].push({listener:b,useCapture:c});
    };

    Element.prototype.getEventListeners = function(a){
        if(!this.eventListenerList)
            this.eventListenerList = {};
        if(a==undefined)
            return this.eventListenerList;
        return this.eventListenerList[a];
    };
    Element.prototype.clearEventListeners = function(a){
        if(!this.eventListenerList)
            this.eventListenerList = {};
        if(a==undefined){
            for(let x in (this.getEventListeners())) this.clearEventListeners(x);
            return;
        }
        let el = this.getEventListeners(a);
        if(el==undefined)
            return;
        for(let i = el.length - 1; i >= 0; --i) {
            let ev = el[i];
            this.removeEventListener(a, ev.listener, ev.useCapture);
        }
    };

    Element.prototype._removeEventListener = Element.prototype.removeEventListener;
    Element.prototype.removeEventListener = function(a,b,c) {
        if(c==undefined)
            c=false;
        this._removeEventListener(a,b,c);
        if(!this.eventListenerList)
            this.eventListenerList = {};
        if(!this.eventListenerList[a])
            this.eventListenerList[a] = [];

        // Find the event in the list
        for(let i=0;i<this.eventListenerList[a].length;i++){
            if(this.eventListenerList[a][i].listener==b, this.eventListenerList[a][i].useCapture==c){ // Hmm..
                this.eventListenerList[a].splice(i, 1);
                break;
            }
        }
        if(this.eventListenerList[a].length==0)
            delete this.eventListenerList[a];
    };
})();