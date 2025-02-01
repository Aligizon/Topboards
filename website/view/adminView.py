from decimal import Decimal
from flask import render_template, redirect, url_for, request, flash, current_app as app
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound, IntegrityError
from flask_login import current_user
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.sql import func, text
import psycopg2
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from . import adminView
from ..model import db
from ..model.models import Product, Product_image,\
                    Design_categories,\
                    User, Role, UserType, User_address,\
                    Order_details, Order_items, Order_status_history, OrderStatus,\
                    Payment_details, PaymentMethod,\
                    Shipping_details, ShippingMethod, ShippingMethodsPrices
import json
import shutil
import re

@adminView.before_request
def check_user():
    if not is_admin_accessible(current_user):
        flash('You don\'t have permission to access this page', category='error')
        return redirect(url_for('adminAuth.adminLogin'))
    

def is_admin_accessible(user):
    return user.is_authenticated and user.role >= Role.Manager.value


#------------------------------Home page------------------------------#

@adminView.route('/')
def home():
    orders = Order_details.query.all()
    total_sum = sum(order.total_cost - order.taxes_cost - order.shipping_cost - order.sub_total for order in orders if order.current_status == OrderStatus.Completed.value)
    users = len(User.query.filter_by(role = Role.Customer.value).all())
    return render_template('admin/admin.html', orders=orders, total_sum=total_sum, users=users, orderStatus=OrderStatus)

#------------------------------Catalog page------------------------------#
@adminView.route('/catalog', methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        product_main_image = request.files.get('prod_main_image')
        product_additional_images = request.files.getlist('product_img[]')
        productName = request.form.get('_name')
        description = request.form.get('_description')
        model = request.form.get('_model')
        category = request.form.get('_category')
        brand = request.form.get('_brand')
        switches = request.form.get('_switches')
        color = request.form.get('_color')
        color_HEX = request.form.get('_color_HEX')
        sku = request.form.get('_SKU')
        quantity = request.form.get('_quantity')
        formFactor = request.form.get('_formFactor')
        dimensions = request.form.get('_dimensions')
        weight = request.form.get('_weight')
        price = request.form.get('_price')
        withoutTax = request.form.get('_withoutTax')
        cost = request.form.get('_cost')
        isEnabled = request.form.get('_isEnabled')

        try:
            isEnabled = int(isEnabled)
            if not(isinstance(isEnabled, int)):
                flash('You must specify if product is enabled', category='error')
                return redirect(url_for('adminView.catalog'))
        except:
            flash('You must specify if product is enabled', category='error')
            return redirect(url_for('adminView.catalog'))
        
        pattern = r'^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$'
  
        if product_main_image.filename == '':
            flash('Main image must be uploaded', category='error')   
        elif len(productName) < 2:
            flash('Name must be specified', category='error')
        elif len(model) < 2:
            flash('Model name must be specified', category='error')
        elif len(category) < 2:
            flash('Category name must be specified', category='error')
        elif len(brand) < 2:
            flash('Brand name must be specified', category='error')
        elif len(color) < 2:
            flash('Product color must be specified', category='error')
        elif not re.match(pattern, color_HEX):
            flash('Enter valid HEX color', category='error')
        elif len(quantity) < 1:
            flash('Quantity must be specified', category='error')
        elif len(price) < 1:
            flash('Price must be specified', category='error')
        elif len(cost) < 1:
            flash('Cost must be specified', category='error')
        else:
            new_product = Product(
                name=productName,
                desc=description,
                model=model,
                category=category,
                brand=brand,
                switches=switches,
                color=color,
                color_HEX=color_HEX,
                SKU=sku,
                quantity=quantity,
                form_factor=formFactor,
                dimensions=dimensions,
                weight=weight,
                cost=cost,
                price_without_tax=withoutTax,
                price=price,
                is_enabled=isEnabled)
            
            try:
                # MAIN IMAGE UPLOAD
                ''' appends a unique identifier to an image '''
                unique_str = str(uuid.uuid4())[:8]
                product_main_image.filename = f"{unique_str}_{product_main_image.filename}"
                
                '''handling file uploads'''
                filename = secure_filename(product_main_image.filename)
                if filename:
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                            flash('File type not supported', category='error')
                            return redirect(url_for('adminView.catalog'))
                    product_main_image.save(os.path.join(app.config["UPLOAD_PATH"], filename))
                    new_product.product_images.append(Product_image(image_name=filename, is_main = True))

                # ADDITIONAL IMAGES UPLOAD
                if product_additional_images[0].filename != '':
                    for image in product_additional_images:
                        ''' appends a unique identifier to an image '''
                        unique_str = str(uuid.uuid4())[:8]
                        image.filename = f"{unique_str}_{image.filename}"

                        '''handling file uploads'''
                        filename = secure_filename(image.filename)
                        if filename:
                            file_ext = os.path.splitext(filename)[1]
                            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                                    flash('File type not supported', category='error')
                                    return redirect(url_for('adminView.catalog'))
                            image.save(os.path.join(app.config["UPLOAD_PATH"], filename))
                            new_product.product_images.append(Product_image(image_name=filename, is_main = False))

                db.session.add(new_product)
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Error while adding images: {e}')
                flash('An error occurred', category='error')
                return redirect(url_for('adminView.catalog'))

            db.session.commit()
            flash('Product was added', category='success')

    products = Product.query.order_by('id').all()
    return render_template('admin/catalog/admin_catalog.html', products=products)

#------------------------------Add product window------------------------------#
@adminView.route('/product/update/<int:id>', methods=['GET', 'POST'])
def product_update(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product_main_image = request.files.get('prod_main_image')
        product_additional_images = request.files.getlist('product_img[]')
        productName = request.form.get('_name')
        description = request.form.get('_description')
        model = request.form.get('_model')
        category = request.form.get('_category')
        brand = request.form.get('_brand')
        switches = request.form.get('_switches')
        color = request.form.get('_color')
        color_HEX = request.form.get('_color_HEX')
        sku = request.form.get('_SKU')
        quantity = request.form.get('_quantity')
        formFactor = request.form.get('_formFactor')
        dimensions = request.form.get('_dimensions')
        weight = request.form.get('_weight')
        price = request.form.get('_price')
        withoutTax = request.form.get('_withoutTax')
        cost = request.form.get('_cost')
        isEnabled = request.form.get('_isEnabled')

        try:
            isEnabled = int(isEnabled)
        except:
            flash('You must specify if product is enabled', category='error')
            return redirect(url_for('adminView.catalog'))
        
        pattern = r'^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$'

        if len(productName) < 2:
            flash('Name must be specified', category='error')
        elif len(model) < 2:
            flash('Model name must be specified', category='error')
        elif len(category) < 2:
            flash('Category name must be specified', category='error')
        elif len(brand) < 2:
            flash('Brand name must be specified', category='error')
        elif len(color) < 2:
            flash('Product color must be specified', category='error')
        elif not re.match(pattern, color_HEX):
            flash('Enter valid HEX color', category='error')
        elif len(quantity) < 1:
            flash('Quantity must be specified', category='error')
        elif len(price) < 1:
            flash('Price must be specified', category='error')
        elif len(cost) < 1:
            flash('Cost must be specified', category='error')
        else:
            product.name=productName
            product.desc=description
            product.model=model
            product.category=category
            product.brand=brand
            product.switches=switches
            product.color=color
            product.color_HEX=color_HEX
            product.SKU=sku
            product.quantity=quantity
            product.form_factor=formFactor
            product.dimensions=dimensions
            product.weight=weight
            product.cost=cost
            product.price=price
            product.price_without_tax=withoutTax
            product.is_enabled=isEnabled
            product.modified_at = func.now()

            #images editing
            try:
                # main image update
                if product_main_image.filename != '':   
                    ''' appends a unique identifier to an image '''
                    unique_str = str(uuid.uuid4())[:8]
                    product_main_image.filename = f"{unique_str}_{product_main_image.filename}"

                    '''handling file uploads'''
                    filename = secure_filename(product_main_image.filename)
                    if filename:
                        file_ext = os.path.splitext(filename)[1]
                        if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                            flash('Main image wasn\'t updated (file type not supported)', category='error')
                        else:
                            product_main_image.save(os.path.join(app.config["UPLOAD_PATH"], filename))
                            old_main_image = Product_image.query.filter(Product_image.product_id==id, Product_image.is_main==True).first()
                            print(old_main_image.image_name)
                            os.remove(os.path.join(app.config["UPLOAD_PATH"], old_main_image.image_name))
                            old_main_image.image_name = filename
                            print(old_main_image.image_name)

                # additional images update
                if product_additional_images[0].filename != '':
                    old_product_additional_images = Product_image.query.filter(Product_image.product_id==id, Product_image.is_main==False).all()

                    for image in old_product_additional_images:
                        imagePath = image.image_name
                        os.remove(os.path.join(app.config["UPLOAD_PATH"], imagePath))
                        db.session.delete(image)
                   
                    for image in product_additional_images:
                        ''' appends a unique identifier to an image '''
                        unique_str = str(uuid.uuid4())[:8]
                        image.filename = f"{unique_str}_{image.filename}"

                        '''handling file uploads'''
                        filename = secure_filename(image.filename)
                        if filename:
                            file_ext = os.path.splitext(filename)[1]
                            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                                    flash('File type not supported', category='error')
                                    return redirect(url_for('adminView.catalog'))
                            image.save(os.path.join(app.config["UPLOAD_PATH"], filename))
                            product.product_images.append(Product_image(image_name=filename, is_main = False))
            
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Error while editing images: {e}')
                flash('An error occurred', category='error')
                return redirect(url_for('adminView.catalog'))
            
            db.session.commit()
            flash('Product was edited', category='success')

        return redirect(url_for('adminView.catalog'))

    return render_template('admin/catalog/admin_product.html', product=product)

@adminView.route('/product/copy/<int:id>')
def product_copy(id):
    product = Product.query.get_or_404(id)
    new_product = Product(
                name=product.name,
                desc=product.desc,
                model=product.model,
                category=product.category,
                brand=product.brand, 
                switches=product.switches,
                color=product.color,
                color_HEX=product.color_HEX,
                SKU=product.SKU,
                quantity=product.quantity,
                form_factor=product.form_factor,
                dimensions=product.dimensions,
                weight=product.weight,
                cost=product.cost,
                price_without_tax=product.price_without_tax,
                price=product.price,
                is_enabled=False)
    
    for image in product.product_images:
        new_product.product_images.append(Product_image(image_name=image.image_name, is_main = image.is_main))
    
    try:
        for i in range(len(new_product.product_images)):
            ''' appends a unique identifier to an image '''
            unique_str = str(uuid.uuid4())[:8]
            new_product.product_images[i].image_name = f"{unique_str}_{new_product.product_images[i].image_name}"

            new_filename =  new_product.product_images[i].image_name
            old_filename =  product.product_images[i].image_name
            shutil.copyfile(os.path.join(app.config["UPLOAD_PATH"])+ '/' + old_filename, os.path.join(app.config["UPLOAD_PATH"])+ '/' + new_filename)
            db.session.add(new_product)

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error while copying product images: {e}')
        flash('Can\'t copy this product', category='error')
        return redirect(url_for('adminView.catalog'))
    
    db.session.commit()
    return redirect(url_for('adminView.catalog'))

@adminView.route('/product/delete/<int:id>')
def product_delete(id):
    product = Product.query.get_or_404(id)
    product_images = Product_image.query.filter(Product_image.product_id==id).all()
    try:
        for img in product_images:
            imagePath = img.image_name
            try:
                os.remove(os.path.join(app.config["UPLOAD_PATH"], imagePath))
            except:
                flash('File not found on the server', category='error')
            db.session.delete(img)

        db.session.delete(product)

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error while deleting images: {e}')
        flash('An error occurred', category='error')

    db.session.commit()
    return redirect(url_for('adminView.catalog'))

@adminView.route('/product')
def product():
    return render_template('admin/catalog/admin_product.html')

#------------------------------Main page categories------------------------------#
@adminView.route('/categories', methods=['GET', 'POST'])
def categories():
    minCategoriesLength = 3
    maxCategoriesLength = 6

    allCategories = Design_categories.query.order_by('id').all()
    currentCategoriesLength = len(allCategories)

    if currentCategoriesLength != maxCategoriesLength:
        try:
            if currentCategoriesLength > maxCategoriesLength:
                Design_categories.query.filter(Design_categories.id > 6).delete()
            for i in range(currentCategoriesLength, maxCategoriesLength):
                db.session.add(Design_categories(name=f'Category {i+1}' if i < 3 else ''))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred', category='error')
            app.logger.error(f"Error adjusting categories: {e}")
            return redirect(url_for('adminView.categories'))
        db.session.commit()

    if request.method == 'POST':

        if current_user.role <  Role.Admin.value:
            flash('You don\'t have permission to modify design of the website', category='error')
            return redirect(url_for('adminView.categories'))

        categories = request.form.getlist('_category[]')
        categories = [x for x in categories if x.strip()]

        if minCategoriesLength <= len(categories) <= maxCategoriesLength:
            try:
                categories.extend([''] * (maxCategoriesLength - len(categories)))
            except Exception as e:
                app.logger.error(f'Error while filling an array of categories: {e}')
                flash("An error occurred", category="error")
            try:
                for i, category in enumerate(categories):
                    if len(category) > 2 or category == '':
                        if len(category) < 19:
                            allCategories[i].name = category
                        else:
                            db.session.rollback()
                            flash("Category name length must be 18 symbols or less", category="error")
                            return redirect(url_for('adminView.categories'))
                    else:
                        flash("Category name is invalid", category="error")
            except Exception as e:
                db.session.rollback()
                flash("An error occurred", category="error")
                return redirect(url_for('adminView.categories'))
            db.session.commit()

        else:
            flash('You can\'t have less than 3 categories', category='error')

    categories = Design_categories.query.order_by('id').all()
    return render_template('admin/design/admin_categories.html', categories=categories)

#------------------------------Main page sliders------------------------------#
@adminView.route('/mainPageConstructor')
def mainPageConstructor():
    products = Product.query.filter(Product.is_enabled == True).order_by('id').all()
    return render_template('admin/design/admin_mainPage.html', products = products)

#------------------------------1st slider------------------------------#
@adminView.route('/mainPageConstructor/mainSlider', methods=['GET', 'POST'])
def mainSlider():
    if request.method == 'POST':
        mainSliderProducts = request.form.getlist("is_main_category[]")
        try:
            products = Product.query.filter(Product.id.in_(mainSliderProducts)).all()
            for product in products:
                product.is_main_category = True
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error occurred while adding category to products: {e}')
            flash('An error occurred', category='error')
        db.session.commit()

    return redirect(url_for('adminView.mainPageConstructor'))

@adminView.route('/mainPageConstructor/mainSlider/delete/<int:id>')
def mainSlider_delete(id):
    product = Product.query.filter(Product.id==id).first()
    try:
        product.is_main_category = False
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        flash('An error occurred', category='error')
    db.session.commit()

    return redirect(url_for('adminView.mainPageConstructor'))

#------------------------------2nd slider------------------------------#
@adminView.route('/mainPageConstructor/newAdded', methods=['GET', 'POST'])
def newAdded():
    if request.method == 'POST':
        newAddedProducts = request.form.getlist("is_new_category[]")
        try:
            products = Product.query.filter(Product.id.in_(newAddedProducts)).all()
            for product in products:
                product.is_new_category = True
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error occurred while adding category to products: {e}')
            flash('An error occurred', category='error')
        db.session.commit()

    return redirect(url_for('adminView.mainPageConstructor'))

@adminView.route('/mainPageConstructor/newAdded/delete/<int:id>')
def newAdded_delete(id):
    product = Product.query.filter(Product.id==id).first()
    try:
        product.is_new_category = False
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        flash('An error occurred', category='error')
    db.session.commit()

    return redirect(url_for('adminView.mainPageConstructor'))

#------------------------------3rd slider------------------------------#
@adminView.route('/mainPageConstructor/recommended', methods=['GET', 'POST'])
def recommended():
    if request.method == 'POST':
        recommendedProducts = request.form.getlist("is_recommended_category[]")
        try:
            products = Product.query.filter(Product.id.in_(recommendedProducts)).all()
            for product in products:
                product.is_recommended_category = True
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error occurred while adding category to products: {e}')
            flash('An error occurred', category='error')
        db.session.commit()

    return redirect(url_for('adminView.mainPageConstructor'))

@adminView.route('/mainPageConstructor/recommended/delete/<int:id>')
def recommended_delete(id):
    product = Product.query.filter(Product.id==id).first()
    try:
        product.is_recommended_category = False
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        flash('An error occurred', category='error')
    db.session.commit()

    return redirect(url_for('adminView.mainPageConstructor'))

#------------------------------4th slider------------------------------#
@adminView.route('/mainPageConstructor/otherServices', methods=['GET', 'POST'])
def otherServices():
    if request.method == 'POST':
        otherServicesProducts = request.form.getlist("is_otherServices_category[]")
        try:
            products = Product.query.filter(Product.id.in_(otherServicesProducts)).all()
            for product in products:
                product.is_otherServices_category = True
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error occurred while adding category to products: {e}')
            flash('An error occurred', category='error')
        db.session.commit()

    return redirect(url_for('adminView.mainPageConstructor'))

@adminView.route('/mainPageConstructor/otherServices/delete/<int:id>')
def otherServices_delete(id):
    product = Product.query.filter(Product.id==id).first()
    try:
        product.is_otherServices_category = False
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        flash('An error occurred', category='error')
    db.session.commit()

    return redirect(url_for('adminView.mainPageConstructor'))

#------------------------------Orders------------------------------#
@adminView.route('/orders', methods=['GET', 'POST'])
def orders():
    orders = Order_details.query.order_by(desc(Order_details.id)).all()
    return render_template('admin/orders/admin_orders.html', orders=orders)

@adminView.route('/order/update/<int:id>', methods=['GET', 'POST'])
def order(id):
    if request.method == 'POST':
        try:
            payment_method = int(request.form.get('_payment_method'))
            shipping_method = int(request.form.get('_shipping_method'))
        except Exception as e:
            app.logger.error(e)
            flash('An error occurred', category='error')
        try:
            userID = int(request.form.get('_userId'))
            if (not User.query.get(userID)):
                raise KeyError(f"User with id {userID} doesn't exist")
        except Exception as e:
            userID = None

        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        email = request.form.get('_email')
        phoneNumber = request.form.get('_phoneNumber')
        billingAddressLine1 = request.form.get('_billing_address_line_1')
        billingAddressLine2 = request.form.get('_billing_address_line_2')
        billingAddressCity = request.form.get('_billing_address_city')
        billingAddressPostalCode = request.form.get('_billing_address_postal_code')
        billingAddressCountry = request.form.get('_billing_address_country')
        shippingAddressLine1 = request.form.get('_shipping_address_line_1')
        shippingAddressLine2 = request.form.get('_shipping_address_line_2')
        shippingAddressCity = request.form.get('_shipping_address_city')
        shippingAddressPostalCode = request.form.get('_shipping_address_postal_code')
        shippingAddressCountry = request.form.get('_shipping_address_country')
        productsString = request.form.get('_productID_productQuantity[]')
        if productsString:
            productsList = json.loads(productsString)
        try:
            currentStatus = int(request.form.get('_status_update_new_status'))
        except ValueError:
            currentStatus = None
        notify = bool(request.form.get('_status_update_notify'))
        statusComment = request.form.get('_status_update_comment')

        if (not payment_method in PaymentMethod._value2member_map_):
            flash('Payment method must be selected', category='error')
        elif (not shipping_method in ShippingMethod._value2member_map_):
            flash('Shipping method must be selected', category='error')
        elif (currentStatus and not currentStatus in OrderStatus._value2member_map_):
            flash('Invalid order status', category='error')
        elif (userID == ''):
            if (firstName == '' or lastName == '' or email == '' or phoneNumber == ''):
                flash('User info must be filled', category='error')
        elif (shippingAddressLine1 == '' or shippingAddressLine2 == '' or shippingAddressCity == '' or shippingAddressPostalCode == '' or shippingAddressCountry == ''):
            flash('Shipping address must be filled', category='error')
        elif (not productsList):
            flash('Products must be selected', category='error')
        else:
            order = Order_details.query.get_or_404(id)
            shippingMethodPrice = ShippingMethodsPrices.query.filter_by(shipping_method_id=shipping_method).first() 
            additionalShippingCost = Decimal('0.00')

            if not shippingMethodPrice:
                raise ValueError(f"No shipping method price found for ID: {shipping_method}")

            order.shipping_cost = shippingMethodPrice.price + additionalShippingCost
            order.payment_details.method=payment_method
            order.shipping_details.method=shipping_method
            order.shipping_details.price = shippingMethodPrice.price + additionalShippingCost

            if (currentStatus and currentStatus != order.current_status):
                order.current_status = currentStatus
                order.status_history.append(Order_status_history(new_status=currentStatus, customer_notified=notify, comment=statusComment, modified_at=func.now()))
            
            if (userID):
                order.user_id = userID
            else:
                order.user = User(role=Role.Customer.value,
                                     type=UserType.Guest.value,
                                     first_name=firstName,
                                     last_name=lastName,
                                     email=email,
                                     phone_number=phoneNumber,
                                     is_enabled=True)

            if (userID):
                userShippingAddresses = User_address.query.filter_by(user_id=userID)\
                                .filter(User_address.address_line_1==shippingAddressLine1, User_address.address_line_2==shippingAddressLine2, User_address.city==shippingAddressCity, User_address.postal_code==shippingAddressPostalCode, User_address.country==shippingAddressCountry).first()

            if (userID and userShippingAddresses):
                order.shipping_details.shipping_address_id = userShippingAddresses.id
            else:
                newShippingAddress = User_address(address_line_1=shippingAddressLine1,
                                                address_line_2=shippingAddressLine2,
                                                city=shippingAddressCity,
                                                postal_code=shippingAddressPostalCode,
                                                country=shippingAddressCountry)
                if (userID):
                    newShippingAddress.user_id = userID
                else:
                    newShippingAddress.user = order.user
                order.shipping_details.shipping_address = newShippingAddress

            if not(billingAddressLine1 == '' or billingAddressLine2 == '' or billingAddressCity == '' or billingAddressPostalCode == '' or billingAddressCountry == ''):
                if (userID):
                    userBillingAddresses = User_address.query.filter_by(user_id=userID)\
                                    .filter(User_address.address_line_1==billingAddressLine1, User_address.address_line_2==billingAddressLine2, User_address.city==billingAddressCity, User_address.postal_code==billingAddressPostalCode, User_address.country==billingAddressCountry).first()
                if (userID and userBillingAddresses):
                    order.payment_details.billing_address_id = userBillingAddresses.id
                else:
                    newBillingAddress = User_address(address_line_1=billingAddressLine1,
                                                    address_line_2=billingAddressLine2,
                                                    city=billingAddressCity,
                                                    postal_code=billingAddressPostalCode,
                                                    country=billingAddressCountry)
                    if ((newBillingAddress.address_line_1 == order.shipping_details.shipping_address.address_line_1) and (newBillingAddress.address_line_2 == order.shipping_details.shipping_address.address_line_2) and (newBillingAddress.city == order.shipping_details.shipping_address.city) and (newBillingAddress.postal_code == order.shipping_details.shipping_address.postal_code) and (newBillingAddress.country == order.shipping_details.shipping_address.country)):
                        order.payment_details.billing_address = order.shipping_details.shipping_address
                    else:
                        if (userID):
                            newBillingAddress.user_id = userID
                        else:
                            newBillingAddress.user = order.user
                        order.payment_details.billing_address = newBillingAddress
            
            Order_items.query.filter_by(order_id = id).delete()
            order.sub_total = Decimal()
            order.taxes_cost = Decimal()
            order.total_cost = Decimal()
            
            for productId, quantity in productsList:
                productToAdd = Product.query.get(productId)
                if productToAdd is None:
                    raise NoResultFound("Product with id={productId} wasn't found")
                if (productToAdd.quantity < quantity):
                    raise ValueError("Not enough items with id {productToAdd.id}")
                order.sub_total += (productToAdd.cost * quantity)
                order.taxes_cost += ((productToAdd.price-productToAdd.price_without_tax) * quantity)
                order.total_cost += (productToAdd.price_without_tax * quantity)
                orderItem = Order_items(product_id=productId, quantity=quantity)
                order.order_items.append(orderItem)

            order.total_cost += (order.taxes_cost + order.shipping_cost)
            if order.total_cost > Decimal('99.00'):
                order.shipping_cost = Decimal('0.00')
            order.modified_at = func.now()

            # if order.status == OrderStatus.Completed.value:
            #     order.user.reward_points += order.reward_points

            flash('Order was modified', category='success')
            db.session.commit()

        return redirect(url_for("adminView.orders"))
    
    order = Order_details.query.get_or_404(id)
    users = User.query.options(load_only(User.id, User.type, User.first_name, User.last_name, User.email, User.phone_number)).filter(User.role==Role.Customer.value).order_by('id').all()
    products = Product.query.filter(Product.is_enabled == True).order_by('id').all()
    
    uploadPath = app.config['UPLOAD_PATH'].split('/', 1)[1]

    return render_template('admin/orders/admin_order.html', order=order, users=users, products=products, OrderStatus=OrderStatus, ShippingMethod=ShippingMethod, PaymentMethod=PaymentMethod, uploadPath=uploadPath)

@adminView.route('/order/delete/<int:id>', methods=['GET', 'POST'])
def order_delete(id):

    order = Order_details.query.get_or_404(id)
    try:
        order_status_history = Order_status_history.query.filter_by(order_id=id).all()
        for statusRecord in order_status_history:
            db.session.delete(statusRecord)
        
        order_items = Order_items.query.filter_by(order_id=id).all()
        for item in order_items:
            db.session.delete(item)

        shipping_details = Shipping_details.query.get(order.shipping_id)

        db.session.delete(shipping_details)

        payment_details = Payment_details.query.get(order.payment_id)
        db.session.delete(payment_details)

        db.session.delete(order)

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error while deleting order: {e}')
        flash('An error occurred', category='error')

    db.session.commit()
    flash('Order was deleted', category='success')
    return redirect(url_for('adminView.orders'))

#TODO: write a __eq__ overload for comparing two addresses
@adminView.route('/order', methods=['GET', 'POST'])
def newOrder():
    if request.method == 'POST':        
        payment_method = request.form.get('_payment_method')
        shipping_method = request.form.get('_shipping_method')

        try:
            payment_method = int(payment_method)
        except ValueError as e:
            app.logger.warning(f"Invalid payment method: {e}")
        
        try:
            shipping_method = int(shipping_method)
        except ValueError as e:
            app.logger.warning(f"Invalid shipping method: {e}")
            
        try:
            userID = int(request.form.get('_userId'))
        except Exception as e:
            userID = None

        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        email = request.form.get('_email')
        phoneNumber = request.form.get('_phoneNumber')
        billingAddressLine1 = request.form.get('_billing_address_line_1')
        billingAddressLine2 = request.form.get('_billing_address_line_2')
        billingAddressCity = request.form.get('_billing_address_city')
        billingAddressPostalCode = request.form.get('_billing_address_postal_code')
        billingAddressCountry = request.form.get('_billing_address_country')
        shippingAddressLine1 = request.form.get('_shipping_address_line_1')
        shippingAddressLine2 = request.form.get('_shipping_address_line_2')
        shippingAddressCity = request.form.get('_shipping_address_city')
        shippingAddressPostalCode = request.form.get('_shipping_address_postal_code')
        shippingAddressCountry = request.form.get('_shipping_address_country')
        productsString = request.form.get('_productID_productQuantity[]')
        if productsString:
            productsList = json.loads(productsString)
        
        try:
            currentStatus = int(request.form.get('_status_update_new_status'))
        except ValueError as e:
            app.logger.warning(f"Invalid input: {e}")

        try:
            notify = int(request.form.get('_status_update_notify'))
        except:
            notify = 0

        statusComment = request.form.get('_status_update_comment')

        if (payment_method == '' or not(payment_method in PaymentMethod._value2member_map_)):
            flash('Payment method must be selected', category='error')
        elif (shipping_method == '' or not(shipping_method in ShippingMethod._value2member_map_)):
            flash('Shipping method must be selected', category='error')
        elif (userID == ''):
            if (firstName == '' or lastName == '' or email == '' or phoneNumber == ''):
                flash('User info must be filled', category='error')
        elif (shippingAddressLine1 == '' or shippingAddressLine2 == '' or shippingAddressCity == '' or shippingAddressPostalCode == '' or shippingAddressCountry == ''):
            flash('Shipping address must be filled', category='error')
        elif (not productsList):
            flash('Products must be selected', category='error')
        elif (currentStatus == '' or not(currentStatus in OrderStatus._value2member_map_)):
            flash('Invalid status of the order', category='error')
        else:
            shippingMethodPrice = ShippingMethodsPrices.query.filter_by(shipping_method_id=shipping_method).first() 
            additionalShippingCost = Decimal('0.00')
            rewardPointsRate = Decimal('0.10')

            if not shippingMethodPrice:
                raise ValueError(f"No shipping method price found for ID: {shipping_method}")
            
            newOrder = Order_details(
                            sub_total = Decimal('0.00'),
                            shipping_cost = shippingMethodPrice.price + additionalShippingCost,
                            taxes_cost = Decimal('0.00'),
                            total_cost = Decimal('0.00'),
                            payment_details=Payment_details(method=payment_method),
                            shipping_details=Shipping_details(method=shipping_method, price = shippingMethodPrice.price + additionalShippingCost, estimated_delivery_time=func.now() + text("INTERVAL '7 days'")),
                            current_status = currentStatus,
                            modified_at = func.now())
            
            newOrder.status_history.append(Order_status_history(new_status=currentStatus, customer_notified=notify, comment=statusComment, modified_at = func.now())),
            
            if (userID):
                newOrder.user_id = userID
            else:
                existingUser = User.query.filter_by(email=email).first()
                if (existingUser):
                    raise RuntimeError(f"User with email {email} already exists")
                
                newOrder.user = User(role=Role.Customer.value,
                                     type=UserType.Guest.value,
                                     first_name=firstName,
                                     last_name=lastName,
                                     email=email,
                                     phone_number=phoneNumber,
                                     is_enabled=True)
          
            if (userID):
                userShippingAddresses = User_address.query.filter_by(user_id=userID)\
                                .filter(User_address.address_line_1==shippingAddressLine1, User_address.address_line_2==shippingAddressLine2, User_address.city==shippingAddressCity, User_address.postal_code==shippingAddressPostalCode, User_address.country==shippingAddressCountry).first()

            if (userID and userShippingAddresses):
                newOrder.shipping_details.shipping_address_id = userShippingAddresses.id
            else:
                newShippingAddress = User_address(address_line_1=shippingAddressLine1,
                                                address_line_2=shippingAddressLine2,
                                                city=shippingAddressCity,
                                                postal_code=shippingAddressPostalCode,
                                                country=shippingAddressCountry)
                if (userID):
                    newShippingAddress.user_id = userID
                else:
                    newShippingAddress.user = newOrder.user
                newOrder.shipping_details.shipping_address = newShippingAddress


            if not(billingAddressLine1 == '' or billingAddressLine2 == '' or billingAddressCity == '' or billingAddressPostalCode == '' or billingAddressCountry == ''):
                if (userID):
                    userBillingAddresses = User_address.query.filter_by(user_id=userID)\
                                    .filter(User_address.address_line_1==billingAddressLine1, User_address.address_line_2==billingAddressLine2, User_address.city==billingAddressCity, User_address.postal_code==billingAddressPostalCode, User_address.country==billingAddressCountry).first()
                if (userID and userBillingAddresses):
                    newOrder.payment_details.billing_address_id = userBillingAddresses.id
                else:
                    newBillingAddress = User_address(address_line_1=billingAddressLine1,
                                                    address_line_2=billingAddressLine2,
                                                    city=billingAddressCity,
                                                    postal_code=billingAddressPostalCode,
                                                    country=billingAddressCountry)
                    if ((newBillingAddress.address_line_1 == newOrder.shipping_details.shipping_address.address_line_1) and (newBillingAddress.address_line_2 == newOrder.shipping_details.shipping_address.address_line_2) and (newBillingAddress.city == newOrder.shipping_details.shipping_address.city) and (newBillingAddress.postal_code == newOrder.shipping_details.shipping_address.postal_code) and (newBillingAddress.country == newOrder.shipping_details.shipping_address.country)):
                        newOrder.payment_details.billing_address = newOrder.shipping_details.shipping_address
                    else:
                        if (userID):
                            newBillingAddress.user_id = userID
                        else:
                            newBillingAddress.user = newOrder.user
                        newOrder.payment_details.billing_address = newBillingAddress

            for productId, quantity in productsList:
                productToAdd = Product.query.get(productId)
                if productToAdd is None:
                    raise NoResultFound("Product with id={productId} wasn't found")
                if (productToAdd.quantity < quantity):
                    raise ValueError("Not enough items with id {productToAdd.id}")
                newOrder.sub_total += (productToAdd.cost * quantity)
                newOrder.taxes_cost += ((productToAdd.price-productToAdd.price_without_tax) * quantity)
                newOrder.total_cost += (productToAdd.price_without_tax * quantity)      
                orderItem = Order_items(product_id=productId, quantity=quantity, modified_at=func.now())
                newOrder.order_items.append(orderItem)

            newOrder.total_cost += (newOrder.taxes_cost + newOrder.shipping_cost)
            newOrder.reward_points = newOrder.total_cost * rewardPointsRate

            db.session.add(newOrder)
            flash('Order created!', category='success')
            db.session.commit()
           
        return redirect(url_for("adminView.orders"))   

    users = User.query.options(load_only(User.id, User.type, User.first_name, User.last_name, User.email, User.phone_number)).filter(User.role==Role.Customer.value).order_by('id').all()
    products = Product.query.filter(Product.is_enabled == True).order_by('id').all()
    
    uploadPath = app.config['UPLOAD_PATH'].split('/', 1)[1] 
    return render_template('admin/orders/admin_order.html', users=users, products=products, OrderStatus=OrderStatus, ShippingMethod=ShippingMethod, PaymentMethod=PaymentMethod, uploadPath=uploadPath)


#------------------------------Customers page------------------------------#
@adminView.route('/customers', methods=['GET', 'POST'])
def customers():
    if request.method == 'POST':

        if current_user.role <  Role.Admin.value:
            flash('You don\'t have permission to add customers', category='error')
            return redirect(url_for('adminView.customers'))
           
        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        email = request.form.get('_email')
        phoneNumber = request.form.get('_phoneNumber')
        password = request.form.get('_password')
        passwordConfirm = request.form.get('_password_confirm')
        accountBalance = request.form.get('_account_balance')
        addresslines1 = request.form.getlist('_address_line_1[]')
        addresslines2 = request.form.getlist('_address_line_2[]')
        cities = request.form.getlist('_city[]')
        postalCodes = request.form.getlist('_postal_code[]')
        countries = request.form.getlist('_country[]')
        isEnabled = request.form.get('_isEnabled')

        user = User.query.filter_by(email=email).first()

        try:
            isEnabled = int(isEnabled)
            if not(isinstance(isEnabled, int)):
                flash('You must specify if user is enabled', category='error')
                return redirect(url_for('adminView.addCustomers'))
        except:
            flash('You must specify if user is enabled', category='error')
            return redirect(url_for('adminView.addCustomers'))
        try:
            _accountBalance = int(accountBalance)
            if (_accountBalance < 0 or _accountBalance > 1000000): 
                flash('Account balance must be a number between 0 and 1000000', category='error')
                return redirect(url_for('adminView.addCustomers'))
        except:
            flash('Account balance must be a number between 0 and 1000000', category='error')
            return redirect(url_for('adminView.addCustomers'))

        if len(firstName) < 2:
            flash('Name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.addCustomers'))
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.addCustomers'))
        elif len(phoneNumber) < 6:
            flash('Phone number must be greater than 5 characters', category='error')
            return redirect(url_for('adminView.addCustomers'))
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
            return redirect(url_for('adminView.addCustomers'))
        elif len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
            return redirect(url_for('adminView.addCustomers'))
        elif password != passwordConfirm:
            flash('Passwords don\'t match', category='error')
            return redirect(url_for('adminView.addCustomers'))
        elif user:
            flash('User with this email already exists', category='error')
            return redirect(url_for('adminView.addCustomers'))
        else:
            try:
                new_user = User(role=Role.Customer.value,
                                type=UserType.Permanent.value,
                                first_name=firstName,
                                last_name=lastName,
                                phone_number=phoneNumber,
                                email=email,
                                password=generate_password_hash(password),
                                account_balance=accountBalance,
                                is_enabled=isEnabled)
                
                print(addresslines1,addresslines2,cities,postalCodes,countries)
                
                for i in range(len(addresslines1)):
                    if (addresslines1[i] == '' or addresslines2[i] == '' or cities[i] == '' or postalCodes[i] == '' or countries[i] == ''):
                        db.session.rollback()
                        flash('Address info can\'t be empty', category='error')
                        return redirect(url_for('adminView.addCustomers'))
                    else:
                        new_user.address.append(User_address(address_line_1 = addresslines1[i],
                                                            address_line_2 = addresslines2[i],
                                                            city=cities[i],
                                                            postal_code=postalCodes[i],
                                                            country=countries[i]))
                db.session.add(new_user)

            except Exception as e:
                db.session.rollback()
                app.logger.error(e)
                flash('An error occurred', category='error')
           
            db.session.commit()
            flash('New user was added', category='success')

    users = User.query.filter(User.role==Role.Customer.value).order_by('id').all()
    for user in users:
        user.total_sum = sum(order.total_cost for order in user.order_details)

    return render_template('admin/users/admin_customers.html', users=users)

@adminView.route('/customers/update/<int:id>', methods=['GET', 'POST'])
def customers_update(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        
        if current_user.role <  Role.Admin.value:
            flash('You don\'t have permission to modify customers', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
         
        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        email = request.form.get('_email')
        phoneNumber = request.form.get('_phoneNumber')
        password = request.form.get('_password')
        passwordConfirm = request.form.get('_password_confirm')
        accountBalance = request.form.get('_account_balance')
        addresslines1 = request.form.getlist('_address_line_1[]')
        addresslines2 = request.form.getlist('_address_line_2[]')
        cities = request.form.getlist('_city[]')
        postalCodes = request.form.getlist('_postal_code[]')
        countries = request.form.getlist('_country[]')
        isEnabled = request.form.get('_isEnabled')

        user_email = User.query.filter_by(email=email).first()

        try:
            isEnabled = int(isEnabled)
            if not(isinstance(isEnabled, int)):
                flash('You must specify if user is enabled', category='error')
                return redirect(url_for('adminView.customers_update', id=id))
        except:
            flash('You must specify if user is enabled', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        try:
            _accountBalance = int(accountBalance)
            if (_accountBalance < 0 or _accountBalance > 1000000): 
                flash('Account balance must be a number between 0 and 1000000', category='error')
                return redirect(url_for('adminView.customers_update', id=id))
        except:
            flash('Account balance must be a number between 0 and 1000000', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        
        if len(firstName) < 2:
            flash('Name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        elif len(phoneNumber) < 6:
            flash('Phone number must be greater than 5 characters', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        elif len(password) > 0 and len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        elif password != passwordConfirm:
            flash('Passwords don\'t match', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        elif user_email and user_email != user:
            flash('User with this email already exists', category='error')
            return redirect(url_for('adminView.customers_update', id=id))
        else:
            try:
                user.first_name=firstName
                user.last_name=lastName
                user.phone_number=phoneNumber
                user.email=email
                if password != '':
                    user.password=generate_password_hash(password)
                user.account_balance=accountBalance
                user.is_enabled=isEnabled
                user.modified_at=func.now()
                
                addresses = User_address.query.filter(User_address.user_id == id).all()
                newAddresses = [list(i) for i in zip(addresslines1, addresslines2, cities, postalCodes, countries)]
                newAddressesSet = set(tuple(i) for i in newAddresses)

                for address in addresses:
                    address_tuple = (address.address_line_1, address.address_line_2, address.city, address.postal_code, address.country)
                    if address_tuple not in newAddressesSet:                       
                        db.session.delete(address)

                addressesSet = set(tuple([address.address_line_1, address.address_line_2, address.city, address.postal_code, address.country]) for address in addresses)
                
                for newAddressTuple in newAddressesSet:
                    if (newAddressTuple not in addressesSet):
                        # raise ValueError("....")
                        if (newAddressTuple[0] == '' or newAddressTuple[1] == '' or newAddressTuple[2] == '' or newAddressTuple[3] == '' or newAddressTuple[4] == ''):
                            db.session.rollback()
                            flash('Address info can\'t be empty', category='error')
                            return redirect(url_for('adminView.customers_update', id=id))
                        else:
                            user.address.append(User_address(address_line_1=newAddressTuple[0],
                                                        address_line_2=newAddressTuple[1],
                                                        city=newAddressTuple[2],
                                                        postal_code=newAddressTuple[3],
                                                        country=newAddressTuple[4]))
            except Exception as e:
                db.session.rollback()
                app.logger.error(e)
                if isinstance(e.orig, psycopg2.errors.ForeignKeyViolation):
                    flash("You can't modify a shipping address of an order", category='error')
                    print("Foreign key violation detected:", e)
                else:
                    print("An integrity error occurred:", e)
                    flash('An error occurred', category='error')
                return redirect(url_for("adminView.customers"))
            
            db.session.commit()            
            flash('User was edited', category='success')

        return redirect(url_for('adminView.customers'))

    return render_template('admin/users/admin_customer_edit.html', user=user)

def hasIncompletedOrders(user):
    for order in user.order_details:
        if order.current_status < OrderStatus.Completed.value:
            return True
    return False

@adminView.route('/customers/delete/<int:id>')
def customers_delete(id):
    user = User.query.get_or_404(id)
    user_addresses = User_address.query.filter(User_address.user_id==id).all()

    if current_user.role < Role.Admin.value:
        flash('You don\'t have permission to modify customers', category='error')
    elif (hasIncompletedOrders(user)):
        flash('You can\'t delete user who has unfulfilled    orders', category='error')
    else:
        try:
            if user_addresses:
                for address in user_addresses:
                    if not address.payment_details and not address.shipping_details:
                        db.session.delete(address)
            db.session.delete(user)
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash('An error occurred', category='error')
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash('An error occurred', category='error')
            return redirect(url_for('adminView.customers'))


        flash('User was deleted', category='success')
    return redirect(url_for('adminView.customers'))

@adminView.route('/customers/reward_points/<int:id>', methods=['GET', 'POST'])
def customers_reward_points(id):
    if request.method == 'POST':
        rewardPoints = request.form.get('_add_reward_points')
        try:
            rewardPoints = int(rewardPoints)
            user = User.query.get(id)
            if (user.reward_points + rewardPoints >= 0):
                user.reward_points += rewardPoints
                flash('Reward points were scored', category='success')
            else:
                flash('Invalid amount', category="error")
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash('Invalid amount', category="error")
        db.session.commit()

    return redirect(url_for('adminView.customers_update', id=id))

@adminView.route('/customers/add')
def addCustomers():
    return render_template('admin/users/admin_customer_edit.html')

#------------------------------Managers page------------------------------#
@adminView.route('/managers', methods=['GET', 'POST'])
def managers():
    if request.method == 'POST':

        if current_user.role <  Role.Admin.value:
            flash('You don\'t have permission to add managers', category='error')
            return redirect(url_for('adminView.managers'))
        
        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        email = request.form.get('_email')
        phoneNumber = request.form.get('_phoneNumber')
        password = request.form.get('_password')
        passwordConfirm = request.form.get('_password_confirm')
        isEnabled = request.form.get('_isEnabled')

        user = User.query.filter_by(email=email).first()

        try:
            isEnabled = int(isEnabled)
            if not(isinstance(isEnabled, int)):
                flash('You must specify if manager is enabled', category='error')
                return redirect(url_for('adminView.addManagers'))
        except:
            flash('You must specify if manager is enabled', category='error')
            return redirect(url_for('adminView.addManagers'))
        
        if len(firstName) < 2:
            flash('Name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.addManagers'))
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.addManagers'))
        elif len(phoneNumber) < 6:
            flash('Phone number must be greater than 5 characters', category='error')
            return redirect(url_for('adminView.addManagers'))
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
            return redirect(url_for('adminView.addManagers'))
        elif len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
            return redirect(url_for('adminView.addManagers'))
        elif password != passwordConfirm:
            flash('Passwords don\'t match', category='error')
            return redirect(url_for('adminView.addManagers'))
        elif user:
            flash('User with this email already exists', category='error')
            return redirect(url_for('adminView.addManagers'))
        else:
            try:
                new_user = User(role=Role.Manager.value,
                                type=UserType.Permanent.value,
                                first_name=firstName,
                                last_name=lastName,
                                email=email,
                                phone_number=phoneNumber,
                                password=generate_password_hash(password),
                                is_enabled=isEnabled)
                db.session.add(new_user)
            except Exception as e:
                db.session.rollback()
                app.logger.error(e)
                flash('An error occurred', category='error')
           
            db.session.commit()
            flash('New user was added', category='success')

    users = User.query.filter(User.role==Role.Manager.value).order_by('id').all()
    return render_template('admin/users/admin_managers.html', users=users)

@adminView.route('/managers/update/<int:id>', methods=['GET', 'POST'])
def managers_update(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':

        if current_user.role <  Role.Admin.value:
            flash('You don\'t have permission to modify managers', category='error')
            return redirect(url_for('adminView.managers_update', id=id))

        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        email = request.form.get('_email')
        phoneNumber = request.form.get('_phoneNumber')
        password = request.form.get('_password')
        passwordConfirm = request.form.get('_password_confirm')
        isEnabled = request.form.get('_isEnabled')

        user_email = User.query.filter_by(email=email).first()

        try:
            isEnabled = int(isEnabled)
            if not(isinstance(isEnabled, int)):
                flash('You must specify if manager is enabled', category='error')
                return redirect(url_for('adminView.managers_update', id=id))
        except:
            flash('You must specify if manager is enabled', category='error')
            return redirect(url_for('adminView.managers_update', id=id))
        
        if len(firstName) < 2:
            flash('Name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.managers_update', id=id))
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.managers_update', id=id))
        elif len(phoneNumber) < 6:
            flash('Phone number must be greater than 5 characters', category='error')
            return redirect(url_for('adminView.managers_update', id=id))
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
            return redirect(url_for('adminView.managers_update', id=id))
        elif len(password) > 0 and len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
            return redirect(url_for('adminView.managers_update', id=id))
        elif password != passwordConfirm:
            flash('Passwords don\'t match', category='error')
            return redirect(url_for('adminView.managers_update', id=id))
        elif user_email and user_email != user:
            flash('User with this email already exists', category='error')
            return redirect(url_for('adminView.managers_update', id=id))
        else:
            try:
                user.first_name=firstName
                user.last_name=lastName
                user.phone_number=phoneNumber
                user.email=email
                if password != '':
                    user.password=generate_password_hash(password)
                user.is_enabled=isEnabled
                user.modified_at=func.now()

            except Exception as e:
                db.session.rollback()
                app.logger.error(e)
                flash('An error occurred', category='error')

            db.session.commit()
            flash('User was edited', category='success')
        return redirect(url_for('adminView.managers'))

    return render_template('admin/users/admin_manager_edit.html', user=user)

@adminView.route('/managers/delete/<int:id>')
def managers_delete(id):
    user = User.query.get_or_404(id)

    if current_user.role <  Role.Admin.value:
            flash('You don\'t have permission to delete managers', category='error')
    else:
        try:
            db.session.delete(user)
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash('An error occurred', category='error')
        
        db.session.commit()
        flash('User was deleted', category='success')
    
    return redirect(url_for('adminView.managers'))

@adminView.route('/managers/add')
def addManagers():
    return render_template('admin/users/admin_manager_edit.html')

#------------------------------Admins page------------------------------#
@adminView.route('/admins', methods=['GET', 'POST'])
def admins():
    if request.method == 'POST':

        if current_user.role != Role.Owner.value:
            flash('You don\'t have permission to add admins', category='error')
            return redirect(url_for('adminView.admins'))
        
        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        email = request.form.get('_email')
        phoneNumber = request.form.get('_phoneNumber')
        password = request.form.get('_password')
        passwordConfirm = request.form.get('_password_confirm')
        isEnabled = request.form.get('_isEnabled')

        user = User.query.filter_by(email=email).first()

        try:
            isEnabled = int(isEnabled)
            if not(isinstance(isEnabled, int)):
                flash('You must specify if admin is enabled', category='error')
                return redirect(url_for('adminView.addAdmins'))
        except:
            flash('You must specify if admin is enabled', category='error')
            return redirect(url_for('adminView.addAdmins'))
        
        if len(firstName) < 2:
            flash('Name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.addAdmins'))
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.addAdmins'))
        elif len(phoneNumber) < 6:
            flash('Phone number must be greater than 5 characters', category='error')
            return redirect(url_for('adminView.addAdmins'))
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
            return redirect(url_for('adminView.addAdmins'))
        elif len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
            return redirect(url_for('adminView.addAdmins'))
        elif password != passwordConfirm:
            flash('Passwords don\'t match', category='error')
            return redirect(url_for('adminView.addAdmins'))
        elif user:
            flash('User with this email already exists', category='error')
            return redirect(url_for('adminView.addAdmins'))
        else:
            try:
                new_user = User(role=Role.Admin.value,
                                type=UserType.Permanent.value,
                                first_name=firstName,
                                last_name=lastName,
                                email=email,
                                phone_number=phoneNumber,
                                password=generate_password_hash(password),
                                is_enabled=isEnabled)
                db.session.add(new_user)
            except Exception as e:
                db.session.rollback()
                app.logger.error(e)
                flash('An error occurred', category='error')
           
            db.session.commit()
            flash('New admin was added', category='success')

    users = User.query.filter(User.role==Role.Admin.value).order_by('id').all()
    return render_template('admin/users/admin_admins.html', users=users)

@adminView.route('/admins/update/<int:id>', methods=['GET', 'POST'])
def admins_update(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':

        if current_user.role !=  Role.Owner.value:
            flash('You don\'t have permission to modify admins', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        
        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        email = request.form.get('_email')
        phoneNumber = request.form.get('_phoneNumber')
        password = request.form.get('_password')
        passwordConfirm = request.form.get('_password_confirm')
        isEnabled = request.form.get('_isEnabled')

        user_email = User.query.filter_by(email=email).first()

        try:
            isEnabled = int(isEnabled)
            if not(isinstance(isEnabled, int)):
                flash('You must specify if admin is enabled', category='error')
                return redirect(url_for('adminView.admins_update', id=id))
        except:
            flash('You must specify if admin is enabled', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        
        if len(firstName) < 2:
            flash('Name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        elif len(phoneNumber) < 6:
            flash('Phone number must be greater than 5 characters', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        elif len(password) > 0 and len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        elif password != passwordConfirm:
            flash('Passwords don\'t match', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        elif user_email and user_email != user:
            flash('User with this email already exists', category='error')
            return redirect(url_for('adminView.admins_update', id=id))
        else:
            try:
                user.first_name=firstName
                user.last_name=lastName
                user.phone_number=phoneNumber
                user.email=email
                if password != '':
                    user.password=generate_password_hash(password)
                user.is_enabled=isEnabled
                user.modified_at=func.now()

            except Exception as e:
                db.session.rollback()
                app.logger.error(e)
                flash('An error occurred', category='error')

            db.session.commit()
            flash('User was edited', category='success')
        return redirect(url_for('adminView.admins'))

    return render_template('admin/users/admin_admin_edit.html', user=user)

@adminView.route('/admins/delete/<int:id>')
def admins_delete(id):
    user = User.query.get_or_404(id)

    # if current_user.role !=  Role.Owner.value:
    if current_user.role < Role.Admin.value:
        flash('You don\'t have permission to delete admins', category='error')
    else:
        try:
            db.session.delete(user)
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash('An error occurred', category='error')
        
        db.session.commit()
        flash('User was deleted', category='success')

    return redirect(url_for('adminView.admins'))

@adminView.route('/admins/add')
def addAdmins():
    return render_template('admin/users/admin_admin_edit.html')





