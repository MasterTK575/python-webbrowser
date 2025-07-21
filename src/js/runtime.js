console = {
    log: function (msg) {
        call_python("log", msg);
    }
}

document = {
    querySelectorAll: function (s) {
        var handles = call_python("querySelectorAll", s);
        return handles.map(function (h) {
            return new Node(h)
        });
    }
}

function Node(handle) {
    this.handle = handle;
}

Node.prototype.getAttribute = function (attr) {
    return call_python("getAttribute", this.handle, attr);
}

LISTENERS = {}

Node.prototype.addEventListener = function (type, listener) {
    if (!LISTENERS[this.handle]) LISTENERS[this.handle] = {};
    var dict = LISTENERS[this.handle];
    if (!dict[type]) dict[type] = [];
    var list = dict[type];
    list.push(listener);
}

Node.prototype.dispatchEvent = function (evt) {
    var type = evt.type;
    var handle = this.handle;
    var listeners = (LISTENERS[handle] && LISTENERS[handle][type]) || [];
    for (var i = 0; i < listeners.length; i++) {
        listeners[i].call(this, evt);  // set this to the node that the event was generated on
    }
    return evt.do_default;  // has call() prevented default on evt?
}

Object.defineProperty(Node.prototype, 'innerHTML', {
    set: function (s) {
        call_python("innerHTML_set", this.handle, s.toString());
    }
})

function Event(type) {
    this.type = type
    this.do_default = true;
}

Event.prototype.preventDefault = function () {
    this.do_default = false;
}

function XMLHttpRequest() {
}

XMLHttpRequest.prototype.open = function (method, url, is_async) {
    if (is_async) throw Error("Asynchronous XHR is not supported");
    this.method = method;
    this.url = url;
}

XMLHttpRequest.prototype.send = function (body) {
    this.responseText = call_python("XMLHttpRequest_send",
        this.method, this.url, body);
}