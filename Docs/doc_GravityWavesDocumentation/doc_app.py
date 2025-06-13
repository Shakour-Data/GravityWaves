from flask import Flask, render_template
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    return render_template('doc_index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
