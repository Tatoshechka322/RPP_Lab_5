from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = '09990'
user_db = "ershtrub"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "lab5"
password = "postgres"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

# Инициализация LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Загрузка пользователя по ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Корневая страница
@app.route('/')
def index():
    if current_user.is_authenticated:
        # Авторизованный пользователь
        return render_template('index.html', user=current_user.name)
    else:
        # Неавторизованный пользователь
        return redirect(url_for('login'))

# Страница вход
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    errors = []
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    # Ошибка: поля не заполнены
    if email == '' or password == '':
        errors.append('Пожалуйста, заполните все поля')

    # Ошибка: пользователь отсутствует
    if user is None:
        errors.append('Такой пользователь отсутствует')

    # Ошибка: неправильный пароль
    if user and user.password != password:
        errors.append('Неверный пароль')

    if user and user.password == password:
        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html', errors=errors, email=email, password=password)

# Страница регистрации
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('signup.html', error='Пользователь с таким логином уже существует')

        new_user = User(email=email, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
  app.run(debug=True)
