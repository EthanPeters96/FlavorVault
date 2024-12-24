// Sidenav
$(document).ready(function () {
    $(".sidenav").sidenav({ edge: "right" });
});

// Collapsible
$(document).ready(function () {
    $(".collapsible").collapsible();
});

// Datepicker
$(document).ready(function () {
    $(".datepicker").datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 5,
        showClearBtn: true,
        i18n: {
            done: "Select",
        },
    });
});

// Select
$(document).ready(function () {
    $("select").formSelect();
});

// Remove flash messages after 3 seconds
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        let messages = document.getElementsByClassName("flashes");
        for (let message of messages) {
            message.style.opacity = "0";
            // Remove element after fade out
            setTimeout(function () {
                message.remove();
            }, 500);
        }
    }, 3000);
});
