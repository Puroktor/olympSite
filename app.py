from flask import Flask

from db import db
from routes import blueprint

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='super secret key',
    SQLALCHEMY_DATABASE_URI='sqlite:///olymp.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
app.register_blueprint(blueprint)
db.init_app(app)

with app.app_context():
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
