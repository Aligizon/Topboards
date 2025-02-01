// animations
const addButtonArray = document.getElementsByClassName("add-product-button");

Array.from(addButtonArray).forEach(addButton => {
    addButton.addEventListener('click', function() {
        addButton.style.animation = "add-product-animation 0.5s ease-out";
        let animationTimeout = (+addButton.style.animationDuration.slice(0, -1)) * 1000;
        setTimeout(()=>{
            addButton.style.animation="none";
        }, animationTimeout);
    });
});

// checkboxes
const mainSliderSelectAll = document.getElementById("mainSliderSelectAll");
var mainSliderCheckboxes = document.getElementsByClassName("mainSliderCheckbox");

mainSliderSelectAll.addEventListener('change', function() {
    Array.from(mainSliderCheckboxes).forEach(checkbox => {
        if (checkbox.checked) {
            checkbox.checked = false
        }
        else {
            checkbox.checked = true
        }
    });
});

const newAddedSelectAll = document.getElementById("newAddedSelectAll");
var newAddedCheckboxes = document.getElementsByClassName("newAddedCheckbox");

newAddedSelectAll.addEventListener('change', function() {
    Array.from(newAddedCheckboxes).forEach(checkbox => {
        if (checkbox.checked) {
            checkbox.checked = false
        }
        else {
            checkbox.checked = true
        }
    });
});

const recommendedSelectAll = document.getElementById("recommendedSelectAll");
var recommendedCheckboxes = document.getElementsByClassName("recommendedCheckbox");

recommendedSelectAll.addEventListener('change', function() {
    Array.from(recommendedCheckboxes).forEach(checkbox => {
        if (checkbox.checked) {
            checkbox.checked = false
        }
        else {
            checkbox.checked = true
        }
    });
});

const otherServicesSelectAll = document.getElementById("otherServicesSelectAll");
var otherServicesCheckboxes = document.getElementsByClassName("otherServicesCheckbox");

otherServicesSelectAll.addEventListener('change', function() {
    Array.from(otherServicesCheckboxes).forEach(checkbox => {
        if (checkbox.checked) {
            checkbox.checked = false
        }
        else {
            checkbox.checked = true
        }
    });
});

