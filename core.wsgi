import os
import sys

root = os.path.dirname(__file__)
sys.path.insert(0, root)

from core import app as application
from core import index
from core.handlers.search import *
from core.handlers.regulation import *

index.init_schema()
