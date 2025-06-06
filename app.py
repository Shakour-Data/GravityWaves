from app import app, db
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--init-db":
        # Initialize the database tables
        with app.app_context():
            db.create_all()
        print("Database tables created successfully.")
        sys.exit(0)

    port = 5000
    if len(sys.argv) > 1 and sys.argv[1] == "--port" and len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            pass
    app.run(port=port)
