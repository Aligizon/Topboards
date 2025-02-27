import urllib.parse
from flask import render_template, redirect, url_for, request, abort, flash, session, jsonify
from flask_login import current_user, login_required
from sqlalchemy.sql import func, text
from sqlalchemy.exc import NoResultFound
from ..model import db
from . import homeView
from ..model.models import Product, Product_image,\
                    User, User_address, UserType, Role,\
                    Shopping_session, Cart_item,\
                    Order_details, Order_items, ShippingMethod, ShippingMethodsPrices, PaymentMethod,\
                    Shipping_details, Payment_details, OrderStatus, Order_status_history
from decimal import Decimal
import urllib
from flask import current_app as app

from ..controller.user_validators import OrderForm, OrderUserDetailsForm


@homeView.before_request
def check_user():
    if is_admin_accessible(current_user):
        flash('You don\'t have permission to access this page', category='error')
        return redirect(url_for('adminView.home'))

def is_admin_accessible(user):
    return user.is_authenticated and user.role >= Role.Manager.value

#------------------------------Error handlers------------------------------#
@homeView.app_errorhandler(404)
def page_not_found(e):
    return render_template('page-404.html'), 404

@homeView.app_errorhandler(500)
def page_not_found(e):
    return render_template('page-500.html'), 500


@homeView.route('/')
def home():
    products = Product.query.order_by('id').filter(Product.is_enabled==True).all()
    return render_template('index.html', products=products)


@homeView.route('/catalog/mice')
def catalog_mice():
    products_query = Product.query.filter(Product.is_enabled==True, Product.category=='Mice').order_by('id')
    products = products_query.all()
    switches, brands, prices = createProductFilters(products)
    products_query = filterProducts(products_query, prices)
    return render_template('catalog.html', products=products_query.all(), switchesList=switches, brandsList=brands, prices=prices)

@homeView.route('/catalog/keyboards')
def catalog_keyboards():
    products_query = Product.query.filter(Product.is_enabled==True, Product.category=='Keyboards').order_by('id')
    products = products_query.all()
    switches, brands, prices = createProductFilters(products)
    products_query = filterProducts(products_query, prices)
    return render_template('catalog.html', products=products_query.all(), switchesList=switches, brandsList=brands, prices=prices)

@homeView.route('/catalog')
def catalog():
    products_query = Product.query.filter(Product.is_enabled==True).order_by('id')
    products = products_query.all()
    switches, brands, prices = createProductFilters(products)
    products_query = filterProducts(products_query, prices)
    return render_template('catalog.html', products=products_query.all(), switchesList=switches, brandsList=brands, prices=prices)


def createProductFilters(products):
    switches = set()
    brands = set()
    prices = dict()
    defaultMinPrice = 100000000
    defaultMaxPrice = 0

    if len(products) > 0:
        for product in products:
            if product.switches:
                switches.add(product.switches)
            if product.brand:
                brands.add(product.brand)
            if product.price < defaultMinPrice:
                defaultMinPrice = product.price
            if product.price > defaultMaxPrice:
                defaultMaxPrice = product.price
    else:
        defaultMinPrice = 0

    prices['defaultMinPrice'] = defaultMinPrice
    prices['defaultMaxPrice'] = defaultMaxPrice

    minPrice=defaultMinPrice
    maxPrice=defaultMaxPrice

    return switches, brands, prices

def filterProducts(products_query, prices):
    filters = request.args.to_dict(flat=False)
    productFilters = []

    if 'switches' in filters.keys():
        productFilters.append(Product.switches.in_(filters['switches']))
    if 'brand' in filters.keys():
        productFilters.append(Product.brand.in_(filters['brand']))
    if 'availability' in filters.keys():
        if filters['availability'][0] == 'available':
            productFilters.append(Product.quantity > 0)
    if '_from' in filters.keys():
        if filters['_from'] != '':
            try:
                minPrice = float(filters['_from'][0])
                productFilters.append(Product.price >= minPrice)
                prices['minPrice'] = minPrice
            except Exception as e:
                app.logger.error(f'Invalid minPrice value: {e}')
    if '_to' in filters.keys():
        if filters['_from'] != '':
            try:
                maxPrice = float(filters['_to'][0])
                productFilters.append(Product.price <= maxPrice)
                prices['maxPrice'] = maxPrice
            except Exception as e:
                app.logger.error(f'Invalid minPrice value: {e}')

    # if len(productFilters) > 0:
    for filter_condition in productFilters:
        products_query = products_query.filter(filter_condition)

        # products = Product.query.filter(*productFilters).order_by('id').all()
        # return products
    return products_query

@homeView.app_template_global()
def createMultipleChoiseFilterUrl(category, filter):
    filters = request.query_string.decode()
    if filter in request.args.getlist(category):
        filters = filters.replace(f"&{category}={urllib.parse.quote(filter)}", "")
        return f'{request.path}?{filters}'
    else:
        return f'{request.path}?{filters}&{category}={filter}'

@homeView.app_template_global()
def createSingleChoiseFilterUrl(category, filter):
    filters = request.args.to_dict(flat=False).copy()
    queryString = request.path + '?'

    if (category in filters.keys()):
        if (filter in filters[category]):
            filters.pop(category)
        else:
            filters[category] = filter
    else:
        filters[category] = filter

    for key, value in filters.items():
        if isinstance(value, list):
            for valueItem in value:
                queryString += f'&{key}={valueItem}'
        else:
            queryString += f'&{key}={value}'

    return queryString


@homeView.route('/productPage/<string:name>/<int:id>')
def product(name, id):
    selectedProduct = Product.query.filter_by(id=id, is_enabled=True).first_or_404()   
    products = Product.query.order_by('id').filter(Product.name==name, Product.is_enabled==True).all()
    colorFilters = dict()
    colorsHex = dict()
    switchesFilters = dict()

    for product in products:
        if product.color not in colorFilters.keys():
            colorFilters[product.color] = []
            colorFilters[product.color].append(product.switches)
        else:
            colorFilters[product.color].append(product.switches)

        if product.color_HEX not in colorsHex.keys():
            colorsHex[product.color] = product.color_HEX

        if product.switches not in switchesFilters.keys():
            switchesFilters[product.switches] = []
            switchesFilters[product.switches].append(product.color)
        else:
            switchesFilters[product.switches].append(product.color)

    return render_template('productPage.html', selectedProduct=selectedProduct, colorFilters=colorFilters, switchesFilters=switchesFilters, colorsHex=colorsHex)

@homeView.route('/productPage/<string:name>_<string:color>_<string:switches>')
def specify_product_by_color_and_switches(name, color, switches):
    selectedProduct = Product.query.filter(Product.name==name, Product.color==color, Product.switches==switches).first()
    if selectedProduct:
        return redirect(url_for('homeView.product', name=selectedProduct.name, id=selectedProduct.id))
    else:
        abort(404)

@homeView.route('/productPage/<string:name>_<string:color>_')
def specify_product_by_color(name, color):
    selectedProduct = Product.query.filter(Product.name==name, Product.color==color).first()
    return redirect(url_for('homeView.product', name=selectedProduct.name, id=selectedProduct.id))


@homeView.route('/addToCart/<int:id>', methods=['POST'])
def addToCart(id):
    if request.method == 'POST':
        product = Product.query.get_or_404(id)

        if (product.quantity == 0):
            return "This product is out of stock", 404
        
        uploadPath = app.config['UPLOAD_PATH'].split('/', 1)[1]
        productImage = Product_image.query.filter_by(product_id=id, is_main=True).first()
        productID = str(product.id)
        wasEmpty = False

        if current_user.is_authenticated:
            shopping_session = Shopping_session.query.filter_by(user_id = current_user.id).first()
            
            if not shopping_session or not shopping_session.cart_items:
                wasEmpty = True
            if not shopping_session:
                current_user.shopping_session = Shopping_session(total = Decimal('0.00'))

            cart_item = Cart_item.query.filter_by(session_id = current_user.shopping_session.id, product_id=id).first()
            if cart_item:
                if product.quantity == cart_item.quantity:
                    raise ValueError("Not enough products")
                cart_item.quantity += 1
                cart_item.modified_at=func.now()
            else:
                current_user.shopping_session.cart_items.append(Cart_item(product_id=product.id, quantity = 1, modified_at=func.now()))
            current_user.shopping_session.total += product.price

            db.session.commit()
            productQuantity = Cart_item.query.filter_by(session_id = current_user.shopping_session.id, product_id=id).first().quantity
            return jsonify({"name": product.name, "color": product.color, "price": product.price, "imagePathName": uploadPath + '/' + productImage.image_name, "quantity": productQuantity, "wasEmpty": wasEmpty, "totalAmount": current_user.shopping_session.total}), 200

        else:
            if 'cart' not in session:
                session['cart'] = {}
                session['cartTotalAmount'] = Decimal('0.00')
            
            cart = session['cart']
            if not cart:
                wasEmpty=True

            if productID in cart:
                if product.quantity == cart[productID]['quantity']:
                    raise ValueError("Not enough products")
                cart[productID]['quantity'] += 1
            else:
                cart[productID] = {"name": product.name,
                                   "color": product.color,
                                   "price": product.price,
                                   "switches": product.switches,
                                   "imageName": productImage.image_name,
                                   "quantity": 1}
            session['cartTotalAmount'] = Decimal(session.get('cartTotalAmount', '0.00')) + product.price

            session['cart'] = cart
            session.modified = True
            return jsonify({"name": product.name, "color": product.color, "price": product.price, "imagePathName": uploadPath + '/' + productImage.image_name, "quantity": session['cart'][productID]["quantity"], "wasEmpty": wasEmpty, "totalAmount": session['cartTotalAmount']}), 200

@homeView.route('/increaseCartItemQuantity/<int:id>', methods=['POST'])
def increaseCartItemQuantity(id):
    if request.method == 'POST':
        product = Product.query.get_or_404(id)
        productID = str(product.id)

        if current_user.is_authenticated:
            shopping_session = Shopping_session.query.filter_by(user_id = current_user.id).first()
            if not shopping_session:
                raise KeyError(f"Shopping session wasn't found")

            cart_item = Cart_item.query.filter_by(session_id = current_user.shopping_session.id, product_id=id).first()
            if cart_item:
                if product.quantity == cart_item.quantity:
                    raise ValueError("Not enough products")
                cart_item.quantity += 1
                cart_item.modified_at=func.now()
                current_user.shopping_session.total += product.price
            else:
                raise KeyError(f"Cart item with id {product.id} wasn't found")
            db.session.commit()
            productQuantity = Cart_item.query.filter_by(session_id = current_user.shopping_session.id, product_id=id).first().quantity
            return jsonify({"price": product.price, "quantity": productQuantity, "totalAmount": current_user.shopping_session.total}), 200
        else:
            cart = session['cart']
            if productID in cart:
                if product.quantity == cart[productID]['quantity']:
                    raise ValueError("Not enough products")
                cart[productID]['quantity'] += 1
                session['cartTotalAmount'] = Decimal(session.get('cartTotalAmount', '0.00')) + product.price
            else:
                raise KeyError(f"Product with id {productID} wasn't found")
            
            session['cart'] = cart
            session.modified = True
        
        return jsonify({"price": product.price, "quantity": session['cart'][productID]["quantity"], "totalAmount": session['cartTotalAmount']}), 200

@homeView.route('/decreaseCartItemQuantity/<int:id>', methods=['GET', 'POST'])
def decreaseCartItemQuantity(id):
    if request.method == 'POST':
        product = Product.query.get_or_404(id)
        productID = str(product.id)
        isEmpty = False
        
        if current_user.is_authenticated:
            shopping_session = Shopping_session.query.filter_by(user_id = current_user.id).first()
            if not shopping_session:
                raise KeyError(f"Shopping session wasn't found")

            cart_item = Cart_item.query.filter_by(session_id = current_user.shopping_session.id, product_id=id).first()
            if cart_item:
                cart_item.quantity -= 1
                cart_item.modified_at=func.now()
                current_user.shopping_session.total -= product.price
                if cart_item.quantity <= 0:
                    db.session.delete(cart_item)
                    # ПРОТЕСТИТЬ
                    if not shopping_session.cart_items:
                        isEmpty=True
            else:
                raise KeyError(f"Product with id {productID} wasn't found")
            db.session.commit()

            cart_item = Cart_item.query.filter_by(session_id = current_user.shopping_session.id, product_id=id).first()
            if cart_item:
                return jsonify({"price": product.price, "quantity": cart_item.quantity, "totalAmount": current_user.shopping_session.total}), 200
            else:
                return jsonify({"quantity": 0, "isEmpty": isEmpty, "totalAmount": current_user.shopping_session.total}), 200
            
        else:
            cart = session['cart']
            if productID in cart:
                cart[productID]['quantity'] -= 1
                if cart[productID]['quantity'] <= 0:
                    cart.pop(productID)
            else:
                raise KeyError(f"Product with id {productID} wasn't found")
            session['cartTotalAmount'] = Decimal(session.get('cartTotalAmount', '0.00')) - product.price
            session['cart'] = cart
            session.modified = True

            if session['cart'].get(productID, None):
                return jsonify({"price": product.price, "quantity": session['cart'][productID]["quantity"], "totalAmount": session['cartTotalAmount']}), 200
            else:
                if (not session['cart']):
                    isEmpty = True
                return jsonify({ "quantity": 0, "isEmpty": isEmpty, "totalAmount": session['cartTotalAmount']}), 200

@homeView.route('/thanks', methods=['GET', 'POST'])
def thanks():
    return render_template('order_complete.html')

@homeView.route('/checkout', methods=['GET', 'POST'])
def checkout():
    try:
        if (current_user.is_authenticated):
            if (not current_user.shopping_session or not current_user.shopping_session.cart_items):
                flash('Your cart is empty', category='error')
                raise NoResultFound("Can't create an order with empty cart") 
        else:
            if not session.get('cart'):
                flash('Your cart is empty', category='error')
                raise NoResultFound("Can't create an order with empty cart")
    except Exception as e:
        app.logger.error(f"No cart items were found: {e}")
        flash('Your cart is empty', category='error')
        return redirect(url_for('homeView.home'))

    if not current_user.is_authenticated:
        form = OrderUserDetailsForm() 
    else:
        form = OrderForm()

    if request.method == 'POST': 
        try:   
            if form.validate_on_submit():
                if not current_user.is_authenticated:
                    firstName = form.firstName.data
                    lastName = form.lastName.data
                    email = form.email.data
                    phoneNumber = form.phoneNumber.data
                country = form.country.data
                shippingAddressLine1 = form.shippingAddressLine1.data
                shippingAddressLine2 = form.shippingAddressLine2.data
                shippingAddressCity = form.shippingAddressCity.data
                shippingAddressPostalCode = form.shippingAddressPostalCode.data
                shipping_method = form.shipping_method.data
                payment_method = form.payment_method.data
                sameBillingAddress = form.sameBillingAddress.data
                if not sameBillingAddress:
                    billingAddressLine1 = form.billingAddressLine1.data
                    billingAddressLine2 = form.billingAddressLine2.data
                    billingAddressCity = form.billingAddressCity.data
                    billingAddressPostalCode = form.billingAddressPostalCode.data

                shippingMethodPrice = ShippingMethodsPrices.query.filter_by(shipping_method_id=shipping_method).first() 
                additionalShippingCost = 0

                if not shippingMethodPrice:
                    raise ValueError(f"No shipping method price found for ID: {shipping_method}")

                current_status = OrderStatus.Pending.value
                notify = True
                statusComment = "thank you for your order at Topboards!"

                newOrder = Order_details(
                            sub_total = Decimal('0.00'),
                            shipping_cost = shippingMethodPrice.price + additionalShippingCost,
                            taxes_cost = Decimal('0.00'),
                            total_cost = Decimal('0.00'),
                            payment_details=Payment_details(method=payment_method),
                            shipping_details=Shipping_details(method=shipping_method, price = shippingMethodPrice.price + additionalShippingCost, estimated_delivery_time=func.now() + text("INTERVAL '7 days'")),
                            current_status = current_status,
                            modified_at = func.now())

                newOrder.status_history.append(Order_status_history(new_status=current_status, customer_notified=notify, comment=statusComment, modified_at = func.now())),
            
                if current_user.is_authenticated:
                    shopping_session = Shopping_session.query.filter_by(user_id=current_user.id).first()
                    
                    if (shopping_session.cart_items):

                        newOrder.user_id = current_user.id
                        userShippingAddresses = User_address.query.filter_by(user_id=current_user.id)\
                                            .filter(User_address.address_line_1==shippingAddressLine1, User_address.address_line_2==shippingAddressLine2, User_address.city==shippingAddressCity, User_address.postal_code==shippingAddressPostalCode, User_address.country==country).first()
                        if userShippingAddresses:
                            newOrder.shipping_details.shipping_address_id = userShippingAddresses.id
                        else:
                            newShippingAddress = User_address(address_line_1=shippingAddressLine1,
                                                            address_line_2=shippingAddressLine2,
                                                            city=shippingAddressCity,
                                                            postal_code=shippingAddressPostalCode,
                                                            country=country)
                            newShippingAddress.user_id = current_user.id
                            newOrder.shipping_details.shipping_address = newShippingAddress
                        
                        if sameBillingAddress:
                            newOrder.payment_details.billing_address = newShippingAddress
                        else:
                            newBillingAddress = User_address(address_line_1=billingAddressLine1,
                                                                address_line_2=billingAddressLine2,
                                                                city=billingAddressCity,
                                                                postal_code=billingAddressPostalCode,
                                                                country=country)
                            newBillingAddress.user_id = current_user.id
                            newOrder.payment_details.billing_address = newBillingAddress

                        for cartItem in shopping_session.cart_items:
                            productToAdd = Product.query.get(cartItem.product_id)
                            quantity = cartItem.quantity
                            if (productToAdd.quantity < quantity):
                                raise ValueError("Not enough items with id {productToAdd.id}")
                            newOrder.sub_total += (productToAdd.cost * quantity)
                            newOrder.taxes_cost += ((productToAdd.price-productToAdd.price_without_tax) * quantity)
                            newOrder.total_cost += (productToAdd.price_without_tax * quantity)
                            orderItem = Order_items(product_id=productToAdd.id, quantity=quantity, modified_at=func.now())
                            newOrder.order_items.append(orderItem)
                            db.session.delete(cartItem)

                        newOrder.total_cost += (newOrder.taxes_cost + newOrder.shipping_cost)
                        db.session.delete(shopping_session)
                    else:
                        db.session.rollback()
                        flash('Your cart is empty', category='error')
                        return redirect(url_for('homeView.home'))

                        # raise NoResultFound("Can't create an order with empty cart")
                else:
                    if session.get('cart'):
                        existingUser = User.query.filter_by(email=email).first()
                        if existingUser:
                            newOrder.user = existingUser
                        else:
                            newOrder.user = User(role=Role.Customer.value,
                                                    type=UserType.Guest.value,
                                                    first_name=firstName,
                                                    last_name=lastName,
                                                    email=email,
                                                    phone_number=phoneNumber,
                                                    is_enabled=True)
                        
                        newShippingAddress = User_address(address_line_1=shippingAddressLine1,
                                                            address_line_2=shippingAddressLine2,
                                                            city=shippingAddressCity,
                                                            postal_code=shippingAddressPostalCode,
                                                            country=country)
                        newOrder.shipping_details.shipping_address = newShippingAddress

                        if sameBillingAddress:
                            newOrder.payment_details.billing_address = newShippingAddress
                        else:
                            if ((billingAddressLine1 == newOrder.shipping_details.shipping_address.address_line_1) and (billingAddressLine2 == newOrder.shipping_details.shipping_address.address_line_2) and (billingAddressCity == newOrder.shipping_details.shipping_address.city) and (billingAddressPostalCode == newOrder.shipping_details.shipping_address.postal_code)):
                                newOrder.payment_details.billing_address = newOrder.shipping_details.shipping_address
                            else:
                                newBillingAddress = User_address(address_line_1=billingAddressLine1,
                                                            address_line_2=billingAddressLine2,
                                                            city=billingAddressCity,
                                                            postal_code=billingAddressPostalCode,
                                                            country=country)
                                newOrder.payment_details.billing_address = newBillingAddress

                        for cartItemId, cartItem in session.get('cart').items():
                            productToAdd = Product.query.get(cartItemId)
                            if productToAdd is None:
                                raise NoResultFound("Product with id={productId} wasn't found")
                            if (productToAdd.quantity < cartItem['quantity']):
                                raise ValueError("Not enough items with id {productToAdd.id}")
                            quantity = cartItem['quantity']
                            newOrder.sub_total += (productToAdd.cost * quantity)
                            newOrder.taxes_cost += ((productToAdd.price-productToAdd.price_without_tax) * quantity)
                            newOrder.total_cost += (productToAdd.price_without_tax * quantity)
                            orderItem = Order_items(product_id=cartItemId, quantity=quantity, modified_at=func.now())
                            newOrder.order_items.append(orderItem)
                        
                        newOrder.total_cost += (newOrder.taxes_cost + newOrder.shipping_cost)
                        session.pop('cart', None)
                    else:
                        db.session.rollback()
                        flash('Your cart is empty', category='error')
                        return redirect(url_for('homeView.home'))
                        # raise NoResultFound("Can't create an order with empty cart")

                db.session.add(newOrder)
                db.session.commit()
                flash('Order created!', category='success')
                return redirect(url_for('homeView.thanks'))
            
            else:
                for f, e in form.errors.items():
                    flash(f + ': '  + e[0], category='error')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"An error occurred: {e}")
            flash('An error occurred', category='error')
            return redirect(url_for('homeView.home'))
    
    return render_template('order.html', form=form, ShippingMethod=ShippingMethod, PaymentMethod=PaymentMethod)