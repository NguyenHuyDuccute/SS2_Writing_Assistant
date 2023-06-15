import os
from functools import wraps
import pytz
import openai
from flask import Flask, redirect, render_template, request, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    activities = db.relationship('Activity', backref='user', lazy=True)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    input = db.Column(db.String(255), nullable=False)
    output = db.Column(db.String(1200), nullable=False)
    timestamp = db.Column(db.String(40), nullable=False)


with app.app_context():
    db.create_all()


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
    return render_template('grammar_check.html', is_logged_in=True, name=first_name, picture=picture)


@app.route("/paraphrasing", methods=['GET', 'POST'])
@login_required
def paraphrasing():
    name = session.get('name', 'Unknown')
    picture = session.get('picture', 'Unknown')
    first_name = name.split()[0]
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
            prompt=f"Plagiarism two documents for two content and only show percentage:\n\n{input_text}.",
            temperature=0.0,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        corrected_text = response.choices[0].text.strip()
        user_email = User.query.filter_by(email=session['email']).first().email
        current_time = datetime.now(pytz.utc).astimezone(pytz.timezone('Asia/Bangkok'))
        formatted_time = current_time.strftime("%H:%M %d-%m-%Y")
        activity = Activity(user_email=user_email, activity_type='Grammar Check',
                            input=input_text, output=corrected_text, timestamp=formatted_time)
        db.session.add(activity)
        db.session.commit()
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
        user_email = User.query.filter_by(email=session['email']).first().email
        current_time = datetime.now(pytz.utc).astimezone(pytz.timezone('Asia/Bangkok'))
        formatted_time = current_time.strftime("%H:%M %d-%m-%Y")
        activity = Activity(user_email=user_email, activity_type='Text completion',
                            input=input_text, output=corrected_text, timestamp=formatted_time)
        db.session.add(activity)
        db.session.commit()
        return corrected_text


@app.route("/text-completion", methods=(['GET', 'POST']))
@login_required
def text_completion():
    name = session.get('name', 'Unknown')
    picture = session.get('picture', 'Unknown')
    first_name = name.split()[0]
    return render_template('text_completion.html', is_logged_in=True, name=first_name, picture=picture)


@app.route("/user-activities")
@login_required
def user_activities():
    name = session.get('name', 'Unknown')
    picture = session.get('picture', 'Unknown')
    first_name = name.split()[0]
    user_email = session['email']
    user = User.query.filter_by(email=user_email).first()
    activities = user.activities
    activities = list(reversed(activities))
    return render_template('user_activities.html', activities=activities, is_logged_in=True, name=first_name, picture=picture)


@app.route('/delete_activity/<activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Activity not found"})


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
    email = user_info['email']
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email, name=user_info.get('name', 'Unknown'))
        db.session.add(user)
        db.session.commit()
    session['email'] = email
    session['name'] = user.name
    session['picture'] = user_info.get('picture', 'Unknown')
    next_url = session.get('next') or url_for('index')
    return redirect(next_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
