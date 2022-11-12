from .base import app, db
from .routes import api

app.register_blueprint(api, url_prefix='/api/v1')
