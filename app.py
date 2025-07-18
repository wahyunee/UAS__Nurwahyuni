import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import pymysql

# Daftarkan PyMySQL sebagai driver MySQLdb
pymysql.install_as_MySQLdb()

# Muat .env
load_dotenv()

# Ambil dan bersihkan URL database
raw_db_url = os.getenv('DATABASE_URL', '')
db_url = raw_db_url.strip().strip('"').strip("'")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']    = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ======= Auto-init tables on import =======
with app.app_context():
    db.create_all()

# Model Post
class Post(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    title   = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)

# ======= CLI command =======
@app.cli.command("init-db")
def init_db():
    """Initialize database tables manually."""
    db.create_all()
    print("✅ Tables created.")

# ROUTES
@app.route('/')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        new = Post(title=request.form['title'],
                   content=request.form['content'])
        db.session.add(new)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.title   = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', post=post)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Kalau kamu jalankan dengan `python app.py`
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
