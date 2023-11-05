from . import app,mysql
from flask import render_template, request, jsonify,session,redirect,url_for
import os

from bcrypt import hashpw, gensalt, checkpw
import jwt 
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity,create_access_token

def check_password(usrpwd, password):
    return checkpw(password.encode('utf-8'), usrpwd.encode('utf-8'))   
    
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # .encode('utf-8')
        con = mysql.connection.cursor()
        con.execute("SELECT * FROM user_admin WHERE username = %s",(username,))
        users = con.fetchone()
        print(hashpw(password.encode('utf-8'), gensalt()).decode('utf-8'))
        if users is not None and len(users) > 0:
            if users and check_password(users[2], password):
                session['user_id'] = users[0]
                access_token = create_access_token(identity=users[0])
                session['JWT'] = access_token
                print(access_token)
                return redirect(url_for('admininfodesa'))
            else:
                error = 'Email atau password tidak valid'
                return redirect(url_for('login', error=error))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('admin/login.html')
    
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password'] # .encode('utf-8')
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM user_admin ")
    users = con.fetchall()
    print(users)
    if users == ():
        password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
        con.execute("INSERT INTO user_admin (username,password)VALUES (%s,%s)",(username,password))
        mysql.connection.commit()
        return jsonify({"msg":"register berhasil silakan login"})
    for user in users:
        if username == user[1]:
            return jsonify({"msg":"User sudah terdaftar silakan login"})
        else :
            password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
            con.execute("INSERT INTO user_admin (username,password)VALUES (%s,%s)",(username,password))
            mysql.connection.commit()
            return jsonify({"msg":"register berhasil silakan login"})
    
    