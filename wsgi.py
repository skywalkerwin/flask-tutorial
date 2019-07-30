from flaskr import create_app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

app = create_app(db)

if __name__ == '__main__':
    app.run()
