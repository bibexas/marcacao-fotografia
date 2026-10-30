from flask import Flask

def criar_app():
    app = Flask(__name__)

    from .web import inicio
    app.register_blueprint(inicio.bp)

    return app