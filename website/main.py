from . import create_app
from flask_login import current_user
from .view.filters import get_order_status_name, get_order_payment_method_name, get_user_type_name, decimal


app = create_app()

@app.context_processor
def user():
    return dict(current_user=current_user)

@app.template_filter()
def get_order_status_name_filter(status_value):
    return get_order_status_name(status_value)

@app.template_filter()
def get_order_payment_method_name_filter(method_value):
    return get_order_payment_method_name(method_value)

@app.template_filter()
def get_user_type_name_filter(type_value):
    return get_user_type_name(type_value)

@app.template_filter()
def decimal_filter(value):
    return decimal(value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)