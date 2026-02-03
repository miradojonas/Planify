from app import app as flask_app

# Vercel's Python runtime expects a module-level `app`.
app = flask_app
