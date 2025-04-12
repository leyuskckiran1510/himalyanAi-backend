from app import create_app
from flask import send_file

app = create_app()


@app.route("/")
def index():
    return send_file("home.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
