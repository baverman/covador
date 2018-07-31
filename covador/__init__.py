from .utils import wrap_in, dpass
from .vdecorator import ValidationDecorator
from .types import *

version = '0.9.22'
schema = make_schema(Map)
list_schema = make_schema(ListMap)
