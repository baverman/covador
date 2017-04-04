from .utils import wrap_in, ValidationDecorator, make_schema
from .types import *

version = '0.9.1'
schema = make_schema(Map)
list_schema = make_schema(ListMap)
