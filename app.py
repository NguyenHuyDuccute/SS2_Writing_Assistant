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
    name = session.get('name', 'Unknown')
    picture = session.get('picture', 'Unknown')
    first_name = name.split()[0]
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
        return render_template('grammar_check.html', corrected_text=corrected_text, is_logged_in=True, name=first_name,
                               picture=picture)
    return render_template('grammar_check.html', is_logged_in=True, name=first_name, picture=picture)


@app.route("/paraphrasing", methods=['GET', 'POST'])
@login_required
def paraphrasing():
    name = session.get('name', 'Unknown')
    picture = session.get('picture', 'Unknown')
    first_name = name.split()[0]
    if request.method == "POST":
        input_text = request.form['text']
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"paraphase the following paragraph, using as few words from the original paragraph as possible:\n\n{input_text}.",
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        corrected_text = response.choices[0].text.strip()
        return render_template('paraphrasing.html', corrected_text=corrected_text, is_logged_in=True, name=first_name,
                               picture=picture)
    return render_template('paraphrasing.html', is_logged_in=True, name=first_name, picture=picture)


@app.route("/paraphrasing-post", methods=['POST'])
def paraphrasing_post():
    if request.method == "POST":
        input_text = request.form['text']
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"paraphase and provide several paraphrased versions(serial numbering on each version) the following paragraph, using as few words from the original paragraph as possible:\n\n{input_text}.",
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        corrected_text = response.choices[0].text.strip()
        return corrected_text


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
        name = session.get('name', 'Unknown')
        picture = session.get('picture', 'Unknown')
        first_name = name.split()[0]
        return render_template('base.html', is_logged_in=True, name=first_name, picture=picture)
    else:
        return render_template('base.html', is_logged_in=False)


@app.route("/text-completion-post", methods=['POST'])
def text_completion_post():
    if request.method == "POST":
        input_text = request.form['text']
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Pick up where the user left off and complete the input text with generated sentences:\n\n{input_text}.",
            temperature=0.7,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        corrected_text = response.choices[0].text.strip()
        return corrected_text


@app.route("/text-completion", methods=(['GET', 'POST']))
@login_required
def text_completion():
    name = session.get('name', 'Unknown')
    picture = session.get('picture', 'Unknown')
    first_name = name.split()[0]
    return render_template('text_completion.html', is_logged_in=True, name=first_name, picture=picture)


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
    session['name'] = user_info.get('name', 'Unknown')
    session['picture'] = user_info.get('picture', 'Unknown')
    next_url = session.get('next') or url_for('index')
    return redirect(next_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
