from core.handlers import layer, notice, regulation, search
from core import app, index
index.init_schema()
app.register_blueprint(layer.blueprint)
app.register_blueprint(notice.blueprint)
app.register_blueprint(regulation.blueprint)
app.register_blueprint(search.blueprint)
app.run('0.0.0.0', 8181, debug=True)
