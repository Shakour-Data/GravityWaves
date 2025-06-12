from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask.cli import with_appcontext
import click
from pln_app import app, db

migrate = Migrate(app, db)

@app.cli.command()
@with_appcontext
def db_init():
    """Initialize the database."""
    from flask_migrate import init
    init()

@app.cli.command()
@with_appcontext
def db_migrate():
    """Create a new migration."""
    from flask_migrate import migrate
    migrate(message="Auto migration")

@app.cli.command()
@with_appcontext
def db_upgrade():
    """Apply migrations."""
    from flask_migrate import upgrade
    upgrade()

if __name__ == "__main__":
    app.run()
