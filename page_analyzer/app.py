import os
from datetime import date

from flask import (Flask, render_template, url_for, request, flash, redirect, abort)
import psycopg2
from dotenv import load_dotenv

from url_repository import URLRepository
from validators.url import url as check_url

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
repo = URLRepository(conn)

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route("/")
def index():
    context = 'Context'
    errors = {}
    return render_template(
        'index.html',
        context=context, errors=errors
    )


@app.route('/urls')
def urls_list():
    urls = repo.get_content()
    errors = {}
    return render_template(
        'urls/index.html',
        urls=urls,
        errors=errors
    )



@app.route('/urls', methods=['POST'])
def urls_post():
    url_data = request.form.to_dict()
    errors = {}
    is_valid_url = check_url(url_data['url'])
    if not is_valid_url:
        errors['url'] = 'Некорректный URL'
    if errors:
        return render_template(
            'index.html',
            url=url_data,
            errors=errors
        ), 422
    created_at = date.today()
    url = {'name': url_data['url'], 'created_at': created_at}
    id = repo.save(url)
    flash('Site was added successfully', 'success')
    return redirect(url_for('urls_show', id=id, errors=errors))


@app.route('/urls/<int:id>')
def urls_show(id):
    errors = {}
    url = repo.find(id)
    if not url:
        abort(404)
    return render_template(
        'urls/show.html',
        url=url,
        errors=errors
    )