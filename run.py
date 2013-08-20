from core import app, index
from core.handlers import diff, layer, notice, regulation, search


index.init_schema()

app.register_blueprint(diff.blueprint)
app.register_blueprint(layer.blueprint)
app.register_blueprint(notice.blueprint)
app.register_blueprint(regulation.blueprint)
app.register_blueprint(search.blueprint)

app.run('0.0.0.0', 8181, debug=True)
