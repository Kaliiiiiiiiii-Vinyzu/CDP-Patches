function ensure_no_bot(click_elem = document.documentElement) {
    var callback
    const _promise = new Promise((resolve, reject) => {
        callback = resolve
    });
    const on_click = async function(e){
            var is_bot = (e.pageY == e.screenY && e.pageX == e.screenX)
            if (is_bot && 1 >= outerHeight - innerHeight){ // fullscreen
                is_bot = false
            }
            callback(is_bot)
        } 
    click_elem.removeEventListener("mousedown", self)
    click_elem.addEventListener("mousedown", on_click)
    return _promise
}