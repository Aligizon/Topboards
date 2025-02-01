from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, Email, Regexp, AnyOf
from ..model.models import ShippingMethod, PaymentMethod
    
class OrderForm(FlaskForm):
    country = StringField('_country',
                            render_kw={"id": "country-select", "type": "hidden"},
                            validators=[DataRequired()]) # Validate it when there is a table of all allowed countries
    shipping_method = IntegerField('_shipping_method',
                                    render_kw={"id": "shipping-method-select", "type": "hidden"},
                                    validators=[AnyOf([method.value for method in ShippingMethod])])
    shippingAddressLine1 = StringField('_shipping_address_line_1',
                                        render_kw={"class": "base-input mb-4", "placeholder": "Street"},
                                        validators=[DataRequired()])
    shippingAddressLine2 = StringField('_shipping_address_line_2',
                                        render_kw={"class": "base-input mb-4", "placeholder": "House no."},
                                        validators=[DataRequired()])
    shippingAddressCity = StringField('_shipping_address_city',
                                        render_kw={"class": "base-input mb-4", "placeholder": "City"},
                                        validators=[DataRequired()])
    shippingAddressPostalCode = StringField('_shipping_address_postal_code',
                                                render_kw={"class": "base-input mb-4", "placeholder": "Postal code"},
                                                validators=[DataRequired(), Regexp(r'^\d+$', message='The postal code must contain only numbers.')])
    payment_method = IntegerField('_payment_method',
                                    render_kw={"id": "payment-method-select", "type": "hidden"},
                                    validators=[AnyOf([method.value for method in PaymentMethod])])
    sameBillingAddress = BooleanField('_same_billing_address',
                                        render_kw={"id": "same_billing_address", "type": "checkbox"},
                                        default=True,
                                        validators=[Optional()])
    billingAddressLine1 = StringField('_billing_address_line_1',
                                        render_kw={"class": "base-input mb-4", "placeholder": "Street"},
                                        validators=[Optional()])
    billingAddressLine2 = StringField('_billing_address_line_2',
                                        render_kw={"class": "base-input mb-4", "placeholder": "House no."},
                                        validators=[Optional()])
    billingAddressCity = StringField('_billing_address_city',
                                        render_kw={"class": "base-input mb-4", "placeholder": "City"},
                                        validators=[Optional()])
    billingAddressPostalCode = IntegerField('_billing_address_postal_code',
                                                render_kw={"class": "base-input mb-4", "placeholder": "Postal code"},
                                                validators=[Optional()])

class OrderUserDetailsForm(FlaskForm):
    firstName = StringField('_firstName',
                            render_kw={"id": "first_name", "class": "base-input mb-4", "placeholder": "First name"},
                            validators=[DataRequired()])
    lastName = StringField('_lastName',
                        render_kw={"id": "last_name", "class": "base-input mb-4", "placeholder": "Last name"},
                        validators=[DataRequired()])
    email = StringField('Email',
                        render_kw={"id": "email", "class": "base-input mb-4", "placeholder": "Email"},
                        validators=[DataRequired(), Email()])
    phoneNumber = StringField('_phoneNumber',
                              render_kw={"id": "phone_number", "class": "base-input mb-4", "type": "tel", "placeholder": "Phone number"},
                              validators=[DataRequired(), Regexp(r'^\+?[0-9\s-]{8,15}$', message="Invalid phone number format")])
    country = StringField('_country',
                            render_kw={"id": "country-select", "type": "hidden"},
                            validators=[DataRequired()]) # Validate it when there is a table of all allowed countries
    shipping_method = IntegerField('_shipping_method',
                                    render_kw={"id": "shipping-method-select", "type": "hidden"},
                                    validators=[AnyOf([method.value for method in ShippingMethod])])
    shippingAddressLine1 = StringField('_shipping_address_line_1',
                                        render_kw={"class": "base-input mb-4", "placeholder": "Street"},
                                        validators=[DataRequired()])
    shippingAddressLine2 = StringField('_shipping_address_line_2',
                                        render_kw={"class": "base-input mb-4", "placeholder": "House no."},
                                        validators=[DataRequired()])
    shippingAddressCity = StringField('_shipping_address_city',
                                        render_kw={"class": "base-input mb-4", "placeholder": "City"},
                                        validators=[DataRequired()])
    shippingAddressPostalCode = StringField('_shipping_address_postal_code',
                                                render_kw={"class": "base-input mb-4", "placeholder": "Postal code"},
                                                validators=[DataRequired(), Regexp(r'^\d+$', message='The postal code must contain only numbers.')])
    payment_method = IntegerField('_payment_method',
                                    render_kw={"id": "payment-method-select", "type": "hidden"},
                                    validators=[AnyOf([method.value for method in PaymentMethod])])
    sameBillingAddress = BooleanField('_same_billing_address',
                                        render_kw={"id": "same_billing_address", "type": "checkbox"},
                                        default=True,
                                        validators=[Optional()])
    billingAddressLine1 = StringField('_billing_address_line_1',
                                        render_kw={"class": "base-input mb-4", "placeholder": "Street"},
                                        validators=[Optional()])
    billingAddressLine2 = StringField('_billing_address_line_2',
                                        render_kw={"class": "base-input mb-4", "placeholder": "House no."},
                                        validators=[Optional()])
    billingAddressCity = StringField('_billing_address_city',
                                        render_kw={"class": "base-input mb-4", "placeholder": "City"},
                                        validators=[Optional()])
    billingAddressPostalCode = IntegerField('_billing_address_postal_code',
                                                render_kw={"class": "base-input mb-4", "placeholder": "Postal code"},
                                                validators=[Optional()])