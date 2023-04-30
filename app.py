import os
from functools import wraps

import openai
from flask import Flask, redirect, render_template, request, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'random secret'
# openai
openai.api_key = os.getenv("OPENAI_API_KEY")
# oauth config
oauth = OAuth(app)
app.config['GOOGLE_CLIENT_ID'] = "563039761492-tr2s6c24bjps7ks2f69ja8f4oje940kj.apps.googleusercontent.com"
app.config['GOOGLE_CLIENT_SECRET'] = "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"

google = oauth.register(
    name='google',
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={
        'scope': 'openid email profile',
        'jwks_uri': 'https://www.googleapis.com/oauth2/v3/certs'
    },
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'

)


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'email' not in session:
            session['next'] = request.url
            return redirect(url_for('google_login'))
        return func(*args, **kwargs)

    return decorated_view


@app.route("/grammar-check", methods=['GET', 'POST'])
@login_required
def grammar_check():
    if request.method == "POST":
        input_text = request.form['text']
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Correct this to standard English:\n\n{input_text}.",
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        corrected_text = response.choices[0].text.strip()
        return render_template('grammar_check.html', corrected_text=corrected_text, is_logged_in=True)
    return render_template('grammar_check.html', is_logged_in=True)


# Correct this to standard English

@app.route("/grammar-check-post", methods=['POST'])
def test():
    if request.method == "POST":
        input_text = request.form['text']
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Correct this to standard English:\n\n{input_text}.",
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        corrected_text = response.choices[0].text.strip()
        return corrected_text


@app.route('/')
def index():
    if 'email' in session:
        return render_template('base.html', is_logged_in=True)
    else:
        return render_template('base.html', is_logged_in=False)


@app.route("/text-completion", methods=(['GET', 'POST']))
@login_required
def text_completion():
    return render_template('text_completion.html', is_logged_in=True)

@app.route('/login')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    next_url = request.args.get('next', None)
    if next_url:
        redirect_uri += f'?next={next_url}'
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def google_authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    next_url = session.get('next') or url_for('index')
    return redirect(next_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
