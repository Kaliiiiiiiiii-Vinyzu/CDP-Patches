# Concept Input Domains

### the leak
for a interaction event `e`, the page cordinates won't ever equal the screen cordinates, unless Chrome is in fullscreen.
Howerver, all `CDP` input commands just set it the same by default (see [crbug#1477537](https://bugs.chromium.org/p/chromium/issues/detail?id=1477537))
```js
var is_bot = (e.pageY == e.screenY && e.pageX == e.screenX)
if (is_bot && 1 >= outerHeight - innerHeight){ // fullscreen
    is_bot = false
}
```

As we don't want to patch Chromium itsself, let's just dispatch this event at OS-level

### the patch
As we need to send key events to specific tabs, we have to go low-level
#### Windows
This should be possible with `ctypes`
see [example script](https://stackoverflow.com/a/63661354/20443541)

#### Linux
should be possible using [python-libxdo](https://pypi.org/project/python-libxdo/)
see [example-script](https://stackoverflow.com/a/47424799/20443541)

### Roadmap
- [ ] sample script single mousedown
    - [ ] Windows
    - [ ] Linux
- [ ] functions for finding tab windows by PID
    - [ ] Windows
    - [ ] Linux
- [ ] create async low-level classes for specific windows
    - [ ] Windows
        - [ ] `BasePointer`
            - [ ] mousemove
            - [ ] mousedown
            - [ ] mouseup
            - [ ] scroll
        - [ ] `BaseKeyBoard`
            - [ ] single keys
            - [ ] key combos
        - [ ] `BaseTouch` (multiple touchpoints => instances possible)
            - [ ] touchdown
            - [ ] touchmove
            - [ ] touchup
    - [ ] Linux
        - [ ] `BasePointer`
            - [ ] mousemove
            - [ ] mousedown
            - [ ] mouseup
            - [ ] scroll
        - [ ] `BaseKeyBoard`
            - [ ] single keys
            - [ ] key combos
        - [ ] `BaseTouch` (multiple touchpoints => instances possible)
            - [ ] touchdown
            - [ ] touchmove
            - [ ] touchup
- [ ] async higher level classes (randomized wit biases, human-like)
    - [ ] Mousemove (path)
    - [ ] click (random timeouts)
    - [ ] doubble click (random timeouts)
    - [ ] scroll to (path)
    - [ ] click inside rect (bias towards middle)
    - [ ] zoom//pinch (touch)
    - [ ] scroll (touch)
    - [ ] write multple keys (random timeouts)
    - [ ] drag
- [ ] make a package & release

# Runtime.enable patch concept
adding soon