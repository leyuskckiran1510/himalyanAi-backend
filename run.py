from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(ssl_context="adhoc", host="0.0.0.0")
