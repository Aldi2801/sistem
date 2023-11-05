from flask import Flask,request,session
from flask_mysqldb import MySQL 
import bcrypt

from flask_jwt_extended import JWTManager
from flask_cors import CORS

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']  = ''
app.config['MYSQL_DB'] = 'sistem'
app.config['UPLOAD_FOLDER'] = 'D:/KULIAH/sistemdesa/app/static/image'
app.config['SECRET_KEY'] = 'bukan rahasia'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = b'asahdjhwquoyo192382qo'
app.config['JWT_SECRET_KEY'] = 'secret_key_for_jwt'  # Kunci rahasia untuk tanda tangan JWT
jwt = JWTManager(app)
mysql.init_app(app)
app.secret_key = 'your_secret_key'  # Set session secret key


from . import infodesa, surat, berita, dana, login, warga, umkm, apihalaman