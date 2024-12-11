from flask import Flask
from app.routes import setup_routes

# initialize the app
def create_app():
    app = Flask(__name__)

    # app.config.from_mapping(
    #     SECRET_KEY="", 
    # )

    # routes
    setup_routes(app)

    return app
