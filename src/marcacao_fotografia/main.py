from flask import Flask

def criar_app():
    app = Flask(__name__)

    from .database import iniciar_bd

    iniciar_bd()

    from .web import inicio
    app.register_blueprint(inicio.bp)

    return app
