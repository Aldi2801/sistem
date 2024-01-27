from flask import Flask,jsonify,request,session,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_bcrypt import Bcrypt
from datetime import timedelta
from functools import wraps
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sistem'
project_directory = os.path.abspath(os.path.dirname(__file__))
upload_folder = os.path.join(project_directory, 'static', 'image')
app.config['UPLOAD_FOLDER'] = upload_folder 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/sistem'
app.config['SECRET_KEY'] = 'bukan rahasia'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = b'asahdjhwquoyo192382qo'
app.config['JWT_SECRET_KEY'] = 'qwdu92y17dqsu81'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Define the 'user_roles' class before 'User' class
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary='user_roles', 
                            primaryjoin='User.id == UserRoles.user_id',
                            secondaryjoin='Role.id == UserRoles.role_id',
                            backref=db.backref('users', lazy='dynamic'))
    fs_uniquifier = db.Column(db.String(64), unique=True)
    
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(datastore=user_datastore, app=app)

jwt = JWTManager(app)
mysql = MySQL()
mysql.init_app(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        jwt_required()
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400
        
        # Check if the username already exists
        print(username+' | '+password+' | ')
        if user_datastore.find_user(username=username):
            return jsonify({"msg": "Username already  exists"}), 400

        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        user = user_datastore.create_user(username=username, password=hashed_password, active=True)
        db.session.commit()

        return redirect(url_for('masuk', msg='Registration Successful'))

    return render_template('admin/register.html')
# Import rute dari modul-modul Anda
from . import api_user, api_admin, login
