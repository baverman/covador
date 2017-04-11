from .utils import wrap_in, ValidationDecorator, make_schema
from .types import *

version = '0.9.2'
schema = make_schema(Map)
list_schema = make_schema(ListMap)
