from routes.lines import lines_bp
from routes.data_points import data_points_bp


def register_blueprints(app):
    app.register_blueprint(lines_bp)
    app.register_blueprint(data_points_bp)
