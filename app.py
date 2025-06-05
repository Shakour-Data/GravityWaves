from app import app
import sys

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1] == "--port" and len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            pass
    app.run(port=port)
