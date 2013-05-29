import os
import sys

root = os.path.dirname(__file__)
sys.path.insert(0, root)

from core import app as application
from core import index
from core.handlers import layer, notice, regulation, search

index.init_schema()
application.register_blueprint(layer.blueprint)
application.register_blueprint(notice.blueprint)
application.register_blueprint(regulation.blueprint)
application.register_blueprint(search.blueprint)
