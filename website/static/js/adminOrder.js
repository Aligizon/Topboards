"use strict";

class UserSelectManager {
    constructor() {
        this.guestUserInputs = document.getElementById("guest-user-inputs");
        this.userTable = document.getElementById("existing-user-table");
        this.userIDInput = document.getElementById("user_id");
        
        this.firstNameInput = this.guestUserInputs.querySelector("#first_name");
        this.lastNameInput = this.guestUserInputs.querySelector("#last_name");
        this.emailInput = this.guestUserInputs.querySelector("#email");
        this.phoneNumberInput = this.guestUserInputs.querySelector("#phone_number");

        this.nameRow = document.getElementById("user-name-col");
        this.emailRow = document.getElementById("user-email-col");
        this.phoneNumberRow = document.getElementById("user-phone-number-col");
        this.typeRow = document.getElementById("user-type-col");
        
        document.addEventListener("DOMContentLoaded", () => this.initializeUser());

        document.addEventListener("click", (event) => {
            if (event.target.closest(".user-row")) {
                this.selectUser(event);
            }
            else if (event.target.closest("#user-cancel-col")) {
                this.deselectUser(event);
            }
        });
    }

    initializeUser() {
        if (this.userIDInput.value) {
            const id = parseInt(this.userIDInput.value);
            const user = document.querySelector(`.user-row[data-id="${id}"]`);

            const firstName = user.getAttribute("data-firstName");
            const lastName = user.getAttribute("data-lastName");
            const email = user.getAttribute("data-email");
            const phoneNumber = user.getAttribute("data-phoneNumber");
            const type = user.getAttribute("data-userType");

            if (user) { // if user not a guest
                this.selectUserAfterInitialization(firstName, lastName, email, phoneNumber, type);  
            }
            else {
                this.firstNameInput.value = firstName;
                this.lastNameInput.value = lastName;
                this.emailInput.value = email;
                this.phoneNumberInput.value = phoneNumber;
            } 
        }
    }

    selectUserAfterInitialization(firstName, lastName, email, phoneNumber, type) {
        this.guestUserInputs.classList.add("d-none");
        this.userTable.classList.remove("d-none");

        this.updateUserTable(firstName, lastName, email, phoneNumber, type);
    }

    selectUser(event) {
        const clickedElement = event.target.closest(".user-row");

        const id = parseInt(clickedElement.getAttribute("data-id"));
        const firstName = clickedElement.getAttribute("data-firstName");
        const lastName = clickedElement.getAttribute("data-lastName");
        const email = clickedElement.getAttribute("data-email");
        const phoneNumber = clickedElement.getAttribute("data-phoneNumber");
        const type = clickedElement.getAttribute("data-userType");

        this.guestUserInputs.classList.add("d-none");
        this.userTable.classList.remove("d-none"); 

        this.updateUserTable(firstName, lastName, email, phoneNumber, type);

        this.userIDInput.value = parseInt(id);
    }

    deselectUser(event) {
        event.stopPropagation();

        this.updateUserTable();

        this.guestUserInputs.classList.remove("d-none");
        this.userTable.classList.add("d-none");

        this.userIDInput.value = "";
    }

    updateUserTable(firstName="", lastName="", email="", phoneNumber="", type="") {
        this.nameRow.innerText = firstName + " " + lastName;
        this.emailRow.innerText = email;
        this.phoneNumberRow.innerText = phoneNumber;
        this.typeRow.innerText = type;
    }
}

const userSelectManager = new UserSelectManager();

class ProductManager {

    constructor() {
        this.productsInput = document.getElementById("productID_productQuantity[]");
        this.productsTable = document.getElementById("order-products-table");
        // TODO: здесь добавить инициализацию taxes и subtotal
        this.insertRowsBeforeMe = document.getElementById("insert-product-rows-before-me");

        this.productsInputString = "";
        this.subTotalPrice = 0;
        this.minPriceForFreeShipping = 140;
        this.priceForCurrentShippingMethod = 7.9;
        
        document.addEventListener("DOMContentLoaded", () => this.initializeTable());

        document.addEventListener("click", (event) => {
            if (event.target.closest(".increase-quantity-button")) {
                this.increaseProductQuantity(event);
            }
            else if (event.target.closest(".decrease-quantity-button")) {
                this.decreaseProductQuantity(event);
            }
            else if (event.target.closest(".delete-from-order-button")) {
                this.deleteProduct(event);
            }
        });
    }

    initializeTable() {
        this.productsTable.classList.remove("d-none");
        
        let productsArray = [];
        if (this.productsInput.value) {
            this.productsTable.classList.remove("d-none");
            productsArray = JSON.parse(this.productsInput.value);

            for (let i = 0; i < productsArray.length; i++) {
                const productID = productsArray[i][0];
                const productQuantity = productsArray[i][1];
                this.addProductToTable(productID, productQuantity);
            }
        }   
    }

    addProductToTable(id, quantity) {
        const product = document.querySelector(`.product-quantity-div[data-id="${id}"]`);
        if (product) {
            const productCounterSpan = product.querySelector('.product-counter');
            const imageName = product.getAttribute("data-image-name");
            const name = product.getAttribute("data-name");
            const price = parseFloat(product.getAttribute("data-price"));
            const cost = parseFloat(product.getAttribute("data-cost"));

            let newProductHtml = `
            <tr class="new-product-row" data-product-id=${id}>
                <td class="p-0">
                    <div class="table-image-div">
                        <img src="${window.location.origin}/${resources.image_folder}/${imageName}" alt="">
                    </div>
                </td>
                <td class="prod-name-col">${name}</td>
                <td class="prod-quantity-col">${quantity}</td>
                <td class="prod-price-col">$${price}</td>
                <td class="prod-cost-col">$${cost}</td>
                <td class="prod-total-col">$${price * quantity}</td>
                <td>
                    <div class="d-flex justify-content-center align-items-center">
                        <img class="delete-from-order-button icon-s" src="${resources.cancel_icon}" alt="cancel">
                    </div>
                </td>
            </tr>`;

            this.insertRowsBeforeMe.insertAdjacentHTML("beforebegin", newProductHtml);
            productCounterSpan.innerText = quantity;
            this.calculateTotalPrice(price*quantity);
        }
    }

    increaseProductQuantity(event) {
        const clickedElement = event.target.closest(".product-quantity-div");
        const id = parseInt(clickedElement.getAttribute("data-id"));
        const imageName = clickedElement.getAttribute("data-image-name");
        const name = clickedElement.getAttribute("data-name");
        const price = parseFloat(clickedElement.getAttribute("data-price"));
        const cost = parseFloat(clickedElement.getAttribute("data-cost"));

        const productCounterSpan = clickedElement.querySelector('.product-counter');
        let counter = parseInt(productCounterSpan.innerText);
        
        if (counter === 99) {
            return;
        }

        counter += 1;

        if (counter === 1) {
            let newProductHtml = `
            <tr class="new-product-row" data-product-id=${id}>
                <td class="p-0">
                    <div class="table-image-div">
                        <img src="${window.location.origin}/${resources.image_folder}/${imageName}" alt="">
                    </div>
                </td>
                <td class="prod-name-col">${name}</td>
                <td class="prod-quantity-col">${counter}</td>
                <td class="prod-price-col">$${price}</td>
                <td class="prod-cost-col">$${cost}</td>
                <td class="prod-total-col">$${price}</td>
                <td>
                    <div class="d-flex justify-content-center align-items-center">
                        <img class="delete-from-order-button icon-s" src="${resources.cancel_icon}" alt="cancel">
                    </div>
                </td>
            </tr>`;
            this.insertRowsBeforeMe.insertAdjacentHTML("beforebegin", newProductHtml);
        }
        else {
            const product = document.querySelector(`.new-product-row[data-product-id="${id}"]`);
            product.querySelector(".prod-quantity-col").innerText = counter;
            product.querySelector(".prod-total-col").innerText = "$" + price * counter;
        }
        productCounterSpan.innerText = counter;

        this.calculateTotalPrice(price);
        this.modifyProductsInput(id, counter);        
    }


    decreaseProductQuantity(event) {
       
        const clickedElement = event.target.closest(".product-quantity-div");

        const id = parseInt(clickedElement.getAttribute("data-id"));
        const price = parseFloat(clickedElement.getAttribute("data-price"));

        const productCounterSpan = clickedElement.querySelector('.product-counter');
        let counter = parseInt(productCounterSpan.innerText);
        
        if (counter === 0) {
            return;
        }

        counter -= 1;

        const product = document.querySelector(`.new-product-row[data-product-id="${id}"]`);
        if (counter === 0) {
            product.remove();
        }
        else {
            product.querySelector(".prod-quantity-col").innerText = counter;
            product.querySelector(".prod-total-col").innerText = "$" + price * counter;
        }
        productCounterSpan.innerText = counter;

        this.calculateTotalPrice(-price);
        this.modifyProductsInput(id, counter);
    }

    deleteProduct(event) {
        const clickedElement = event.target.closest(".new-product-row");
        const id = parseInt(clickedElement.getAttribute("data-product-id"));
        const price = parseFloat(clickedElement.querySelector(".prod-price-col").innerText.substring(1));
        const quantity = parseInt(clickedElement.querySelector(".prod-quantity-col").innerText);

        const product = document.querySelector(`.new-product-row[data-product-id="${id}"]`);
        const productCounterSpan = document.querySelector(`.product-quantity-div[data-id="${id}"]`).querySelector('.product-counter');

        let counter = quantity;
        this.calculateTotalPrice(-price * counter);
        
        counter = 0;
        product.remove();
        productCounterSpan.innerText = counter;

        this.modifyProductsInput(id, counter);
    }

    calculateTotalPrice(price) {    
        const subTotalPriceCol = document.getElementById('sub-total-price-col');
        const shippingPriceCol = document.getElementById('shipping-price-col');
        const taxesPriceCol = document.getElementById('taxes-price-col');
        const totalPriceCol = document.getElementById('total-price-col');

        this.subTotalPrice = parseInt(subTotalPriceCol.innerText.substring(1)) + price;
        let shippingPrice = 0;

        if ((this.subTotalPrice !== 0) && (this.subTotalPrice < this.minPriceForFreeShipping)) {
            shippingPrice = this.priceForCurrentShippingMethod;
        }
        let totalPrice = this.subTotalPrice + shippingPrice;
    
        subTotalPriceCol.innerText = "$" + this.subTotalPrice;
        shippingPriceCol.innerText = "$" + shippingPrice;
        totalPriceCol.innerText = "$" + totalPrice;
    }

    modifyProductsInput(id, quantity) {

        let productsArray = [];

        if (this.productsInput.value) {
            productsArray = JSON.parse(this.productsInput.value);
        }

        let product = productsArray.find(subArray => subArray[0] === id);
        if (product) {
            if (quantity === 0) {
                productsArray.splice(productsArray.indexOf(product), 1);
            }
            else {
                product[1] = quantity;
            }
        }
        else {
            productsArray.push([id, quantity]);
        }
        this.productsInput.value = JSON.stringify(productsArray);
    }
}

const productManager = new ProductManager();
