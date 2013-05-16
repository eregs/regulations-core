from core.handlers.regulation import *
from core.handlers.search import *
from core import app, index
index.init_schema()
app.run('0.0.0.0', 8181, debug=True)
