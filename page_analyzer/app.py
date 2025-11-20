import os
from datetime import date
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from flask import (Flask, render_template, url_for, request, flash, redirect, abort, get_flashed_messages)
import psycopg2
from dotenv import load_dotenv

from url_repository import URLRepository
from validators.url import url as check_url

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
print(f'============ DATABASE URL: {DATABASE_URL}')
conn = psycopg2.connect(DATABASE_URL)
repo = URLRepository(conn) 

app = Flask(__name__)
app.secret_key = 'secret_key'


def get_seo_data(url):
    print('Strat seo testing')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    seo_data = {}

    seo_data['h1'] = soup.find('h1').text if soup.find('h1') else ''
    seo_data['title'] = soup.find('title').text if soup.find('title') else ''
    try:
        seo_data['description'] = soup.find('meta')['content'].text if soup.find('meta')['content'] else ''
    except Exception:
        seo_data['description'] = ''
    return seo_data


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
    for url in urls:
        last_check = repo.get_last_check(url['id'])
        url['last_check'] = last_check.created_at if last_check and last_check.created_at else ''
        url['status_code'] = last_check.status_code if last_check and last_check.status_code else ''
        print(urls)
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
    
    url = repo.get_url_by_name(url_data['url'])
    if not url:
        url = {'name': url_data['url'], 'created_at': created_at}
        id = repo.save(url)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('urls_show', id=id, errors=errors))
    else:
        flash('Страница уже существует', 'success')
        id = url['id']
    return redirect(url_for('urls_show', id=id, errors=errors))


@app.route('/urls/<int:id>')
def urls_show(id):
    errors = {}
    checks = repo.get_checks(id)

    url = repo.find(id)
    messages = get_flashed_messages(with_categories=True)
    last_check = repo.get_last_check(id)
    print(f'Last check: {last_check}')
    if not url:
        abort(404)
    return render_template(
        'urls/show.html',
        url=url,
        checks=checks,
        errors=errors,
        messages=messages
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def url_check(id):
    errors = {}
    url = repo.find(id)
    created_at = date.today()
    try:
        response = requests.get(url['name'])
        response.raise_for_status()
        seo_data = get_seo_data(url['name'])
        pprint(seo_data)
        status_code = response.status_code
        check_id = repo.check(id, created_at, seo_data['h1'], seo_data['title'], seo_data['description'], status_code)
        checks = repo.get_checks(id)
    except Exception as e:
        print(f'Ошибка HTTP: {e}')
        flash('Произошла ошибка при проверке', 'danger')
    return redirect(url_for('urls_show', id=id))

    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'urls/show.html',
        url=url,
        checks=checks,
        errors=errors,
        messages=messages
    )