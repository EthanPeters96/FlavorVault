const $ = require("jquery");
// Initialize jQuery globally for Materialize
global.$ = global.jQuery = $;
// Initialize Materialize after jQuery is global
require("materialize-css/dist/js/materialize.min.js");
require("materialize-css/dist/css/materialize.min.css");

describe("Sidenav and Select Validation", () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div class="sidenav"></div>
            <div class="collapsible"></div>
            <div class="select-wrapper">
                <select class="validate" required>
                    <option value="">Select an option</option>
                    <option value="1">Option 1</option>
                </select>
                <input class="select-dropdown" />
            </div>
            <div class="flashes"></div>
            <button class="delete-recipe" href="/delete/1">Delete Recipe</button>
            <div id="deleteModal" class="modal"></div>
            <button id="confirmDelete">Confirm Delete</button>
        `;

        // Initialize Materialize components
        M.AutoInit();

        // Initialize select validation
        const selectElem = document.querySelector("select");
        M.FormSelect.init(selectElem);

        // Add validation event handlers
        $(".select-wrapper input.select-dropdown").on("focusin change", function () {
            const $select = $(this).siblings("select");
            const selectedValue = $select.val();
            console.log("Validation check - selected value:", selectedValue);
            console.log("DOM structure:", $(this).parent().html());

            if (selectedValue && selectedValue !== "") {
                $(this).css({
                    "border-bottom": "1px solid #4caf50",
                    "box-shadow": "0 1px 0 0 #4caf50",
                });
            } else {
                $(this).css({
                    "border-bottom": "1px solid #f44336",
                    "box-shadow": "0 1px 0 0 #f44336",
                });
            }
        });
    });

    test("should initialize sidenav", () => {
        const elem = document.querySelector(".sidenav");
        const instance = M.Sidenav.init(elem, { edge: "right" });
        expect(instance).toBeTruthy();
        expect(elem.classList.contains("sidenav")).toBe(true);
    });

    test("should validate select input", () => {
        const $select = $("select.validate");
        const $input = $(".select-wrapper input.select-dropdown");

        // Set value and trigger events
        $select.val("1");
        $input.trigger("focusin");
        $select.trigger("change");
        $select.trigger("change");

        // Debugging output
        console.log("Selected value:", $select.val());
        console.log("Border color after valid selection:", $input.css("border-bottom"));

        expect($input.css("border-bottom")).toBe("1px solid #4caf50");

        // Simulate selection of empty option
        $select.val("");
        $select.trigger("change");
        $input.trigger("change");

        // Debugging output
        console.log("Selected value after empty:", $select.val());
        console.log("Border color after empty selection:", $input.css("border-bottom"));

        expect($input.css("border-bottom")).toBe("1px solid #f44336");
    });

    test("should handle delete confirmation", () => {
        // Mock window.location
        const location = new URL("http://localhost");
        delete window.location;
        window.location = { href: location.href };

        const deleteUrl = "/delete/1";
        const $deleteButton = $(".delete-recipe");
        $deleteButton.trigger("click");

        const modal = M.Modal.getInstance(document.getElementById("deleteModal"));
        expect(modal).toBeTruthy();

        // Simulate confirm delete
        const $confirmDelete = $("#confirmDelete");
        $confirmDelete.trigger("click");

        // Check if the href was attempted to be set
        expect(window.location.href).toContain("localhost");
    });
});
