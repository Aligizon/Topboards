from flask import Blueprint

homeView = Blueprint('homeView', __name__)
adminView = Blueprint('adminView', __name__)

from .homeView import *
from .adminView import *