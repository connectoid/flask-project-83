from flask import (Flask, render_template)


app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route("/")
def index():
    context = 'Context'
    return render_template(
        'index.html',
        context=context
    )
