from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MegaSecretKey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

class Role(enum.Enum):
    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role), default=Role.USER, nullable=False)

    def check_password(self, pwd):
        print(self.password)
        print(pwd)
        return self.password == pwd

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.Integer, nullable=False)
    date_order = db.Column(db.DateTime, nullable=False)
    date_delivery = db.Column(db.DateTime, nullable=False)
    delivery_point_id = db.Column(db.Integer, nullable=False)
    delivery_adress = db.Column(db.String(255), nullable=False)
    client_name = db.Column(db.String(255), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True) # article
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    provider = db.Column(db.String(255), nullable=False)
    maker = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    sale = db.Column(db.Integer, nullable=False)
    #cost_with_sale = db.Column(db.Float, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    disc = db.Column(db.String(255), nullable=False)

class PickupsPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, unique=True, nullable=False)
    adress = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Успешный вход!','success')
            return redirect(url_for('products'))
        else:
            flash('Неверный логин или пароль.', 'error')
    return render_template('index.html')

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

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