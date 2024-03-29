import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


def create_app(test_config=None):
    # create and configure the app
    print(os.environ['APP_SETTINGS'])
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=True)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app()
    from models import Result
   # app.config.from_mapping(
   #  SECRET_KEY='dev',
   #  DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
   # )
   # if test_config is None:
   #     # load the instance config, if it exists, when not testing
   #    app.config.from_pyfile('config.py', silent=True)
   #   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   # else:
   # load the test config if passed in
   #    app.config.from_mapping(test_config)

   # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import board
    app.register_blueprint(board.bp)
    app.add_url_rule('/', endpoint='index')

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
