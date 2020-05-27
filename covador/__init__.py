from .utils import wrap_in, dpass
from .vdecorator import ValidationDecorator
from .types import *

version = '0.10'

schema = make_schema(item_getter)
list_schema = make_schema(list_item_getter)
