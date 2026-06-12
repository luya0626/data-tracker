import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from database import init_db, close_db
from routes import register_blueprints
from config import DIST_DIR


def create_app():
    app = Flask(__name__, static_folder=None)

    # CORS for development (Vite dev server on different port)
    CORS(app)

    # Register API blueprints
    register_blueprints(app)

    # Initialize database on first request
    with app.app_context():
        init_db()

    # Teardown: close DB connection
    app.teardown_appcontext(close_db)

    # ---- Production: serve Vue static files ----

    @app.route('/')
    def serve_index():
        index_path = os.path.join(DIST_DIR, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(DIST_DIR, 'index.html')
        return (
            'Frontend not built. Run: cd frontend && npm install && npm run build<br>'
            'Then refresh this page.',
            503,
        )

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        assets_dir = os.path.join(DIST_DIR, 'assets')
        return send_from_directory(assets_dir, filename)

    @app.route('/favicon.ico')
    def serve_favicon():
        favicon = os.path.join(DIST_DIR, 'favicon.ico')
        if os.path.exists(favicon):
            return send_from_directory(DIST_DIR, 'favicon.ico')
        return '', 204

    # Catch-all for Vue Router (if we ever add routing)
    @app.route('/<path:path>')
    def serve_fallback(path):
        # Skip API routes
        if path.startswith('api/'):
            return {'error': 'Not found'}, 404
        file_path = os.path.join(DIST_DIR, path)
        if os.path.exists(file_path):
            return send_from_directory(DIST_DIR, path)
        # SPA fallback
        index_path = os.path.join(DIST_DIR, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(DIST_DIR, 'index.html')
        return {'error': 'Not found'}, 404

    return app


if __name__ == '__main__':
    app = create_app()
    print('L线 server starting at http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
