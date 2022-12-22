import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def config_db(app):
    global db
    print(
        "mysql+pymysql://{}:{}@{}/{}".format(
            os.getenv("DB_USER"),
            os.getenv("DB_PASSWORD"),
            os.getenv("DB_HOST"),
            os.getenv("DB_NAME"),
        )
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{}:{}@{}/{}".format(
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_HOST"),
        os.getenv("DB_NAME"),
    )

    db.init_app(app)

    with app.app_context():
        db.create_all()
