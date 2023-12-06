from . import app,db,bcrypt,user_datastore,security,jwt,Role,User
from flask import request,render_template,redirect,url_for,jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
    
@app.route('/masuk')
def masuk():
    return render_template('admin/admin.html')
# Endpoint untuk membuat token
@app.route('/proses_masuk', methods=['POST'])
def login():
        username = request.json['username']
        password = request.json['password']

        # Seharusnya Anda memverifikasi kredensial pengguna di sini
        # Misalnya, memeriksa username dan password di database
        if user_datastore.find_user(username=username):
            user = user_datastore.find_user(username=username)
        else:
            return "false"
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=username)
            return access_token
        else:
            return "false"

# Endpoint yang memerlukan autentikasi
@app.route('/logout')
@jwt_required()
def logout():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return redirect(url_for('masuk', msg='logout sukses'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        # Check if the username already exists
        print(username+' | '+password+' | ')
        if user_datastore.find_user(username=username):
            return jsonify({"msg": "Username already exists"}), 400

        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        user = user_datastore.create_user(username=username, password=hashed_password, active=True)
        db.session.commit()

        return redirect(url_for('masuk', msg='Registration Successful'))

    return render_template('admin/register.html')

@jwt.expired_token_loader
def expired_token_callback():
    return redirect(url_for('login'))