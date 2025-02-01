"use strict";
document.addEventListener("DOMContentLoaded", function() {
    // Select all custom select elements
    const customSelects = document.querySelectorAll(".custom-select");

    customSelects.forEach(customSelect => {
        const selectedOption = customSelect.querySelector(".selected-option");
        const optionsList = customSelect.querySelector(".options-list");
        const options = customSelect.querySelectorAll(".option");
        const hiddenInput = customSelect.nextElementSibling; // Get the hidden input right after the custom select

        // Function to set the default selected option based on the hidden input value
        function setDefaultSelectedOption() {
            const defaultValue = hiddenInput.value;
            options.forEach(option => {
                if (option.getAttribute("data-value") === defaultValue) {
                    selectedOption.textContent = option.textContent; // Set the selected option text
                }
            });
        }

        // Call the function to set the default selected option
        setDefaultSelectedOption();

        // Function to close dropdown when clicking outside
        function closeDropdownOnClickOutside(e) {
            if (!customSelect.contains(e.target)) {
                customSelect.classList.remove("active");
                document.removeEventListener("click", closeDropdownOnClickOutside);
            }
        }

        // Toggle dropdown on click
        customSelect.addEventListener("click", function(e) {
            e.stopPropagation(); // Prevent event from bubbling up
            const isActive = customSelect.classList.toggle("active");

            if (isActive) {
                document.addEventListener("click", closeDropdownOnClickOutside);
            } else {
                document.removeEventListener("click", closeDropdownOnClickOutside);
            }
        });

        // Set selected option and close dropdown
        options.forEach(option => {
            option.addEventListener("click", function(e) {
                const value = option.getAttribute("data-value");
                const text = option.textContent;
                e.stopPropagation(); // Prevent event from bubbling up

                // Set the selected option text
                selectedOption.textContent = text;

                // Set the hidden input value
                hiddenInput.value = value;

                // Close the dropdown
                customSelect.classList.remove("active");

                // Remove the outside click event listener since dropdown is closed
                document.removeEventListener("click", closeDropdownOnClickOutside);
            });
        });
    });
});