// Initialize jQuery functionality
jQuery(function ($) {
    // Sidenav
    $(".sidenav").sidenav({ edge: "right" });

    // Collapsible
    $(".collapsible").collapsible();

    // Datepicker
    $(".datepicker").datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 5,
        showClearBtn: true,
        i18n: {
            done: "Select",
        },
    });

    // Select
    $("select").formSelect();

    // Modal
    $(".modal").modal();

    // Validate Materialize Select
    validateMaterializeSelect();
});

function validateMaterializeSelect() {
    let classValid = {
        "border-bottom": "1px solid #4caf50",
        "box-shadow": "0 1px 0 0 #4caf50",
    };
    let classInvalid = {
        "border-bottom": "1px solid #f44336",
        "box-shadow": "0 1px 0 0 #f44336",
    };
    if ($("select.validate").prop("required")) {
        $("select.validate").css({
            display: "block",
            height: "0",
            padding: "0",
            width: "0",
            position: "absolute",
        });
    }
    $(".select-wrapper input.select-dropdown")
        .on("focusin", function () {
            $(this)
                .parent(".select-wrapper")
                .on("change", function () {
                    if (
                        $(this)
                            .children("ul")
                            .children("li.selected:not(.disabled)")
                            .on("click", function () {})
                    ) {
                        $(this).children("input").css(classValid);
                    }
                });
        })
        .on("click", function () {
            if (
                $(this)
                    .parent(".select-wrapper")
                    .children("ul")
                    .children("li.selected:not(.disabled)")
                    .css("background-color") === "rgba(0, 0, 0, 0.03)"
            ) {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
}

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

// Add event listeners to Edit and Delete buttons in recipe collapsible
document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".collapsible-header .amber.darken-3");
    const deleteButtons = document.querySelectorAll(".collapsible-header .black");

    // Stop propagation for Edit buttons
    editButtons.forEach((button) => {
        button.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    });

    // Stop propagation for Delete buttons
    deleteButtons.forEach((button) => {
        button.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    });
});

// Handle recipe deletion confirmation
document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".delete-recipe");
    const confirmDeleteBtn = document.getElementById("confirmDelete");
    let deleteUrl = "";

    deleteButtons.forEach((button) => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            deleteUrl = this.getAttribute("href");
            const modal = M.Modal.getInstance(document.getElementById("deleteModal"));
            modal.open();
        });
    });

    confirmDeleteBtn.addEventListener("click", function () {
        if (deleteUrl) {
            window.location.href = deleteUrl;
        }
    });
});

// Handle category deletion confirmation
document.addEventListener("DOMContentLoaded", function () {
    const deleteCategoryButtons = document.querySelectorAll(".delete-category");
    const confirmDeleteCategoryBtn = document.getElementById("confirmDeleteCategory");
    let deleteCategoryUrl = "";

    deleteCategoryButtons.forEach((button) => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            deleteCategoryUrl = this.getAttribute("href");
            const modal = M.Modal.getInstance(document.getElementById("deleteCategoryModal"));
            modal.open();
        });
    });

    confirmDeleteCategoryBtn.addEventListener("click", function () {
        if (deleteCategoryUrl) {
            window.location.href = deleteCategoryUrl;
        }
    });
});
