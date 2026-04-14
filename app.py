from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from groq import Groq
from PIL import Image
import pytesseract
import pymysql
import pickle
import nltk
import json
import re
import functools
from nltk.corpus import stopwords
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')

# tesseract location
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# database connection
con = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

# login setup
lm = LoginManager(app)
lm.login_view = 'login'

# load trained model
with open('model/model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('model/tfidf.pkl', 'rb') as f:
    tfidf = pickle.load(f)

# stopwords
nltk.download('stopwords')
sw = set(stopwords.words('english'))

# groq ai
ai = Groq(api_key=os.getenv("GROQ_API_KEY"))
# stats file path
STATS = r'F:\fakenews\stats.json'

# fake and real keywords
fake_kw = ['shocking', 'secret', 'exposed', 'unbelievable', 'breaking', 'conspiracy', 'hoax', 'viral', 'exclusive']
real_kw = ['according', 'confirmed', 'reported', 'official', 'government', 'research', 'study', 'announced']


def get_stats():
    try:
        with open(STATS, 'r') as f:
            return json.load(f)
    except:
        return {"total_checked": 0, "total_fake_caught": 0}


def update_stats(data):
    with open(STATS, 'w') as f:
        json.dump(data, f)


def clean(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    words = [w for w in text.split() if w not in sw]
    return ' '.join(words)


def find_keywords(text):
    words = text.lower().split()
    fk = [w for w in fake_kw if w in words]
    rk = [w for w in real_kw if w in words]
    return fk, rk


def ask_groq(text):
    try:
        res = ai.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""You are a professional fact checker. Analyze this news carefully.

Check:
1. Is this factually correct?
2. Does it have false claims about real people or events?
3. Is it sensational or misleading?

News: {text[:500]}

Reply in this exact format only:
Verdict: FAKE or REAL
Confidence: number between 75 and 99
Reason: one sentence"""
            }]
        )
        output = res.choices[0].message.content
        verdict = 'REAL'
        conf = 80
        reason = 'No reason'

        for line in output.split('\n'):
            if 'Verdict:' in line:
                verdict = 'FAKE' if 'FAKE' in line.upper() else 'REAL'
            if 'Confidence:' in line:
                try:
                    conf = int(''.join(filter(str.isdigit, line)))
                    conf = max(75, min(99, conf))
                except:
                    conf = 80
            if 'Reason:' in line:
                reason = line.replace('Reason:', '').strip()

        return {'verdict': verdict, 'conf': conf, 'reason': reason}
    except:
        return {'verdict': 'UNKNOWN', 'conf': 0, 'reason': 'AI not available'}


def rate_ok(uid):
    cur = con.cursor()
    cur.execute("SELECT checks_this_hour, last_check_time FROM users WHERE id = %s", (uid,))
    u = cur.fetchone()
    now = datetime.now()

    if u['last_check_time'] is None:
        return True

    diff = now - u['last_check_time']
    if diff > timedelta(hours=1):
        cur.execute("UPDATE users SET checks_this_hour = 0 WHERE id = %s", (uid,))
        return True

    if u['checks_this_hour'] >= 10:
        return False
    return True


def give_badge(uid):
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) as t FROM history WHERE user_id = %s", (uid,))
    total = cur.fetchone()['t']

    cur.execute("SELECT COUNT(*) as f FROM history WHERE user_id = %s AND result IN ('FAKE','SUSPICIOUS')", (uid,))
    fakes = cur.fetchone()['f']

    if total >= 10:
        cur.execute("SELECT * FROM badges WHERE user_id = %s AND badge_name = 'Fact Checker'", (uid,))
        if not cur.fetchone():
            cur.execute("INSERT INTO badges (user_id, badge_name) VALUES (%s, 'Fact Checker')", (uid,))

    if fakes >= 5:
        cur.execute("SELECT * FROM badges WHERE user_id = %s AND badge_name = 'News Detective'", (uid,))
        if not cur.fetchone():
            cur.execute("INSERT INTO badges (user_id, badge_name) VALUES (%s, 'News Detective')", (uid,))

    if total >= 50:
        cur.execute("SELECT * FROM badges WHERE user_id = %s AND badge_name = 'Truth Seeker'", (uid,))
        if not cur.fetchone():
            cur.execute("INSERT INTO badges (user_id, badge_name) VALUES (%s, 'Truth Seeker')", (uid,))


class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role


@lm.user_loader
def load_user(uid):
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (uid,))
    u = cur.fetchone()
    if u:
        return User(u['id'], u['username'], u['email'], u['role'])
    return None


def admin_only(f):
    @functools.wraps(f)
    def check(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return check


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        email = request.form['email']
        pwd = generate_password_hash(request.form['password'])
        cpwd = request.form['confirm_password']
        sq = request.form['security_question']
        sa = request.form['security_answer'].lower().strip()

        if request.form['password'] != cpwd:
            return render_template('register.html', error='Passwords do not match!')
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, email, password, security_question, security_answer) VALUES (%s,%s,%s,%s,%s)",
                        (uname, email, pwd, sq, sa))
            return redirect(url_for('login'))
        except:
            return render_template('register.html', error='Username or email already exists!')
    return render_template('register.html')


@app.route('/admin_setup', methods=['GET', 'POST'])
def admin_setup():
    CODE = 'keshavsharmaisgreat'
    if request.method == 'POST':
        uname = request.form['username']
        email = request.form['email']
        pwd = generate_password_hash(request.form['password'])
        cpwd = request.form['confirm_password']
        code = request.form['secret_code']

        if code != CODE:
            return render_template('admin_setup.html', error='Wrong secret code!')
        if request.form['password'] != cpwd:
            return render_template('admin_setup.html', error='Passwords do not match!')
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s,%s,%s,'admin')",
                        (uname, email, pwd))
            return redirect(url_for('login'))
        except:
            return render_template('admin_setup.html', error='Username or email already exists!')
    return render_template('admin_setup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (uname,))
        u = cur.fetchone()
        if u and check_password_hash(u['password'], pwd):
            login_user(User(u['id'], u['username'], u['email'], u['role']))
            return redirect(url_for('index'))
        return render_template('login.html', error='Wrong username or password!')
    return render_template('login.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html', step=1)

    step = int(request.form.get('step', 1))

    if step == 1:
        uname = request.form['username']
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (uname,))
        u = cur.fetchone()
        if not u:
            return render_template('forgot_password.html', step=1, error='Username not found!')
        return render_template('forgot_password.html', step=2, username=uname, question=u['security_question'])

    elif step == 2:
        uname = request.form['username']
        ans = request.form['answer'].lower().strip()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (uname,))
        u = cur.fetchone()
        if not u or u['security_answer'] != ans:
            return render_template('forgot_password.html', step=2, username=uname, question=u['security_question'], error='Wrong answer!')
        return render_template('forgot_password.html', step=3, username=uname)

    elif step == 3:
        uname = request.form['username']
        np = request.form['new_password']
        cp = request.form['confirm_password']
        if np != cp:
            return render_template('forgot_password.html', step=3, username=uname, error='Passwords do not match!')
        cur = con.cursor()
        cur.execute("UPDATE users SET password = %s WHERE username = %s", (generate_password_hash(np), uname))
        return render_template('login.html', success='Password reset! Please login.')

    return render_template('forgot_password.html', step=1)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) as total FROM history WHERE user_id = %s", (current_user.id,))
    total = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as f FROM history WHERE user_id = %s AND result IN ('FAKE','SUSPICIOUS')", (current_user.id,))
    caught = cur.fetchone()['f']

    cur.execute("SELECT * FROM history WHERE user_id = %s ORDER BY timestamp DESC LIMIT 5", (current_user.id,))
    hist = cur.fetchall()

    cur.execute("SELECT * FROM badges WHERE user_id = %s", (current_user.id,))
    badges = cur.fetchall()

    cur.execute("SELECT checks_this_hour, last_check_time FROM users WHERE id = %s", (current_user.id,))
    info = cur.fetchone()
    left = 10
    if info['last_check_time']:
        if datetime.now() - info['last_check_time'] <= timedelta(hours=1):
            left = 10 - info['checks_this_hour']

    return render_template('dashboard.html', total_checks=total, fake_caught=caught,
                           history=hist, badges=badges, checks_left=left)


@app.route('/admin')
@admin_only
def admin():
    cur = con.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("SELECT h.*, u.username FROM history h JOIN users u ON h.user_id = u.id ORDER BY h.timestamp DESC")
    all_hist = cur.fetchall()

    cur.execute("SELECT COUNT(*) as t FROM history")
    total = cur.fetchone()['t']

    cur.execute("SELECT COUNT(*) as f FROM history WHERE result IN ('FAKE','SUSPICIOUS')")
    fakes = cur.fetchone()['f']

    return render_template('admin.html', users=users, all_history=all_hist,
                           total_checks=total, total_fakes=fakes)


@app.route('/delete_user/<int:uid>')
@admin_only
def delete_user(uid):
    if uid == current_user.id:
        return redirect(url_for('admin'))
    cur = con.cursor()
    cur.execute("DELETE FROM history WHERE user_id = %s", (uid,))
    cur.execute("DELETE FROM badges WHERE user_id = %s", (uid,))
    cur.execute("DELETE FROM users WHERE id = %s", (uid,))
    return redirect(url_for('admin'))


@app.route('/stats')
def stats():
    return jsonify(get_stats())


@app.route('/predict', methods=['POST'])
def predict():
    text = ''

    if 'image' in request.files and request.files['image'].filename != '':
        img = Image.open(request.files['image'])
        text = pytesseract.image_to_string(img)
    else:
        text = request.form.get('news_text', '')

    extracted = text

    if not text.strip():
        return jsonify({'error': 'No text found!'})

    if len(text.strip()) < 5:
        return jsonify({'error': 'Please enter some text!'})

    if current_user.is_authenticated and current_user.role != 'admin':
        if not rate_ok(current_user.id):
            return jsonify({'error': 'Limit reached! Only 10 checks per hour allowed!'})

    # ml prediction
    vec = tfidf.transform([clean(text)])
    ml_result = model.predict(vec)[0]
    proba = model.predict_proba(vec)[0]
    confidence = round(max(proba) * 100, 2)

    fk, rk = find_keywords(text)
    groq = ask_groq(text)

    # final verdict logic
    show_graph = False
    graph_fake = 0
    graph_real = 0
    reason = ''

    if groq['verdict'] == 'UNKNOWN':
        final = ml_result
        graph_fake = confidence if ml_result == 'FAKE' else 100 - confidence
        graph_real = 100 - graph_fake

    elif ml_result == 'REAL' and groq['verdict'] == 'REAL':
        final = 'REAL'

    elif ml_result == 'FAKE' and groq['verdict'] == 'FAKE':
        final = 'FAKE'

    elif ml_result == 'REAL' and groq['verdict'] == 'FAKE':
        final = 'SUSPICIOUS'
        show_graph = True
        graph_fake = groq['conf']
        graph_real = 100 - graph_fake
        reason = groq['reason']

    else:
        final = 'REAL'
        reason = groq['reason']

    # update stats
    s = get_stats()
    s['total_checked'] += 1
    if final in ['FAKE', 'SUSPICIOUS']:
        s['total_fake_caught'] += 1
    update_stats(s)

    # save history and badges
    if current_user.is_authenticated:
        cur = con.cursor()
        if current_user.role != 'admin':
            cur.execute("UPDATE users SET checks_this_hour = checks_this_hour + 1, last_check_time = %s WHERE id = %s",
                        (datetime.now(), current_user.id))
        cur.execute("INSERT INTO history (user_id, news_text, result) VALUES (%s,%s,%s)",
                    (current_user.id, text[:500], final))
        give_badge(current_user.id)

    return jsonify({
        'prediction': final,
        'ml_confidence': confidence,
        'extracted_text': extracted[:500],
        'fake_keywords': fk,
        'real_keywords': rk,
        'show_graph': show_graph,
        'graph_fake': graph_fake,
        'graph_real': graph_real,
        'reason': reason
    })


if __name__ == '__main__':
    app.run(debug=True)
