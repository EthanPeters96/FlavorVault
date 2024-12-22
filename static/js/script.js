// Sidenav
$(document).ready(function () {
    $(".sidenav").sidenav({ edge: "right" });
});

// Collapsible
$(document).ready(function () {
    $(".collapsible").collapsible();
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
