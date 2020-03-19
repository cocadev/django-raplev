! function() {
    "use strict";
    window.Collapse = function() {}, Collapse.prototype.listen = function() {
        document.addEventListener("click", this._initialize.bind(this))
    }, Collapse.prototype._initialize = function(e) {
        for (var t, n, i = e.target;;) {
            if (!i) return;
            if (i.classList.contains("js-collapse-trigger")) return e.preventDefault(), n = i, t = document.querySelectorAll(n.getAttribute("data-target")), void this._handle(n, t);
            i = i.parentElement
        }
    }, Collapse.prototype._handle = function(e, t) {
        var n, i = this._getDuration(t[0]);
        if (!e.classList.contains("pending")) {
            e.classList.add("pending"), setTimeout((function() {
                e.classList.remove("pending")
            }), i);
            for (var s = 0; s < t.length; s++) n = t[s], e.classList.contains("is-active") ? this._slideUp(n) : this._slideDown(n);
            e.classList.toggle("is-active")
        }
    }, Collapse.prototype._slideDown = function(e) {
        var t, n = e.style,
            i = this._getStyle(e, "padding-top"),
            s = this._getStyle(e, "padding-bottom"),
            r = this._getDuration(e);
        n.overflow = "hidden", n.display = "block", t = e.offsetHeight, n.transition = "none", n.height = "0", n.paddingTop = "0", n.paddingBottom = "0", setTimeout((function() {
            n.transition = "", n.height = t + "px", n.paddingTop = i + "px", n.paddingBottom = s + "px", setTimeout((function() {
                n.overflow = ""
            }), r)
        }), 10)
    }, Collapse.prototype._slideUp = function(e) {
        var t = e.style,
            n = this._getDuration(e);
        t.overflow = "hidden", t.height = "0", t.paddingTop = "0", t.paddingBottom = "0", setTimeout((function() {
            e.removeAttribute("style")
        }), n)
    }, Collapse.prototype._getDuration = function(e) {
        return 1e3 * parseFloat(getComputedStyle(e).transitionDuration)
    }, Collapse.prototype._getStyle = function(e, t) {
        var n = getComputedStyle(e)[t];
        return parseFloat(n)
    }
}();
var collapse = new Collapse;

function Dropdown(e) {
    "use strict";
    var t = document.querySelector(e.button),
        n = document.querySelector(e.dropdown),
        i = e.multiple || !1;
    Dropdown.isActive = !1, Dropdown.isEnabled = !0, this.open = function() {
        i && (Dropdown.isEnabled = !1), n.classList.contains("is-active") && Dropdown.isEnabled ? this.close() : !i && Dropdown.isActive || (Dropdown.isActive = !0, n.style.display = "block", setTimeout((function() {
            n.classList.add("is-active"), t.classList.add("is-active")
        }), 30))
    }, this.close = function() {
        i || (Dropdown.isActive = !1), Dropdown.isEnabled = !0, n.classList.remove("is-active"), setTimeout(function() {
            n.style.display = "", t.classList.remove("is-active")
        }.bind(this), this._getDuration(n))
    }, this._getDuration = function(e) {
        return 1e3 * parseFloat(getComputedStyle(e).transitionDuration)
    }
}
collapse.listen();
var userMenu = new Dropdown({
        button: ".js-user-menu-trigger",
        dropdown: ".js-user-menu-target"
    }),
    login = new Dropdown({
        button: ".js-login-trigger",
        dropdown: ".js-login-target"
    }),
    register = new Dropdown({
        button: ".js-register-trigger",
        dropdown: ".js-register-target"
    }),
    forgotPW = new Dropdown({
        button: ".js-forgot-pwd-trigger",
        dropdown: ".js-forgot-pwd-target",
        multiple: !0
    }),
    support = new Dropdown({
        button: ".js-support-trigger",
        dropdown: ".js-support-target"
    }),
    twoFactorAuth = new Dropdown({
        button: ".js-two-factor-auth-trigger",
        dropdown: ".js-two-factor-auth-target"
    });

function switchToLogin(e) {
    e = e || 300, register.close(), setTimeout((function() {
        login.open()
    }), e)
}

function switchToRegister(e) {
    e = e || 300, login.close(), setTimeout((function() {
        register.open()
    }), e)
}

function ScrollButton(e) {
    "use strict";
    var t = document.querySelector(e.button);

    function n() {
        var t, i = -e.step || -100;
        0 != document.documentElement.scrollTop || 0 != document.body.scrollTop ? (window.scrollBy(0, i), t = setTimeout((function() {
            n()
        }), 10)) : clearTimeout(t)
    }
    t.onclick = n, e.threshold && window.addEventListener("scroll", (function() {
        var n = e.threshold;
        pageYOffset > n ? t.classList.add("is-active") : t.classList.remove("is-active")
    })), this.scrollUp = n
}
try {
    var scrollButton = new ScrollButton({
        button: "[data-toggle='scrollBtn']"
    })
} catch (e) {
    console.log(e.message)
}

function MobileMenu(e) {
    this._trigger = document.querySelector(e.trigger), this._targets = document.querySelectorAll(e.target), this._maxWidth = e.maxWidth
}
MobileMenu.prototype = Object.create(Collapse.prototype), MobileMenu.prototype.constructor = MobileMenu, MobileMenu.prototype._reset = function() {
    var e = window.matchMedia("(max-width:" + this._maxWidth + "px)"),
        t = this._trigger,
        n = this._targets;
    if (e.matches && this._isThrottled && (this._isThrottled = !1), !e.matches && !this._isThrottled) {
        t.classList.remove("is-active");
        for (var i = 0; i < n.length; i++) n[i].removeAttribute("style");
        this._isThrottled = !0
    }
}, MobileMenu.prototype.listen = function() {
    var e = this._trigger,
        t = this._targets;
    e.onclick = function() {
        this._handle(e, t)
    }.bind(this), window.addEventListener("resize", this._reset.bind(this))
};
var menu = new MobileMenu({
    trigger: ".js-mobile-menu-trigger",
    target: ".js-mobile-menu-target",
    maxWidth: 1340
});
try {
    menu.listen()
} catch (e) {
    console.log(e.message)
}

function handleTablist(e) {
    "use strict";
    if (!e) return;
    const t = e.querySelector(".js-tablist-triggers"),
        n = e.querySelector(".js-tablist-tabs");
    e.onclick = e => {
        e.target.closest(".js-tablist-triggers") && (e.target.matches(".is-active") || (function() {
            for (let e of n.children) e.classList.remove("is-active");
            for (let e of t.children) e.classList.remove("is-active")
        }(), function(e) {
            t.children[e].classList.add("is-active"), n.children[e].classList.add("is-active")
        }(function(e) {
            let t = e.parentElement.firstElementChild,
                n = 0;
            for (; t != e && null != t.nextElementSibling;) t = t.nextElementSibling, n++;
            return n
        }(e.target))))
    }
}

function Popup(e) {
    "use strict";
    var t;
    this.open = function() {
        (t = document.querySelector(e)).style.display = "block", setTimeout((function() {
            t.classList.add("is-active")
        }), 20)
    }, this.close = function() {
        var e = t.querySelector(".popup__container"),
            n = 1e3 * parseFloat(getComputedStyle(e).transitionDuration);
        t.classList.remove("is-active"), setTimeout(function() {
            t.style.display = ""
        }.bind(this), n)
    }
}
handleTablist(document.querySelector(".js-tablist-toggle"));
var confirmation = new Popup(".js-confirmation-toggle"),
    followLink = new Popup(".js-follow-link-toggle"),
    pwRecover = new Popup(".js-pw-recover-toggle"),
    pwRecover_2 = new Popup(".js-pw-recover-2-toggle"),
    emailActivation = new Popup(".js-email-activation-toggle"),
    withdrawFunds = new Popup(".js-withdraw-funds-toggle");

function handleMarketPrice() {
    "use strict";
    var e, t = document.querySelector("[name='useMarketPrice']"),
        n = document.querySelector("[name='trailMarketPrice']"),
        i = document.querySelector(".js-trade-price-field"),
        s = i.children[0];
    s.getAttribute("data-placeholder") ? e = s.getAttribute("data-placeholder") : s.setAttribute("data-placeholder", s.placeholder), t.checked ? (i.classList.add("is-disabled"), s.disabled = !0, s.placeholder = "Use market price for Asking Price. Value 3885 USD", n.disabled = !0) : t.checked || (i.classList.remove("is-disabled"), s.disabled = !1, n.disabled = !1, s.placeholder = e), n.checked ? (t.disabled = !0, s.placeholder = "Initial Asking Price? Price will follow market movement") : n.checked || (t.disabled = !1)
}

function Userlist() {
    "use strict";
    var e, t = document.querySelector("[data-toggle='userlist']");
    this._handle = function(n) {
        for (var i = n.target; i != t;) {
            if ("LI" == i.tagName) {
                if (i.classList.contains("is-active")) break;
                e && e.classList.remove("is-active"), i.classList.add("is-active"), e = i;
                break
            }
            i = i.parentElement
        }
    }.bind(this), t.onmousedown = function(e) {
        e.preventDefault()
    }, this.listen = function() {
        t.addEventListener("click", this._handle)
    }
}
try {
    var userlist = new Userlist;
    userlist.listen()
} catch (e) {
    console.log(e.message)
}

function UserStatus() {
    "use strict";
    var e = document.querySelector(".js-status-trigger"),
        t = document.querySelector(".js-status-target");
    this._handle = function(n) {
        for (var i = n.target;;) {
            if (i == document.body) {
                this._hide();
                break
            }
            if (i == e) {
                if (t.classList.contains("is-active")) {
                    this._hide();
                    break
                }
                this._show();
                break
            }
            i = i.parentElement
        }
    }.bind(this), this._show = function() {
        t.style.display = "block", setTimeout((function() {
            t.classList.add("is-active")
        }), 30)
    }, this._hide = function() {
        t.classList.remove("is-active"), setTimeout((function() {
            t.style.cssText = ""
        }), this._getDuration(t))
    }, this.setOnline = function() {
        this._clearState(), e.classList.add("is-online")
    }, this.setAway = function() {
        this._clearState(), e.classList.add("is-away")
    }, this.setOffline = function() {
        this._clearState(), e.classList.add("is-offline")
    }, this._clearState = function() {
        for (var t = ["is-online", "is-away", "is-offline"], n = 0; n <= t.length; n++) e.classList.remove(t[n])
    }, this._getDuration = function(e) {
        return 1e3 * parseFloat(getComputedStyle(e).transitionDuration)
    }, t.onmousedown = function(e) {
        e.preventDefault()
    }, this.listen = function() {
        document.body.addEventListener("click", this._handle)
    }
}
try {
    var userStatus = new UserStatus;
    userStatus.listen()
} catch (e) {
    console.log(e.message)
}

function Copy() {
    "use strict";
    var e = document.querySelector(".js-copy-trigger"),
        t = document.querySelector(".js-copy-target"),
        n = document.querySelector(".js-copy-message");
    this._copy = function() {
        t.focus(), t.select(), document.execCommand("Copy")
    }, this._showMessage = function() {
        n.classList.add("is-active")
    }, this.listen = function() {
        e.addEventListener("click", function() {
            this._copy(), this._showMessage()
        }.bind(this))
    }
}
var copy = new Copy;
try {
    copy.listen()
} catch (e) {
    console.log(e.message)
}

function ResultsBar() {
    "use strict";
    var e = document.querySelector(".js-results-bar");
    this.show = function() {
        e.hidden = !1, setTimeout((function() {
            e.classList.add("is-active")
        }), 20)
    }, this.hide = function() {
        e.classList.remove("is-active"), setTimeout((function() {
            e.hidden = !0
        }), 1e3 * parseFloat(getComputedStyle(e).transitionDuration))
    }
}
var resultsBar = new ResultsBar;

function removeCard() {
    "use strict";
    var e = document.getElementsByClassName("js-card-toggle"),
        t = e[0].parentElement,
        n = event.target.parentElement.parentElement;
    t.removeChild(n), e.length || (t.innerHTML = "")
}
class AlertNote {
    close(e) {
        const t = e.parentElement,
            n = this._getDuration(t);
        t.classList.add("is-hidden"), setTimeout(() => t.remove(), n)
    }
    _getDuration(e) {
        return 1e3 * parseFloat(getComputedStyle(e).transitionDuration)
    }
}
const alertNote = new AlertNote;

function handleValidation(e) {
    "use strict";
    const t = e.querySelector(".js-submit-trigger") || e.querySelector("[type='submit']"),
        n = "is-valid",
        i = "is-invalid",
        s = "form-group__message";
    let r;

    function o() {
        if (!r.disabled) {
            if (r.required) {
                if (! function() {
                        if ("INPUT" == r.tagName && "" != r.value) return !0;
                        if ("SELECT" == r.tagName) {
                            let e = r.options[r.selectedIndex];
                            if (!e.disabled && "js-select-placeholder" != e.className) return !0
                        }
                    }()) return void c("This field is required", !1);
                c("Looks good!", !0)
            }
            "" != r.value && ("name" != r.name && "name" != r.autocomplete || (a() ? c("Looks good!", !0) : c("Please enter a valid name", !1)), "last_name" != r.name && "family-name" != r.autocomplete || (a() ? c("Looks good!", !0) : c("Please enter a valid last name", !1)), "date" == r.name && (a() ? c("Looks good!", !0) : c("Please enter a valid date", !1)), "email" == r.type && (a() ? c("Looks good!", !0) : c("Please enter a valid email address", !1)), "number" == r.type && (! function() {
                const e = r.value,
                    t = +r.min || -1 / 0,
                    n = +r.max || 1 / 0;
                if ("" == e) return !0;
                if (e >= t && e <= n) return !0
            }() ? c("Please enter a valid number", !1) : c("Looks good!", !0)))
        }
    }

    function a() {
        const e = r.value;
        if ("" == e) return !0;
        if (!r.pattern) return console.log(`No HTML5 pattern found in ${r}`), !0; {
            const t = new RegExp(r.pattern),
                n = e.match(t);
            if (n && e.length == n[0].length) return !0
        }
    }

    function c(e, t) {
        const o = r.parentElement.parentElement;
        0 == t && (o.classList.add(i), o.classList.remove(n)), 1 == t && (o.classList.add(n), o.classList.remove(i)),
            function(e) {
                if (r.closest(".qs-datepicker")) return;
                const t = r.parentElement.parentElement;
                let n = t.querySelector(`.${s}`);
                n || (n = document.createElement("p"), n.className = s, t.append(n));
                n.textContent = e
            }(e)
    } ["input", "change"].forEach(t => {
        e.addEventListener(t, e => {
            r = e.target, o()
        })
    }), t.onclick = t => {
        t.preventDefault(),
            function() {
                for (let t of e.elements) "BUTTON" != t.tagName && (r = t, o());
                (function() {
                    for (let t of e.elements)
                        if (t.closest(`.${i}`)) return !1;
                    return !0
                })() && e.submit()
            }()
    }, document.addEventListener("reset", () => {
        const t = e.querySelectorAll(`.${s}`);
        for (let t of e.elements) t.classList.remove(n), t.classList.remove(i);
        for (let e of t) e.remove()
    })
}
try {
    handleValidation(document.querySelector(".js-form-toggle"))
} catch (e) {
    console.log(e.message)
}

function handleTextarea(e, t = 1 / 0) {
    if (!e) return;
    const n = e.rows || 1,
        i = parseFloat(getComputedStyle(e).fontSize);
    let s;
    e.onfocus = function() {
        s = this.scrollHeight
    }, e.oninput = function() {
        this.rows = n;
        const e = Math.ceil((this.scrollHeight - s) / (2 * i));
        this.rows = n + e < t ? n + e : t
    }
}
const expadingTextareas = document.querySelectorAll(".js-expanding-textarea");
for (let e of expadingTextareas) handleTextarea(e, 7);

function fixTextarea(e) {
    "use strict";
    var t, n, i = document.querySelector(e.element),
        s = document.querySelector(e.container),
        r = e.desktopWidth;

    function o() {
        var e = i.offsetHeight;
        ! function(e) {
            var t = document.documentElement.clientHeight + pageYOffset,
                n = e.getBoundingClientRect().top + pageYOffset;
            return t < n
        }(s) ? a(): (i.classList.add("is-fixed"), s.style.height = e + "px")
    }

    function a() {
        i.classList.remove("is-fixed"), s.style.height = ""
    }

    function c() {
        var e = document.documentElement.clientWidth;
        e < r && !t && (window.addEventListener("scroll", o), o(), t = !0, n = !1), e >= r && !n && (window.removeEventListener("scroll", o), a(), t = !1, n = !0)
    }
    i && s && (window.addEventListener("DOMContentLoaded", c), window.addEventListener("resize", c))
}

function handleTextareaLimiter() {
    "use strict";
    document.addEventListener("input", e => {
        const t = e.target;
        let n, i, s, r;
        if ("TEXTAREA" == t.tagName || t.dataset.characterCounter) {
            if (n = document.querySelector(t.dataset.characterCounter), n.dataset.limit || (n.dataset.limit = n.textContent), i = n.dataset.limit, r = t.value || t.textContent, s = function(e) {
                    let t = 0;
                    for (; e[t];) t++;
                    return t
                }(r), s > i) return r = r.slice(0, i), void(e.target.value = r);
            n.textContent = i - s
        }
    })
}
fixTextarea({
    element: ".js-fix-textarea-toggle",
    container: ".js-fix-textarea-container",
    desktopWidth: 1325
}), document.querySelector("[data-character-counter]") && handleTextareaLimiter();
class HiddenText {
    toggle(e) {
        const t = e.previousElementSibling;
        let n;
        switch (e.dataset.initialText ? n = e.dataset.initialText : e.dataset.initialText = e.textContent, t.hidden) {
            case !0:
                t.hidden = !1, e.textContent = "Less";
                break;
            case !1:
                t.hidden = !0, e.textContent = n
        }
    }
}
var hiddenText = new HiddenText;
(() => {
    const e = document.querySelector(".js-search-results-trigger"),
        t = document.querySelector(".js-search-results-wrapper"),
        n = document.querySelector(".js-search-results-target");
    e && (e.onfocus = () => {
        t.classList.add("is-active"), n.classList.add("is-active")
    }, e.onblur = () => {
        t.classList.remove("is-active"), n.classList.remove("is-active")
    })
})();
class Message {
    toggleDropdown(e) {
        this._getElements(e).dropdown.classList.toggle("is-active")
    }
    edit(e) {
        const t = this._getElements(e),
            n = t.textWrapper.offsetHeight,
            i = t.textWrapper.textContent;
        this._enableEditing(t), t.textarea.style.height = `${n}px`, t.textarea.value = i, t.textWrapper.style.display = "none", t.textarea.style.display = "block"
    }
    delete(e) {
        this._getElements(e).container.remove()
    }
    save(e) {
        const t = this._getElements(e),
            n = t.textarea.value;
        this._disableEditing(t), t.textarea.style.display = "none", t.textWrapper.style.display = "", t.textWrapper.textContent = n
    }
    cancel(e) {
        const t = this._getElements(e);
        this._disableEditing(t), t.textarea.value = "", t.textWrapper.style.display = "", t.textarea.style.display = "none"
    }
    _enableEditing(e) {
        e.dropdown.classList.remove("is-active"), e.dropdownButton.style.display = "none", e.editButtons.style.display = "block"
    }
    _disableEditing(e) {
        e.dropdownButton.style.display = "", e.editButtons.style.display = ""
    }
    _getElements(e) {
        const t = e.closest(".js-message-toggle");
        return {
            container: t,
            dropdownButton: t.querySelector(".js-message-dropdown-button"),
            dropdown: t.querySelector(".js-message-dropdown"),
            textWrapper: t.querySelector(".js-message-content"),
            textarea: t.querySelector(".js-message-textarea"),
            editButtons: t.querySelector(".js-message-edit-buttons")
        }
    }
}
const message = new Message;
"undefined" != typeof jQuery && function(e, t) {
        function n(e, t, n) {
            return new Array(n + 1 - e.length).join(t) + e
        }

        function i() {
            if (1 === arguments.length) {
                var t = arguments[0];
                return "string" == typeof t && (t = e.fn.timepicker.parseTime(t)), new Date(0, 0, 0, t.getHours(), t.getMinutes(), t.getSeconds())
            }
            return 3 === arguments.length ? new Date(0, 0, 0, arguments[0], arguments[1], arguments[2]) : 2 === arguments.length ? new Date(0, 0, 0, arguments[0], arguments[1], 0) : new Date(0, 0, 0)
        }
        var s, r;
        e.TimePicker = function() {
            var t = this;
            t.container = e(".ui-timepicker-container"), t.ui = t.container.find(".ui-timepicker"), 0 === t.container.length && (t.container = e("<div></div>").addClass("ui-timepicker-container").addClass("ui-timepicker-hidden ui-helper-hidden").appendTo("body").hide(), t.ui = e("<div></div>").addClass("ui-timepicker").addClass("ui-widget ui-widget-content ui-menu").addClass("ui-corner-all").appendTo(t.container), t.viewport = e("<ul></ul>").addClass("ui-timepicker-viewport").appendTo(t.ui), e.fn.jquery >= "1.4.2" && t.ui.delegate("a", "mouseenter.timepicker", (function() {
                t.activate(!1, e(this).parent())
            })).delegate("a", "mouseleave.timepicker", (function() {
                t.deactivate(!1)
            })).delegate("a", "click.timepicker", (function(n) {
                n.preventDefault(), t.select(!1, e(this).parent())
            })))
        }, e.TimePicker.count = 0, e.TimePicker.instance = function() {
            return e.TimePicker._instance || (e.TimePicker._instance = new e.TimePicker), e.TimePicker._instance
        }, e.TimePicker.prototype = {
            keyCode: {
                ALT: 18,
                BLOQ_MAYUS: 20,
                CTRL: 17,
                DOWN: 40,
                END: 35,
                ENTER: 13,
                HOME: 36,
                LEFT: 37,
                NUMPAD_ENTER: 108,
                PAGE_DOWN: 34,
                PAGE_UP: 33,
                RIGHT: 39,
                SHIFT: 16,
                TAB: 9,
                UP: 38
            },
            _items: function(t, n) {
                var s, r, o = e("<ul></ul>"),
                    a = null;
                for (-1 === t.options.timeFormat.indexOf("m") && t.options.interval % 60 != 0 && (t.options.interval = 60 * Math.max(Math.round(t.options.interval / 60), 1)), s = n ? i(n) : t.options.startTime ? i(t.options.startTime) : i(t.options.startHour, t.options.startMinutes), r = new Date(s.getTime() + 864e5); s < r;) this._isValidTime(t, s) && (a = e("<li>").addClass("ui-menu-item").appendTo(o), e("<a>").addClass("ui-corner-all").text(e.fn.timepicker.formatTime(t.options.timeFormat, s)).appendTo(a), a.data("time-value", s)), s = new Date(s.getTime() + 60 * t.options.interval * 1e3);
                return o.children()
            },
            _isValidTime: function(e, t) {
                var n = null,
                    s = null;
                return t = i(t), null !== e.options.minTime ? n = i(e.options.minTime) : null === e.options.minHour && null === e.options.minMinutes || (n = i(e.options.minHour, e.options.minMinutes)), null !== e.options.maxTime ? s = i(e.options.maxTime) : null === e.options.maxHour && null === e.options.maxMinutes || (s = i(e.options.maxHour, e.options.maxMinutes)), null !== n && null !== s ? t >= n && t <= s : null !== n ? t >= n : null === s || t <= s
            },
            _hasScroll: function() {
                var e = void 0 !== this.ui.prop ? "prop" : "attr";
                return this.ui.height() < this.ui[e]("scrollHeight")
            },
            _move: function(e, t, n) {
                if (this.closed() && this.open(e), this.active) {
                    var i = this.active[t + "All"](".ui-menu-item").eq(0);
                    i.length ? this.activate(e, i) : this.activate(e, this.viewport.children(n))
                } else this.activate(e, this.viewport.children(n))
            },
            register: function(t, n) {
                var i = this,
                    s = {};
                s.element = e(t), s.element.data("TimePicker") || (s.options = e.metadata ? e.extend({}, n, s.element.metadata()) : e.extend({}, n), s.widget = i, e.extend(s, {
                    next: function() {
                        return i.next(s)
                    },
                    previous: function() {
                        return i.previous(s)
                    },
                    first: function() {
                        return i.first(s)
                    },
                    last: function() {
                        return i.last(s)
                    },
                    selected: function() {
                        return i.selected(s)
                    },
                    open: function() {
                        return i.open(s)
                    },
                    close: function() {
                        return i.close(s)
                    },
                    closed: function() {
                        return i.closed(s)
                    },
                    destroy: function() {
                        return i.destroy(s)
                    },
                    parse: function(e) {
                        return i.parse(s, e)
                    },
                    format: function(e, t) {
                        return i.format(s, e, t)
                    },
                    getTime: function() {
                        return i.getTime(s)
                    },
                    setTime: function(e, t) {
                        return i.setTime(s, e, t)
                    },
                    option: function(e, t) {
                        return i.option(s, e, t)
                    }
                }), i._setDefaultTime(s), i._addInputEventsHandlers(s), s.element.data("TimePicker", s))
            },
            _setDefaultTime: function(t) {
                "now" === t.options.defaultTime ? t.setTime(i(new Date)) : t.options.defaultTime && t.options.defaultTime.getFullYear ? t.setTime(i(t.options.defaultTime)) : t.options.defaultTime && t.setTime(e.fn.timepicker.parseTime(t.options.defaultTime))
            },
            _addInputEventsHandlers: function(t) {
                var n = this;
                t.element.bind("keydown.timepicker", (function(e) {
                    switch (e.which || e.keyCode) {
                        case n.keyCode.ENTER:
                        case n.keyCode.NUMPAD_ENTER:
                            e.preventDefault(), n.closed() ? t.element.trigger("change.timepicker") : n.select(t, n.active);
                            break;
                        case n.keyCode.UP:
                            t.previous();
                            break;
                        case n.keyCode.DOWN:
                            t.next();
                            break;
                        default:
                            n.closed() || t.close(!0)
                    }
                })).bind("focus.timepicker", (function() {
                    t.open()
                })).bind("blur.timepicker", (function() {
                    setTimeout((function() {
                        t.element.data("timepicker-user-clicked-outside") && t.close()
                    }))
                })).bind("change.timepicker", (function() {
                    t.closed() && t.setTime(e.fn.timepicker.parseTime(t.element.val()))
                }))
            },
            select: function(t, n) {
                var i = !1 === t ? this.instance : t;
                this.setTime(i, e.fn.timepicker.parseTime(n.children("a").text())), this.close(i, !0)
            },
            activate: function(e, t) {
                if ((!1 === e ? this.instance : e) === this.instance) {
                    if (this.deactivate(), this._hasScroll()) {
                        var n = t.offset().top - this.ui.offset().top,
                            i = this.ui.scrollTop(),
                            s = this.ui.height();
                        n < 0 ? this.ui.scrollTop(i + n) : n >= s && this.ui.scrollTop(i + n - s + t.height())
                    }
                    this.active = t.eq(0).children("a").addClass("ui-state-hover").attr("id", "ui-active-item").end()
                }
            },
            deactivate: function() {
                this.active && (this.active.children("a").removeClass("ui-state-hover").removeAttr("id"), this.active = null)
            },
            next: function(e) {
                return (this.closed() || this.instance === e) && this._move(e, "next", ".ui-menu-item:first"), e.element
            },
            previous: function(e) {
                return (this.closed() || this.instance === e) && this._move(e, "prev", ".ui-menu-item:last"), e.element
            },
            first: function(e) {
                return this.instance === e && (this.active && 0 === this.active.prevAll(".ui-menu-item").length)
            },
            last: function(e) {
                return this.instance === e && (this.active && 0 === this.active.nextAll(".ui-menu-item").length)
            },
            selected: function(e) {
                return this.instance === e && this.active ? this.active : null
            },
            open: function(t) {
                var n = this,
                    i = t.getTime(),
                    s = t.options.dynamic && i;
                if (!t.options.dropdown) return t.element;
                switch (t.element.data("timepicker-event-namespace", Math.random()), e(document).bind("click.timepicker-" + t.element.data("timepicker-event-namespace"), (function(e) {
                    t.element.get(0) === e.target ? t.element.data("timepicker-user-clicked-outside", !1) : t.element.data("timepicker-user-clicked-outside", !0).blur()
                })), (t.rebuild || !t.items || s) && (t.items = n._items(t, s ? i : null)), (t.rebuild || n.instance !== t || s) && (e.fn.jquery < "1.4.2" ? (n.viewport.children().remove(), n.viewport.append(t.items), n.viewport.find("a").bind("mouseover.timepicker", (function() {
                    n.activate(t, e(this).parent())
                })).bind("mouseout.timepicker", (function() {
                    n.deactivate(t)
                })).bind("click.timepicker", (function(i) {
                    i.preventDefault(), n.select(t, e(this).parent())
                }))) : (n.viewport.children().detach(), n.viewport.append(t.items))), t.rebuild = !1, n.container.removeClass("ui-helper-hidden ui-timepicker-hidden ui-timepicker-standard ui-timepicker-corners").show(), t.options.theme) {
                    case "standard":
                        n.container.addClass("ui-timepicker-standard");
                        break;
                    case "standard-rounded-corners":
                        n.container.addClass("ui-timepicker-standard ui-timepicker-corners")
                }
                n.container.hasClass("ui-timepicker-no-scrollbar") || t.options.scrollbar || (n.container.addClass("ui-timepicker-no-scrollbar"), n.viewport.css({
                    paddingRight: 40
                }));
                var r = n.container.outerHeight() - n.container.height(),
                    o = t.options.zindex ? t.options.zindex : t.element.offsetParent().css("z-index"),
                    a = t.element.offset();
                n.container.css({
                    top: a.top + t.element.outerHeight(),
                    left: a.left
                }), n.container.show(), n.container.css({
                    left: t.element.offset().left,
                    height: n.ui.outerHeight() + r,
                    width: t.element.outerWidth(),
                    zIndex: o,
                    cursor: "default"
                });
                var c = n.container.width() - (n.ui.outerWidth() - n.ui.width());
                return n.ui.css({
                    width: c
                }), n.viewport.css({
                    width: c
                }), t.items.css({
                    width: c
                }), n.instance = t, i ? t.items.each((function() {
                    var s = e(this);
                    return (e.fn.jquery < "1.4.2" ? e.fn.timepicker.parseTime(s.find("a").text()) : s.data("time-value")).getTime() !== i.getTime() || (n.activate(t, s), !1)
                })) : n.deactivate(t), t.element
            },
            close: function(t) {
                return this.instance === t && (this.container.addClass("ui-helper-hidden ui-timepicker-hidden").hide(), this.ui.scrollTop(0), this.ui.children().removeClass("ui-state-hover")), e(document).unbind("click.timepicker-" + t.element.data("timepicker-event-namespace")), t.element
            },
            closed: function() {
                return this.ui.is(":hidden")
            },
            destroy: function(e) {
                return this.close(e, !0), e.element.unbind(".timepicker").data("TimePicker", null)
            },
            parse: function(t, n) {
                return e.fn.timepicker.parseTime(n)
            },
            format: function(t, n, i) {
                return i = i || t.options.timeFormat, e.fn.timepicker.formatTime(i, n)
            },
            getTime: function(t) {
                var n = e.fn.timepicker.parseTime(t.element.val());
                return n instanceof Date && !this._isValidTime(t, n) ? null : n instanceof Date && t.selectedTime ? t.format(n) === t.format(t.selectedTime) ? t.selectedTime : n : n instanceof Date ? n : null
            },
            setTime: function(t, n, s) {
                var r = t.selectedTime;
                if ("string" == typeof n && (n = t.parse(n)), n && n.getMinutes && this._isValidTime(t, n)) {
                    if (n = i(n), t.selectedTime = n, t.element.val(t.format(n, t.options.timeFormat)), s) return t
                } else t.selectedTime = null;
                return null === r && null === t.selectedTime || (t.element.trigger("time-change", [n]), e.isFunction(t.options.change) && t.options.change.apply(t.element, [n])), t.element
            },
            option: function(t, n, i) {
                if (void 0 === i) return t.options[n];
                var s, r, o = t.getTime();
                "string" == typeof n ? (s = {})[n] = i : s = n, r = ["minHour", "minMinutes", "minTime", "maxHour", "maxMinutes", "maxTime", "startHour", "startMinutes", "startTime", "timeFormat", "interval", "dropdown"], e.each(s, (function(n) {
                    t.options[n] = s[n], t.rebuild = t.rebuild || e.inArray(n, r) > -1
                })), t.rebuild && t.setTime(o)
            }
        }, e.TimePicker.defaults = {
            timeFormat: "hh:mm p",
            minHour: null,
            minMinutes: null,
            minTime: null,
            maxHour: null,
            maxMinutes: null,
            maxTime: null,
            startHour: null,
            startMinutes: null,
            startTime: null,
            interval: 30,
            dynamic: !0,
            theme: "standard",
            zindex: null,
            dropdown: !0,
            scrollbar: !1,
            change: function() {}
        }, e.TimePicker.methods = {
            chainable: ["next", "previous", "open", "close", "destroy", "setTime"]
        }, e.fn.timepicker = function(t) {
            if ("string" == typeof t) {
                var n, i, s = Array.prototype.slice.call(arguments, 1);
                return i = this[n = "option" === t && arguments.length > 2 ? "each" : -1 !== e.inArray(t, e.TimePicker.methods.chainable) ? "each" : "map"]((function() {
                    var n = e(this).data("TimePicker");
                    if ("object" == typeof n) return n[t].apply(n, s)
                })), "map" === n && 1 === this.length ? e.makeArray(i).shift() : "map" === n ? e.makeArray(i) : i
            }
            if (1 === this.length && this.data("TimePicker")) return this.data("TimePicker");
            var r = e.extend({}, e.TimePicker.defaults, t);
            return this.each((function() {
                e.TimePicker.instance().register(this, r)
            }))
        }, e.fn.timepicker.formatTime = function(e, t) {
            var i = t.getHours(),
                s = i % 12,
                r = t.getMinutes(),
                o = t.getSeconds(),
                a = {
                    hh: n((0 === s ? 12 : s).toString(), "0", 2),
                    HH: n(i.toString(), "0", 2),
                    mm: n(r.toString(), "0", 2),
                    ss: n(o.toString(), "0", 2),
                    h: 0 === s ? 12 : s,
                    H: i,
                    m: r,
                    s: o,
                    p: i > 11 ? "PM" : "AM"
                },
                c = e,
                l = "";
            for (l in a) a.hasOwnProperty(l) && (c = c.replace(new RegExp(l, "g"), a[l]));
            return c = c.replace(new RegExp("a", "g"), i > 11 ? "pm" : "am")
        }, e.fn.timepicker.parseTime = (r = (s = [
            [/^(\d+)$/, "$1"],
            [/^:(\d)$/, "$10"],
            [/^:(\d+)/, "$1"],
            [/^(\d):([7-9])$/, "0$10$2"],
            [/^(\d):(\d\d)$/, "$1$2"],
            [/^(\d):(\d{1,})$/, "0$1$20"],
            [/^(\d\d):([7-9])$/, "$10$2"],
            [/^(\d\d):(\d)$/, "$1$20"],
            [/^(\d\d):(\d*)$/, "$1$2"],
            [/^(\d{3,}):(\d)$/, "$10$2"],
            [/^(\d{3,}):(\d{2,})/, "$1$2"],
            [/^(\d):(\d):(\d)$/, "0$10$20$3"],
            [/^(\d{1,2}):(\d):(\d\d)/, "$10$2$3"]
        ]).length, function(t) {
            var n, o, a = i(new Date),
                c = !1,
                l = !1,
                d = !1;
            if (void 0 === t || !t.toLowerCase) return null;
            t = t.toLowerCase(), o = !(n = /a/.test(t)) && /p/.test(t), t = t.replace(/[^0-9:]/g, "").replace(/:+/g, ":");
            for (var u = 0; u < r; u += 1)
                if (s[u][0].test(t)) {
                    t = t.replace(s[u][0], s[u][1]);
                    break
                } return 1 === (t = t.replace(/:/g, "")).length ? c = t : 2 === t.length ? c = t : 3 === t.length || 5 === t.length ? (c = t.substr(0, 1), l = t.substr(1, 2), d = t.substr(3, 2)) : (4 === t.length || t.length > 5) && (c = t.substr(0, 2), l = t.substr(2, 2), d = t.substr(4, 2)), t.length > 0 && t.length < 5 && (t.length < 3 && (l = 0), d = 0), !1 !== c && !1 !== l && !1 !== d && (c = parseInt(c, 10), l = parseInt(l, 10), d = parseInt(d, 10), n && 12 === c ? c = 0 : o && c < 12 && (c += 12), c > 24 ? t.length >= 6 ? e.fn.timepicker.parseTime(t.substr(0, 5)) : e.fn.timepicker.parseTime(t + "0" + (n ? "a" : "") + (o ? "p" : "")) : (a.setHours(c, l, d), a))
        })
    }(jQuery), $(".timepicker").timepicker({
        timeFormat: "h:mm p",
        interval: 60,
        defaultTime: "10",
        startTime: "10:00",
        dynamic: !1,
        dropdown: !0,
        scrollbar: !0
    }),
    function(e, t) {
        "object" == typeof exports && "object" == typeof module ? module.exports = t() : "function" == typeof define && define.amd ? define([], t) : "object" == typeof exports ? exports.datepicker = t() : e.datepicker = t()
    }(window, (function() {
        return function(e) {
            var t = {};

            function n(i) {
                if (t[i]) return t[i].exports;
                var s = t[i] = {
                    i: i,
                    l: !1,
                    exports: {}
                };
                return e[i].call(s.exports, s, s.exports, n), s.l = !0, s.exports
            }
            return n.m = e, n.c = t, n.d = function(e, t, i) {
                n.o(e, t) || Object.defineProperty(e, t, {
                    enumerable: !0,
                    get: i
                })
            }, n.r = function(e) {
                "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, {
                    value: "Module"
                }), Object.defineProperty(e, "__esModule", {
                    value: !0
                })
            }, n.t = function(e, t) {
                if (1 & t && (e = n(e)), 8 & t) return e;
                if (4 & t && "object" == typeof e && e && e.__esModule) return e;
                var i = Object.create(null);
                if (n.r(i), Object.defineProperty(i, "default", {
                        enumerable: !0,
                        value: e
                    }), 2 & t && "string" != typeof e)
                    for (var s in e) n.d(i, s, function(t) {
                        return e[t]
                    }.bind(null, s));
                return i
            }, n.n = function(e) {
                var t = e && e.__esModule ? function() {
                    return e.default
                } : function() {
                    return e
                };
                return n.d(t, "a", t), t
            }, n.o = function(e, t) {
                return Object.prototype.hasOwnProperty.call(e, t)
            }, n.p = "", n(n.s = 0)
        }([function(e, t, n) {
            e.exports = n(1)
        }, function(e, t, n) {
            function i(e, t) {
                return function(e) {
                    if (Array.isArray(e)) return e
                }(e) || function(e, t) {
                    if (Symbol.iterator in Object(e) || "[object Arguments]" === Object.prototype.toString.call(e)) {
                        var n = [],
                            i = !0,
                            s = !1,
                            r = void 0;
                        try {
                            for (var o, a = e[Symbol.iterator](); !(i = (o = a.next()).done) && (n.push(o.value), !t || n.length !== t); i = !0);
                        } catch (e) {
                            s = !0, r = e
                        } finally {
                            try {
                                i || null == a.return || a.return()
                            } finally {
                                if (s) throw r
                            }
                        }
                        return n
                    }
                }(e, t) || function() {
                    throw new TypeError("Invalid attempt to destructure non-iterable instance")
                }()
            }
            n(2);
            var s = [],
                r = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                o = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
                a = {
                    t: "top",
                    r: "right",
                    b: "bottom",
                    l: "left",
                    c: "centered"
                },
                c = function() {},
                l = ["click", "focusin", "keydown", "input"];

            function d(e) {
                return Array.isArray(e) ? e.map(d) : "[object Object]" === {}.toString.call(e) ? Object.keys(e).reduce((function(t, n) {
                    return t[n] = d(e[n]), t
                }), {}) : e
            }

            function u(e, t) {
                var n = e.calendar.querySelector(".qs-overlay"),
                    i = n && !n.classList.contains("qs-hidden");
                t = t || new Date(e.currentYear, e.currentMonth), e.calendar.innerHTML = [h(t, e, i), m(t, e, i), p(e, i)].join(""), i && setTimeout((function() {
                    return x(!0, e)
                }), 10)
            }

            function h(e, t, n) {
                return '\n    <div class="qs-controls '.concat(n ? "qs-blur" : "", '">\n      <div class="qs-arrow qs-left"></div>\n      <div class="qs-month-year">\n        <span class="qs-month">').concat(t.months[e.getMonth()], '</span>\n        <span class="qs-year">').concat(e.getFullYear(), '</span>\n      </div>\n      <div class="qs-arrow qs-right"></div>\n    </div>\n  ')
            }

            function m(e, t, n) {
                var i = t.currentMonth,
                    s = t.currentYear,
                    r = t.dateSelected,
                    o = t.maxDate,
                    a = t.minDate,
                    c = t.showAllDates,
                    l = t.days,
                    d = t.disabledDates,
                    u = t.disabler,
                    h = t.noWeekends,
                    m = t.startDay,
                    p = t.weekendIndices,
                    f = t.events,
                    g = t.getRange && t.getRange() || {},
                    v = +g.start,
                    y = +g.end,
                    w = new Date,
                    b = s === w.getFullYear() && i === w.getMonth(),
                    T = S(new Date(e).setDate(1)),
                    k = T.getDay() - m,
                    x = k < 0 ? 7 : 0;
                T.setMonth(T.getMonth() + 1), T.setDate(0);
                var D = T.getDate(),
                    q = [],
                    L = x + 7 * ((k + D) / 7 | 0);
                L += (k + D) % 7 ? 7 : 0, 0 !== m && 0 === k && (L += 7);
                for (var E = 1; E <= L; E++) {
                    var M = (E - 1) % 7,
                        C = l[M],
                        _ = E - (k >= 0 ? k : 7 + k),
                        j = new Date(s, i, _),
                        P = f[+j],
                        A = j.getDate(),
                        N = _ < 1 || _ > D,
                        O = "",
                        B = '<span class="qs-num">'.concat(A, "</span>"),
                        H = v && y && +j >= v && +j <= y;
                    N ? (O = "qs-empty qs-outside-current-month", c ? (P && (O += " qs-event"), O += " qs-disabled") : B = "") : ((a && j < a || o && j > o || u(j) || d.includes(+j) || h && p.includes(M)) && (O = "qs-disabled"), P && (O += " qs-event"), b && _ === w.getDate() && (O += " qs-current"), +j == +r && (O += " qs-active"), H && (O += " qs-range-date-".concat(M), v !== y && (O += +j === v ? " qs-range-date-start qs-active" : +j === y ? " qs-range-date-end qs-active" : " qs-range-date-middle"))), q.push('<div class="qs-square qs-num '.concat(C, " ").concat(O, '">').concat(B, "</div>"))
                }
                var $ = l.map((function(e) {
                    return '<div class="qs-square qs-day">'.concat(e, "</div>")
                })).concat(q);
                if ($.length % 7 != 0) throw "Calendar not constructed properly. The # of squares should be a multiple of 7.";
                return $.unshift('<div class="qs-squares '.concat(n ? "qs-blur" : "", '">')), $.push("</div>"), $.join("")
            }

            function p(e, t) {
                var n = e.overlayPlaceholder,
                    i = e.overlayButton,
                    s = e.overlayMonths.map((function(e, t) {
                        return '\n      <div class="qs-overlay-month" data-month-num="'.concat(t, '">\n        <span data-month-num="').concat(t, '">').concat(e, "</span>\n      </div>\n  ")
                    })).join("");
                return '\n    <div class="qs-overlay '.concat(t ? "" : "qs-hidden", '">\n      <div>\n        <input class="qs-overlay-year" placeholder="').concat(n, '" />\n        <div class="qs-close">&#10005;</div>\n      </div>\n      <div class="qs-overlay-month-container">').concat(s, '</div>\n      <div class="qs-submit qs-disabled">').concat(i, "</div>\n    </div>\n  ")
            }

            function f(e, t, n) {
                var i = t.currentMonth,
                    s = t.currentYear,
                    r = t.calendar,
                    o = t.el,
                    a = t.onSelect,
                    c = t.respectDisabledReadOnly,
                    l = t.sibling,
                    d = r.querySelector(".qs-active"),
                    h = e.textContent;
                (o.disabled || o.readOnly) && c || (t.dateSelected = n ? void 0 : new Date(s, i, h), d && d.classList.remove("qs-active"), n || e.classList.add("qs-active"), v(o, t, n), !n && T(t), l && (g({
                    instance: t,
                    deselect: n
                }), u(t), u(l)), a(t, n ? void 0 : new Date(t.dateSelected)))
            }

            function g(e) {
                var t = e.instance,
                    n = e.deselect,
                    i = t.first ? t : t.sibling,
                    s = i.sibling;
                i === t ? n ? (i.minDate = i.originalMinDate, s.minDate = s.originalMinDate) : s.minDate = i.dateSelected : n ? (s.maxDate = s.originalMaxDate, i.maxDate = i.originalMaxDate) : i.maxDate = s.dateSelected
            }

            function v(e, t, n) {
                if (!t.nonInput) return n ? e.value = "" : t.formatter !== c ? t.formatter(e, t.dateSelected, t) : void(e.value = t.dateSelected.toDateString())
            }

            function y(e, t, n, i) {
                n || i ? (n && (t.currentYear = n), i && (t.currentMonth = +i)) : (t.currentMonth += e.contains("qs-right") ? 1 : -1, 12 === t.currentMonth ? (t.currentMonth = 0, t.currentYear++) : -1 === t.currentMonth && (t.currentMonth = 11, t.currentYear--)), t.currentMonthName = t.months[t.currentMonth], u(t), t.onMonthChange(t)
            }

            function w(e) {
                if (!e.noPosition) {
                    var t = e.el,
                        n = e.calendarContainer,
                        s = e.position,
                        r = e.parent,
                        o = s.top,
                        a = s.right;
                    if (s.centered) return n.classList.add("qs-centered");
                    var c = i([r, t, n].map((function(e) {
                            return e.getBoundingClientRect()
                        })), 3),
                        l = c[0],
                        d = c[1],
                        u = c[2],
                        h = d.top - l.top + r.scrollTop,
                        m = "".concat(h - (o ? u.height : -1 * d.height), "px"),
                        p = "".concat(d.left - l.left + (a ? d.width - u.width : 0), "px");
                    n.style.setProperty("top", m), n.style.setProperty("left", p)
                }
            }

            function b(e) {
                return "[object Date]" === {}.toString.call(e) && "Invalid Date" !== e.toString()
            }

            function S(e) {
                if (b(e) || "number" == typeof e && !isNaN(e)) {
                    var t = new Date(+e);
                    return new Date(t.getFullYear(), t.getMonth(), t.getDate())
                }
            }

            function T(e) {
                e.disabled || !e.calendarContainer.classList.contains("qs-hidden") && !e.alwaysShow && (x(!0, e), e.calendarContainer.classList.add("qs-hidden"), e.onHide(e))
            }

            function k(e) {
                e.disabled || (e.calendarContainer.classList.remove("qs-hidden"), w(e), e.onShow(e))
            }

            function x(e, t) {
                var n = t.calendar;
                if (n) {
                    var i = n.querySelector(".qs-overlay"),
                        s = i.querySelector(".qs-overlay-year"),
                        r = n.querySelector(".qs-controls"),
                        o = n.querySelector(".qs-squares");
                    e ? (i.classList.add("qs-hidden"), r.classList.remove("qs-blur"), o.classList.remove("qs-blur"), s.value = "") : (i.classList.remove("qs-hidden"), r.classList.add("qs-blur"), o.classList.add("qs-blur"), s.focus())
                }
            }

            function D(e, t, n, i) {
                var s = isNaN(+(new Date).setFullYear(t.value || void 0)),
                    r = s ? null : t.value;
                13 === (e.which || e.keyCode) || "click" === e.type ? i ? y(null, n, r, i) : s || t.classList.contains("qs-disabled") || y(null, n, r, i) : n.calendar.contains(t) && n.calendar.querySelector(".qs-submit").classList[s ? "add" : "remove"]("qs-disabled")
            }

            function q(e) {
                var t = e.type,
                    n = e.target,
                    r = n.classList,
                    o = i(s.filter((function(e) {
                        var t = e.calendar,
                            i = e.el;
                        return t.contains(n) || i === n
                    })), 1)[0],
                    a = o && o.calendar.contains(n);
                if (!(o && o.isMobile && o.disableMobile))
                    if ("click" === t) {
                        if (!o) return s.forEach(T);
                        if (o.disabled) return;
                        var c = o.calendar,
                            l = o.calendarContainer,
                            d = o.disableYearOverlay,
                            u = o.nonInput,
                            h = c.querySelector(".qs-overlay-year"),
                            m = !!c.querySelector(".qs-hidden"),
                            p = c.querySelector(".qs-month-year").contains(n),
                            g = n.dataset.monthNum;
                        if (o.noPosition && !a)(l.classList.contains("qs-hidden") ? k : T)(o);
                        else if (r.contains("qs-arrow")) y(r, o);
                        else if (p || r.contains("qs-close")) !d && x(!m, o);
                        else if (g) D(e, h, o, g);
                        else {
                            if (r.contains("qs-num")) {
                                var v = "SPAN" === n.nodeName ? n.parentNode : n,
                                    w = ["qs-disabled", "qs-empty"].some((function(e) {
                                        return v.classList.contains(e)
                                    }));
                                return v.classList.contains("qs-active") ? f(v, o, !0) : !w && f(v, o)
                            }
                            r.contains("qs-submit") && !r.contains("qs-disabled") ? D(e, h, o) : u && n === o.el && k(o)
                        }
                    } else if ("focusin" === t && o) k(o), s.forEach((function(e) {
                    return e !== o && T(e)
                }));
                else if ("keydown" === t && o && !o.disabled) {
                    var b = !o.calendar.querySelector(".qs-overlay").classList.contains("qs-hidden");
                    13 === (e.which || e.keyCode) && b && a ? D(e, n, o) : 27 === (e.which || e.keyCode) && b && a && x(!0, o)
                } else if ("input" === t) {
                    if (!o || !o.calendar.contains(n)) return;
                    var S = o.calendar.querySelector(".qs-submit"),
                        q = n.value.split("").reduce((function(e, t) {
                            return e || "0" !== t ? e + (t.match(/[0-9]/) ? t : "") : ""
                        }), "").slice(0, 4);
                    n.value = q, S.classList[4 === q.length ? "remove" : "add"]("qs-disabled")
                }
            }

            function L() {
                k(this)
            }

            function E() {
                T(this)
            }

            function M(e, t) {
                var n = S(e),
                    i = this.currentYear,
                    s = this.currentMonth,
                    r = this.sibling;
                if (null == e) return this.dateSelected = void 0, v(this.el, this, !0), r && (g({
                    instance: this,
                    deselect: !0
                }), u(r)), u(this), this;
                if (!b(e)) throw "`setDate` needs a JavaScript Date object.";
                if (this.disabledDates.some((function(e) {
                        return +e == +n
                    })) || n < this.minDate || n > this.maxDate) throw "You can't manually set a date that's disabled.";
                return this.currentYear = n.getFullYear(), this.currentMonth = n.getMonth(), this.currentMonthName = this.months[n.getMonth()], this.dateSelected = n, v(this.el, this), r && (g({
                    instance: this
                }), u(r, n)), (i === n.getFullYear() && s === n.getMonth() || t || r) && u(this, n), this
            }

            function C(e) {
                return j(this, e, !0)
            }

            function _(e) {
                return j(this, e)
            }

            function j(e, t, n) {
                var i = e.dateSelected,
                    s = e.first,
                    r = e.sibling,
                    o = e.minDate,
                    a = e.maxDate,
                    c = S(t),
                    l = n ? "Min" : "Max",
                    d = function() {
                        return "original".concat(l, "Date")
                    },
                    h = function() {
                        return "".concat(l.toLowerCase(), "Date")
                    },
                    m = function() {
                        return "set".concat(l)
                    },
                    p = function() {
                        throw "Out-of-range date passed to ".concat(m())
                    };
                if (null == t) e[d()] = void 0, r ? (r[d()] = void 0, n ? (s && !i || !s && !r.dateSelected) && (e.minDate = void 0, r.minDate = void 0) : (s && !r.dateSelected || !s && !i) && (e.maxDate = void 0, r.maxDate = void 0)) : e[h()] = void 0;
                else {
                    if (!b(t)) throw "Invalid date passed to ".concat(m());
                    r ? ((s && n && c > (i || a) || s && !n && c < (r.dateSelected || o) || !s && n && c > (r.dateSelected || a) || !s && !n && c < (i || o)) && p(), e[d()] = c, r[d()] = c, (n && (s && !i || !s && !r.dateSelected) || !n && (s && !r.dateSelected || !s && !i)) && (e[h()] = c, r[h()] = c)) : ((n && c > (i || a) || !n && c < (i || o)) && p(), e[h()] = c)
                }
                return r && u(r), u(e), e
            }

            function P() {
                var e = this.first ? this : this.sibling,
                    t = e.sibling;
                return {
                    start: e.dateSelected,
                    end: t.dateSelected
                }
            }

            function A() {
                var e = this,
                    t = this.inlinePosition,
                    n = this.parent,
                    i = this.calendarContainer,
                    r = this.el,
                    o = this.sibling;
                for (var a in t && (s.some((function(t) {
                        return t !== e && t.parent === n
                    })) || n.style.setProperty("position", null)), i.remove(), s = s.filter((function(e) {
                        return e.el !== r
                    })), o && delete o.sibling, this) delete this[a];
                s.length || l.forEach((function(e) {
                    return document.removeEventListener(e, q)
                }))
            }
            e.exports = function(e, t) {
                s.length || l.forEach((function(e) {
                    return document.addEventListener(e, q)
                }));
                var n = function(e, t) {
                        var n = e;
                        "string" == typeof n && (n = "#" === n[0] ? document.getElementById(n.slice(1)) : document.querySelector(n));
                        var l = function(e, t) {
                                if (s.some((function(e) {
                                        return e.el === t
                                    }))) throw "A datepicker already exists on that element.";
                                var n = d(e);
                                n.events && (n.events = n.events.reduce((function(e, t) {
                                    if (!b(t)) throw '"options.events" must only contain valid JavaScript Date objects.';
                                    return e[+S(t)] = !0, e
                                }), {})), ["startDate", "dateSelected", "minDate", "maxDate"].forEach((function(e) {
                                    var t = n[e];
                                    if (t && !b(t)) throw '"options.'.concat(e, '" needs to be a valid JavaScript Date object.');
                                    n[e] = S(t)
                                }));
                                var o = n.position,
                                    l = n.maxDate,
                                    u = n.minDate,
                                    h = n.dateSelected,
                                    m = n.overlayPlaceholder,
                                    p = n.overlayButton,
                                    f = n.startDay,
                                    g = n.id;
                                if (n.startDate = S(n.startDate || h || new Date), n.disabledDates = (n.disabledDates || []).map((function(e) {
                                        var t = +S(e);
                                        if (!b(e)) throw 'You supplied an invalid date to "options.disabledDates".';
                                        if (t === +S(h)) throw '"disabledDates" cannot contain the same date as "dateSelected".';
                                        return t
                                    })), n.hasOwnProperty("id") && null == g) throw "Id cannot be `null` or `undefined`";
                                if (g || 0 === g) {
                                    var v = s.filter((function(e) {
                                        return e.id === g
                                    }));
                                    if (v.length > 1) throw "Only two datepickers can share an id.";
                                    v.length ? (n.second = !0, n.sibling = v[0]) : n.first = !0
                                }
                                var y = ["tr", "tl", "br", "bl", "c"].some((function(e) {
                                    return o === e
                                }));
                                if (o && !y) throw '"options.position" must be one of the following: tl, tr, bl, br, or c.';
                                if (n.position = function(e) {
                                        var t = i(e, 2),
                                            n = t[0],
                                            s = t[1],
                                            r = {};
                                        return r[a[n]] = 1, s && (r[a[s]] = 1), r
                                    }(o || "bl"), l < u) throw '"maxDate" in options is less than "minDate".';
                                if (h) {
                                    var w = function(e) {
                                        throw '"dateSelected" in options is '.concat(e ? "less" : "greater", ' than "').concat(e || "mac", 'Date".')
                                    };
                                    u > h && w("min"), l < h && w()
                                }
                                if (["onSelect", "onShow", "onHide", "onMonthChange", "formatter", "disabler"].forEach((function(e) {
                                        "function" != typeof n[e] && (n[e] = c)
                                    })), ["customDays", "customMonths", "customOverlayMonths"].forEach((function(e, t) {
                                        var i = n[e],
                                            s = t ? 12 : 7;
                                        if (i) {
                                            if (!Array.isArray(i) || i.length !== s || i.some((function(e) {
                                                    return "string" != typeof e
                                                }))) throw '"'.concat(e, '" must be an array with ').concat(s, " strings.");
                                            n[t ? t < 2 ? "months" : "overlayMonths" : "days"] = i
                                        }
                                    })), f && f > 0 && f < 7) {
                                    var T = (n.customDays || r).slice(),
                                        k = T.splice(0, f);
                                    n.customDays = T.concat(k), n.startDay = +f, n.weekendIndices = [T.length - 1, T.length]
                                } else n.startDay = 0, n.weekendIndices = [6, 0];
                                return "string" != typeof m && delete n.overlayPlaceholder, "string" != typeof p && delete n.overlayButton, n
                            }(t || {
                                startDate: S(new Date),
                                position: "bl"
                            }, n),
                            u = l.startDate,
                            h = l.dateSelected,
                            m = l.sibling,
                            p = n === document.body,
                            f = p ? document.body : n.parentElement,
                            g = document.createElement("div"),
                            y = document.createElement("div");
                        g.className = "qs-datepicker-container qs-hidden", y.className = "qs-datepicker";
                        var w = {
                            el: n,
                            parent: f,
                            nonInput: "INPUT" !== n.nodeName,
                            noPosition: p,
                            position: !p && l.position,
                            startDate: u,
                            dateSelected: h,
                            disabledDates: l.disabledDates,
                            minDate: l.minDate,
                            maxDate: l.maxDate,
                            noWeekends: !!l.noWeekends,
                            weekendIndices: l.weekendIndices,
                            calendarContainer: g,
                            calendar: y,
                            currentMonth: (u || h).getMonth(),
                            currentMonthName: (l.months || o)[(u || h).getMonth()],
                            currentYear: (u || h).getFullYear(),
                            events: l.events || {},
                            setDate: M,
                            remove: A,
                            setMin: C,
                            setMax: _,
                            show: L,
                            hide: E,
                            onSelect: l.onSelect,
                            onShow: l.onShow,
                            onHide: l.onHide,
                            onMonthChange: l.onMonthChange,
                            formatter: l.formatter,
                            disabler: l.disabler,
                            months: l.months || o,
                            days: l.customDays || r,
                            startDay: l.startDay,
                            overlayMonths: l.overlayMonths || (l.months || o).map((function(e) {
                                return e.slice(0, 3)
                            })),
                            overlayPlaceholder: l.overlayPlaceholder || "4-digit year",
                            overlayButton: l.overlayButton || "Submit",
                            disableYearOverlay: !!l.disableYearOverlay,
                            disableMobile: !!l.disableMobile,
                            isMobile: "ontouchstart" in window,
                            alwaysShow: !!l.alwaysShow,
                            id: l.id,
                            showAllDates: !!l.showAllDates,
                            respectDisabledReadOnly: !!l.respectDisabledReadOnly,
                            first: l.first,
                            second: l.second
                        };
                        if (m) {
                            var T = m,
                                x = w,
                                D = T.minDate || x.minDate,
                                q = T.maxDate || x.maxDate;
                            x.sibling = T, T.sibling = x, T.minDate = D, T.maxDate = q, x.minDate = D, x.maxDate = q, T.originalMinDate = D, T.originalMaxDate = q, x.originalMinDate = D, x.originalMaxDate = q, T.getRange = P, x.getRange = P
                        }
                        h && v(n, w);
                        var j = getComputedStyle(f).position;
                        return p || j && "static" !== j || (w.inlinePosition = !0, f.style.setProperty("position", "relative")), w.inlinePosition && s.forEach((function(e) {
                            e.parent === w.parent && (e.inlinePosition = !0)
                        })), s.push(w), g.appendChild(y), f.appendChild(g), w.alwaysShow && k(w), w
                    }(e, t),
                    h = n.startDate,
                    m = n.dateSelected,
                    p = n.alwaysShow;
                if (n.second) {
                    var f = n.sibling;
                    g({
                        instance: n,
                        deselect: !m
                    }), g({
                        instance: f,
                        deselect: !f.dateSelected
                    }), u(f)
                }
                return u(n, h || m), p && w(n), n
            }
        }, function(e, t, n) {}])
    })); {
    const e = document.querySelectorAll(".js-datepicker-toggle"),
        t = {};
    for (let n = 0; n < e.length; n++) t.i = datepicker(e[n], {
        onSelect() {
            const t = new Event("input", {
                bubbles: !0
            });
            e[n].dispatchEvent(t)
        },
        formatter: function(e, t, n) {
            const i = t.toISOString().slice(0, 10);
            e.value = i
        }
    })
}! function(e, t, n) {
    function i(e) {
        return "object" == typeof e
    }
    "o" === (typeof module)[0] && i(module.exports) ? module.exports = n() : "o" === (typeof exports)[0] ? exports[e] = n() : i(t.define) && t.define.amd ? t.define(e, [], n) : i(t.modulejs) ? t.modulejs.define(e, n) : i(t.YUI) ? t.YUI.add(e, (function(t) {
        t[e] = n()
    })) : t[e] = n()
}("PasswordStrength", this, (function() {
    function e(e, t) {
        Object.keys(e).forEach((function(n) {
            t(n, e[n])
        }))
    }

    function t(e, t) {
        var n;
        return n = "[" + (n = e.replace(/[\W_]/g, (function(e) {
            return "\\" + e
        }))) + "]", new RegExp(n, t || "")
    }
    return Math.log2 || (Math.log2 = function(e) {
            return Math.log(e) / Math.log(2)
        }),
        function n() {
            if (!(this instanceof n)) return new n;
            this.commonPasswords = null, this.trigraph = null, this.charsets = {
                number: "0123456789",
                lower: "abcdefghijklmnopqrstuvwxyz",
                upper: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                punctuation: "!'.,:;?&-\" ",
                symbol: "@#$%^*(){}[]><~`_+=|/"
            }, this.addCommonPasswords = function(e) {
                if (e)
                    if (Array.isArray(e)) this.commonPasswords = e;
                    else {
                        if ("string" != typeof e) throw new Error("Format does not match any expected format.");
                        this.commonPasswords = e.split(/\r\n|\r|\n/)
                    }
                else this.commonPasswords = [];
                return this
            }, this.addTrigraphMap = function(e) {
                if (e) {
                    if (!e || "object" != typeof e || Array.isArray(e)) throw new Error("Format does not match any expected format.");
                    this.trigraph = e
                } else this.trigraph = null;
                return this
            }, this.charsetGroups = function(n) {
                var i;
                return i = {}, e(this.charsets, (function(e, s) {
                    i[e] = t(s).test(n)
                })), i.other = this.otherChars(n), i
            }, this.charsetSize = function(t) {
                var n;
                return n = 0, e(this.charsets, (function(e, i) {
                    t[e] && (n += i.length)
                })), "string" == typeof t.other && (n += t.other.length), n
            }, this.check = function(e) {
                var t;
                return t = {
                    charsetSize: 0,
                    commonPassword: !1,
                    nistEntropyBits: 0,
                    passwordLength: 0,
                    shannonEntropyBits: 0,
                    strengthCode: null,
                    trigraphEntropyBits: null,
                    charsets: null
                }, e && e.length ? (t.commonPassword = this.checkCommonPasswords(e), t.charsets = this.charsetGroups(e), t.charsetSize = this.charsetSize(t.charsets), t.nistEntropyBits = this.nistScore(e), t.shannonEntropyBits = this.shannonScore(e), t.passwordLength = e.length, t.trigraphEntropyBits = this.checkTrigraph(e, t.charsetSize), t.strengthCode = this.determineStrength(t), t) : (this.trigraph && (t.trigraphEntropyBits = 0), t)
            }, this.checkCommonPasswords = function(e) {
                var t, n, i;
                if (e = e.toLowerCase(), this.commonPasswords && this.commonPasswords.length) {
                    for (n = this.commonPasswords, t = this.commonPasswords.length, i = 0; i < t; i += 1)
                        if (n[i] === e) return !0;
                    return !1
                }
                return null
            }, this.checkTrigraph = function(e, t) {
                var n, i, s;
                if (!this.trigraph) return null;
                for (i = 1, e = "_" + (e = e.toLowerCase().replace(/[\W_]/gi, " ").trim()) + "_", n = 0; n < e.length - 2; n += 1) s = e.substr(n, 3), this.trigraph[s] ? i *= (1 - this.trigraph[s] / 1e4) * t : i *= t;
                return Math.log2(i)
            }, this.determineStrength = function(e) {
                var t;
                return "", (t = e.trigraphEntropyBits ? e.trigraphEntropyBits : e.shannonEntropyBits) <= 32 ? "VERY_WEAK" : t <= 48 ? "WEAK" : t <= 64 ? "REASONABLE" : t <= 80 ? "STRONG" : "VERY_STRONG"
            }, this.nistScore = function(e) {
                var t, n;
                return n = 0, (t = e.length) > 20 && (n += t - 20, t = 20), t > 8 && (n += 1.5 * (t - 8), t = 8), t > 1 && (n += 2 * (t - 1), t = 1), t && (n += 4), e.match(/[A-Z]/) && e.match(/[^A-Za-z]/) && (n += 6), n
            }, this.otherChars = function(n) {
                var i, s, r;
                return i = "", e(this.charsets, (function(e, t) {
                    i += t
                })), r = t(i, "g"), s = {}, n.replace(r, "").split("").forEach((function(e) {
                    s[e] = !0
                })), Object.keys(s).join("")
            }, this.shannonScore = function(t) {
                var n, i;
                return i = 0, n = t.length, e(function() {
                    var e, i, s;
                    for (i = {}, s = 0; s < n; s += 1) i[e = t.charAt(s)] ? i[e] += 1 : i[e] = 1;
                    return i
                }(), (function(e, t) {
                    var s;
                    i -= (s = t / n) * Math.log2(s)
                })), i * n
            }
        }
}));
const passwordStrength = new PasswordStrength;

function handlePasswordCheck() {
    const e = document.querySelector(".js-password-check-toggle"),
        t = e.querySelector(".js-password-strength-input"),
        n = e.querySelector(".js-password-match-input"),
        i = e.querySelector(".js-password-strength-output"),
        s = e.querySelector(".js-password-match-output"),
        r = i.children[0],
        o = s.children[0],
        a = r.textContent,
        c = o.textContent,
        l = ["VERY_WEAK", "WEAK", "REASONABLE", "STRONG", "VERY_STRONG"];

    function d() {
        return "" == t.value || "" == n.value ? (s.removeAttribute("data-match"), o.textContent = c, !1) : t.value === n.value ? (s.classList.add("has-match"), o.textContent = "Match", s.dataset.match = "true", !0) : t.value !== n.value ? (s.classList.remove("has-match"), o.textContent = "No match", s.dataset.match = "false", !1) : void 0
    }
    e.oninput = e => {
        const n = e.target;
        let s;
        d(), n == t && "" == n.value && (i.removeAttribute("data-strength"), r.textContent = a), n == t && (s = passwordStrength.check(n.value).strengthCode, function(e) {
            switch (e) {
                case l[0]:
                    i.dataset.strength = e, r.textContent = "Very weak";
                    break;
                case l[1]:
                    i.dataset.strength = e, r.textContent = "Weak";
                    break;
                case l[2]:
                    i.dataset.strength = e, r.textContent = "Reasonable";
                    break;
                case l[3]:
                    i.dataset.strength = e, r.textContent = "Strong";
                    break;
                case l[4]:
                    i.dataset.strength = e, r.textContent = "Very strong"
            }
        }(s))
    }, e.onsubmit = () => {
        if (!d()) return !1
    }
}
try {
    handlePasswordCheck()
} catch (e) {
    console.log(e.message)
}

function setEditor(e, t) {
    const n = document.querySelector(t);
    if (!n) return;
    const i = n.querySelector(".js-editor-counter-toggle"),
        s = new Quill(e, {
            modules: {
                toolbar: t
            },
            placeholder: "Enter text",
            theme: "snow"
        }),
        r = i.textContent;
    s.on("text-change", (f) => {
        var z = e.replace(/\./g, "#").replace(/\-/g, "_")
        document.querySelector(z).innerHTML = (s.container.querySelector('.ql-editor').innerHTML)
        s.getLength() > r && s.deleteText(r, s.getLength()), i.textContent = r - (s.getLength() - 1)
    })
}
setEditor(".js-editor-primary", ".js-toolbar-primary"), setEditor(".js-editor-secondary", ".js-toolbar-secondary");