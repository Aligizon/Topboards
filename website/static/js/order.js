const toggleSwitch = document.getElementById("same_billing_address");
const billingAddressInput = document.getElementById("billing-address");

toggleSwitch.addEventListener("change", function() {
    billingAddressInput.classList.toggle("d-none");
});