# Input

## Concept: Input Domain Leaks

Bypass CDP-Leaks in [Input](https://chromedevtools.github.io/devtools-protocol/tot/Input/) domains.\
For an interaction event _`e`_, the page coordinates won't ever equal the screen coordinates, unless Chrome is in full-screen. \
However, all CDP input commands just set it the same by default (see [crbug#1477537](https://bugs.chromium.org/p/chromium/issues/detail?id=1477537)).\


```javascript
var is_bot = (e.pageY == e.screenY && e.pageX == e.screenX)
if (is_bot && 1 >= outerHeight - innerHeight){ // fullscreen
    is_bot = false
}
```



***

{% hint style="warning" %}
#### Because Chrome does not recognize Input Events to specific tabs, these methods can only be used on the active tab.&#x20;

#### Chrome Tabs do have their own process with a process id (PID), but these can not be controlled using Input Events as they´re just engines.
{% endhint %}

{% hint style="warning" %}
#### Pressing SHIFT or CAPSLOCK manually on Windows affects `input.type(text)` as well.&#x20;
{% endhint %}

***

**Owner**: [Vinyzu](https://github.com/Vinyzu/)\
**Co-Maintainer**: [Kaliiiiiiiiii](https://github.com/kaliiiiiiiiii/)



