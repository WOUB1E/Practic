from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Role(enum.Enum):
    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role), default=Role.USER, nullable=False)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            role=Role[request.form['role']]
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/status')
def status():
    return {
        'users_count': User.query.count(),
        'database': 'PostgreSQL',
        'connection': 'OK'
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)