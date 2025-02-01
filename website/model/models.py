from . import db
from decimal import Decimal
from flask_login import UserMixin
from sqlalchemy import DECIMAL
from sqlalchemy.sql import func
from enum import Enum

class Role(Enum):
    Customer = 0
    Manager = 1
    Admin = 2
    Owner = 3

class UserType(Enum):
    Guest = 0
    Permanent = 1

class OrderStatus(Enum):
    # Normal order flow
    Pending = 0
    Confirmed = 1
    Processing = 2
    Shipped = 3
    OutForDelivery = 4
    Delivered = 5
    Completed = 6
    # Dismissed by client
    Cancelled = 7
    Returned = 8
    # Unsuccessful payment
    Failed = 9
    # We don't cater for our reasons
    Denied = 10

class ShippingMethod(Enum):
    Standart = 0
    Express = 1
    Courier = 2
    Freight = 3
    ClickAndCollect = 4
    InStorePickup = 5

class PaymentStatus(Enum):
    Pending = 0
    Processing = 1
    Completed = 2
    Failed = 3
    Cancelled = 4
    Refunded = 5
    Chargeback = 6
    AwaitingPayment = 7

class PaymentMethod(Enum):
    CreditCard = 0
    PayPal = 1
    BankTransfer = 2
    CashOnDelivery = 3
    Cryptocurrency = 4
    DigitalWallets = 5


'''user model'''
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, default=Role.Customer.value)
    type = db.Column(db.Integer, default=UserType.Guest.value)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    phone_number = db.Column(db.String(128))
    password = db.Column(db.Text)
    account_balance = db.Column(DECIMAL(10, 2), default=0)
    reward_points = db.Column(db.Integer, default=0)
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))
    address = db.relationship('User_address', backref='user', order_by="User_address.id")
    payment_method = db.relationship('User_payment')
    shopping_session = db.relationship('Shopping_session', uselist=False)
    order_details = db.relationship('Order_details', backref='user')

class User_address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address_line_1 = db.Column(db.String(128))
    address_line_2 = db.Column(db.String(128))
    city = db.Column(db.String(128))
    postal_code = db.Column(db.String(128))
    country = db.Column(db.String(128))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))

class User_payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    method = db.Column(db.Integer, default=PaymentMethod.CashOnDelivery.value)
    provider = db.Column(db.String(128))
    account_no = db.Column(db.Integer)
    expiry = db.Column(db.DateTime(timezone=True))

'''cart model'''
class Shopping_session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(DECIMAL(10, 2))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))
    cart_items = db.relationship('Cart_item')

class Cart_item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('shopping_session.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))
    
'''product model'''
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_item = db.relationship('Cart_item', backref='product')
    order_item = db.relationship('Order_items', backref='product')
    product_images = db.relationship('Product_image')
    name = db.Column(db.String(128))
    desc = db.Column(db.Text)
    model = db.Column(db.String(128))
    category = db.Column(db.String(128))
    brand = db.Column(db.String(128))
    switches = db.Column(db.String(128))
    color = db.Column(db.String(128))
    color_HEX = db.Column(db.String(128), default='#FFFFFF')
    SKU = db.Column(db.String(128))
    quantity = db.Column(db.Integer)
    form_factor = db.Column(db.String(128))
    dimensions = db.Column(db.String(128))
    weight = db.Column(DECIMAL(10, 2))
    price_without_tax = db.Column(DECIMAL(10, 2))
    price = db.Column(DECIMAL(10, 2))
    cost = db.Column(DECIMAL(10, 2))
    is_enabled = db.Column(db.Boolean, default=False)
    discount_id = db.Column(db.Integer, db.ForeignKey('discount.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))

    is_main_category = db.Column(db.Boolean, default=False)
    is_new_category = db.Column(db.Boolean, default=False)
    is_recommended_category = db.Column(db.Boolean, default=False)
    is_otherServices_category = db.Column(db.Boolean, default=False)

class Product_image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    is_main = db.Column(db.Boolean, default=False)
    image_name = db.Column(db.Text)

class Discount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.relationship('Product')
    name = db.Column(db.String(128))
    desc = db.Column(db.Text)
    discount_percent = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))

'''Orders model'''
class Order_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_items = db.relationship('Order_items')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))    
    reward_points = db.Column(db.Integer)
    sub_total = db.Column(DECIMAL(10, 2))
    shipping_cost = db.Column(DECIMAL(10, 2))
    taxes_cost = db.Column(DECIMAL(10, 2))
    total_cost = db.Column(DECIMAL(10, 2))
    current_status = db.Column(db.Integer, default=OrderStatus.Pending.value)
    status_history = db.relationship('Order_status_history')
    shipping_id = db.Column(db.Integer, db.ForeignKey('shipping_details.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment_details.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))

class Order_items(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    order_id = db.Column(db.Integer, db.ForeignKey("order_details.id")) 
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))

class Order_status_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order_details.id")) 
    new_status = db.Column(db.Integer, default=OrderStatus.Pending.value)
    customer_notified = db.Column(db.Boolean, default=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))

class Shipping_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_details = db.relationship('Order_details', uselist=False, backref="shipping_details")
    method = db.Column(db.Integer, default=ShippingMethod.Standart.value)
    price = db.Column(DECIMAL(10, 2))
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('user_address.id'))
    shipping_address = db.relationship('User_address', uselist=False, backref="shipping_details")
    estimated_delivery_time = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))

class Payment_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_details = db.relationship('Order_details', uselist=False, backref="payment_details")
    amount = db.Column(DECIMAL(10, 2))
    provider = db.Column(db.String(128))
    status = db.Column(db.Integer, default=PaymentStatus.AwaitingPayment.value)
    method = db.Column(db.Integer, default=PaymentMethod.CashOnDelivery.value)
    billing_address_id = db.Column(db.Integer, db.ForeignKey('user_address.id'))
    billing_address = db.relationship('User_address', uselist=False, backref="payment_details")
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(db.DateTime(timezone=True))


'''design categories model'''
class Design_categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub_categories = db.relationship('Design_sub_categories')
    name = db.Column(db.String(128))
    link = db.Column(db.String(258))

class Design_sub_categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('design_categories.id'))
    name = db.Column(db.String(128))
    link = db.Column(db.String(258))


'''Service tables'''

class ShippingMethodsPrices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shipping_method_id = db.Column(db.Integer, unique=True)
    price = db.Column(DECIMAL(10, 2), default=Decimal('0.00'))
