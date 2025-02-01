from flask import Blueprint

auth = Blueprint('auth', __name__)
adminAuth = Blueprint('adminAuth', __name__)

from .auth import *
from .adminAuth import *
