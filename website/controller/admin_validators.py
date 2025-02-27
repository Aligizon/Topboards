from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, MultipleFileField, FileField, TextAreaField, BooleanField, RadioField, PasswordField, SubmitField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, Optional, Length, Email, Regexp, AnyOf
from ..model.models import ShippingMethod, PaymentMethod
from werkzeug.datastructures import FileStorage
from wtforms.validators import ValidationError

def validate_files(form, field):
    allowed_extensions = {'jpg', 'png', 'jpeg'}
    allowed_mime_types = {'image/jpeg', 'image/png'}
    if field.data:
        if isinstance(field.data, list):
            for file in field.data:
                if file.filename:
                    if isinstance(file, FileStorage):
                        if not any(file.filename.endswith(ext) for ext in allowed_extensions):
                            raise ValidationError(f'Invalid file type! Only {", ".join(allowed_extensions)} are allowed.')
                        if file.mimetype not in allowed_mime_types:
                            raise ValidationError('Invalid MIME type! Only image/jpeg and image/png are allowed.')
        elif isinstance(field.data, FileStorage):
            if not any(field.data.filename.endswith(ext) for ext in allowed_extensions):
                raise ValidationError(f'Invalid file type! Only {", ".join(allowed_extensions)} are allowed.')
            if field.data.mimetype not in allowed_mime_types:
                raise ValidationError('Invalid MIME type! Only image/jpeg and image/png are allowed.')

class ProductForm(FlaskForm):
    mainImage = FileField('prod_main_image',
                          render_kw={"id": "prod_main_image", "class": "d-none"}, 
                          validators=[Optional(),
                                      validate_files])
    additionalImages = MultipleFileField('product_img[]',
                                 render_kw={"id": "prod_images", "class": "d-none", "multiple": "multiple"}, 
                                 validators=[Optional(),
                                             validate_files])
    name = StringField('_name',
                        render_kw={"id": "name", "class": "base-input", "placeholder": "Product Name"},
                        validators=[DataRequired()]) 
    desc = TextAreaField('_description',
                        render_kw={"id": "description", "class": "add-product-textarea", "placeholder": "Description", "for": "editForm"},
                        validators=[Optional()])
    model = StringField('_model',
                        render_kw={"id": "model", "class": "base-input", "placeholder": "Model"},
                        validators=[Optional()])
    category = StringField('_category',
                            render_kw={"id": "category", "class": "base-input", "placeholder": "Category"},
                            validators=[DataRequired()])
    brand = StringField('_brand',
                        render_kw={"id": "category", "class": "base-input", "placeholder": "Brand"},
                        validators=[Optional()])
    switches = StringField('_switches',
                        render_kw={"id": "category", "class": "base-input", "placeholder": "Switches"},
                        validators=[Optional()])
    color = StringField('_color',
                        render_kw={"id": "color", "class": "base-input", "placeholder": "Color name"},
                        validators=[Optional()])
    color_HEX = StringField('_color_HEX',
                            render_kw={"id": "color_HEX", "class": "base-input", "placeholder": "#FFFFFF"},
                            validators=[Regexp(r'^$|^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$', message='Invalid HEX color code'), Optional()])
    SKU = StringField('_SKU',
                        render_kw={"id": "SKU", "class": "base-input", "placeholder": "SKU"},
                        validators=[DataRequired()])
    quantity = IntegerField('_quantity',
                            render_kw={"id": "quantity", "class": "base-input", "placeholder": "Quantity"},
                            validators=[Optional()])
    form_factor = StringField('_formFactor',
                                render_kw={"id": "formFactor", "class": "base-input", "placeholder": "Form Factor"},
                                validators=[Optional()])
    dimensions = StringField('_dimensions',
                                render_kw={"id": "dimensions", "class": "base-input", "placeholder": "Dimensions (L x W x H)"},
                                validators=[Optional()])
    weight = FloatField('_weight',
                        render_kw={"id": "weight", "class": "base-input", "placeholder": "Weight (kg)"},
                        validators=[Optional()])
    cost = FloatField('_cost',
                        render_kw={"id": "cost", "class": "base-input", "placeholder": "Cost (purchase price)"},
                        validators=[DataRequired()])
    price_without_tax = FloatField('_withoutTax',
                                    render_kw={"id": "withoutTax", "class": "base-input", "placeholder": "Price without Tax"},
                                    validators=[DataRequired()])
    price = FloatField('_price',
                        render_kw={"id": "price", "class": "base-input", "placeholder": "Price"},
                        validators=[DataRequired()])
    is_enabled = RadioField('Status', 
                         choices=[('1', 'Enabled'), ('0', 'Disabled')],
                         default = '0',
                         render_kw={"class": "add-product-radio"},
                         validators=[DataRequired()])




    
    
    
    
    
    
    
    #TODO: доделать...
