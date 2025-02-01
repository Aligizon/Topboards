"use strict";

class CartManager {
    constructor() {
        this.apiUrl=window.location.origin;
        
        this.cartOffcanvas = document.getElementById("offcanvasCart");
        this.bsOffcanvas = new bootstrap.Offcanvas(this.cartOffcanvas);

        this.cartItemsCounter = document.getElementById("cart-items-counter");
        this.cartList = document.getElementById("cart-list");
        
        this.totalAmount = 0.0;

        this.data;

        document.addEventListener("click", (event) => {
            if (event.target.closest(".decrease-item-quantity")) {
                this.decreaseItemQuantity(event);
            }
            else if (event.target.closest(".increase-item-quantity")) {
                this.increaseItemQuantity(event);
            }
        });
    }

    async addToCart(productID) {
        try {
            const response = await fetch(`/addToCart/${productID}`, {
                method: 'POST',
                headers: { 'contentType': 'application/json' },
            });

            this.data = await response.json();

            if (response.ok) {
                this.totalAmount = parseFloat(this.data.totalAmount);
                this.refreshCartUI(productID);
            }
        } catch (error) {
            console.error('Error adding product to cart:', error);
        }
    }

    async decreaseItemQuantity(event) {
        var productID = event.target.closest(".cart-item").getAttribute("data-product-id");
        try {
            const response = await fetch(`/decreaseCartItemQuantity/${productID}`, {
                method: 'POST',
                headers: { 'contentType': 'application/json' },
            });

            this.data = await response.json();
            
            if (response.ok) {
                this.totalAmount = parseFloat(this.data.totalAmount);
                this.refreshCartUI(productID);
            }
        } catch (error) {
            console.error('Error deleting product from cart:', error);
        }
    }

    async increaseItemQuantity(event) {
        var productID = event.target.closest(".cart-item").getAttribute("data-product-id");
        try {
            const response = await fetch(`/increaseCartItemQuantity/${productID}`, {
                method: 'POST',
                headers: { 'contentType': 'application/json' },
            });

            this.data = await response.json();
            console.log(this.data)
            if (response.ok) {
                this.totalAmount = parseFloat(this.data.totalAmount);
                this.refreshCartUI(productID);
            }
        } catch (error) {
            console.error('Error adding product to cart:', error);
        }
    }

    refreshCartUI(productID) {
        //Checking if cart state was changed
        if (this.data.wasEmpty) {
            this.showCart();
        }
        else if (this.data.isEmpty) {
            this.hideCart();
            return;
        }
        // Opening cart
        this.bsOffcanvas.show();
        const cartItem = document.querySelector(`[data-product-id="${productID}"]`);
        if (cartItem) {
            if (this.data.quantity == 0) {
                cartItem.remove();
            }
            else {
                var cartItemCounter = cartItem.querySelector('.item-quantity-counter');
                var cartItemPrice = cartItem.querySelector('.item-price');
                cartItemCounter.innerHTML = this.data.quantity;
                var price = new Decimal(this.data.price);
                var quantity = new Decimal(this.data.quantity);
                cartItemPrice.innerHTML = '$' + (price * quantity).toFixed(2);
            }
        }
        else {
            var newProduct = `<div class="cart-item mb-2" data-product-id="${productID}"}>
                        <div class="cart-item-img">
                            <img src="${this.apiUrl}/${this.data.imagePathName}"></img>
                        </div>
                        <div class="cart-item-description">
                            <div class="cart-item-total-price my-1">
                                <h6 class="item-price">$${parseInt(this.data.price)}</h6>
                            </div>
                            <div class="cart-item-name my-1">
                                <h6>${this.data.name} ${this.data.color}</h6>
                            </div>
                            <div class="product-quantity-div my-1">
                                <span>
                                    <h6 class="decrease-item-quantity"><</h6>
                                </span>
                                <span>
                                    <h6 class="item-quantity-counter">${this.data.quantity}</h6>
                                </span>
                                <span>
                                    <h6 class="increase-item-quantity">></h6>
                                </span>
                            </div>
                        </div>
                    </div>`;
            const newElement = document.createElement('div');
            newElement.innerHTML = newProduct;
            this.cartList.appendChild(newElement);
        }
        var cartTotalAmount = document.getElementById("cartTotalAmount");
        cartTotalAmount.innerText = (this.totalAmount.toFixed(2));
    }

    showCart() {
        var cart = `<div class="offcanvas-header">
                <h5 class="offcanvas-title" id="offcanvasCartLabel">Bag</h5>
                <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>

            <div class="offcanvas-body p-0">
                <div id="cart-list" class="mb-4">
                </div>

                <div class="cart-tab m-auto">
                    <h6 class="text-start my-2">Total amount: $<strong id="cartTotalAmount">0.00</strong></h6>
                    <a href="/checkout"><button class="cart-order my-2">to Checkout</button></a>
                    <button class="cart-close my-2" data-bs-dismiss="offcanvas">Continue shopping</button>
                </div>
            </div>`;

        this.cartOffcanvas.innerHTML = cart;
        this.cartList = document.getElementById("cart-list");
    }

    hideCart() {
        var cart = `<div class="offcanvas-header">
                <button type="button" class="ms-auto btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>
            <div class="offcanvas-body p-0">
                <div id="cart-list" class="mb-4">
                    <div class="my-3 mx-auto text-center">
                        <h3 class="my-2">Your bag is empty</h3>
                        <a class="my-2" href="/catalog">
                            <button class="product-button">
                                <h5>Go to Shop</h5>
                            </button>
                        </a>
                    </div>
                </div> 
            </div>`;

        this.cartOffcanvas.innerHTML = cart;
        this.cartList = document.getElementById("cart-list");
    }
}

let cartManager = new CartManager();
