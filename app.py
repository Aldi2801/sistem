from app import app,db
#ssl_context='adhoc'
from flask import request, jsonify
import datetime
from app import db, User, Role, UserRoles, bcrypt
from werkzeug.security import generate_password_hash
import uuid

@app.route('/chatbot/get')
def chatbot():
  userText = request.args.get('msg')
  tanggal = datetime.datetime.now()
  tanggal_baru = tanggal.strftime('%Y-%m-%d %H:%M:%S')
  import chatbot
  respon = chatbot.generate_response(userText)
  print(respon)
  return respon
if __name__ == '__main__':
    with app.app_context():
      db.create_all()
            
      # # 1. Buat Role baru
      # role_admin = Role(name='admin')

      # # Hash password sebelum disimpan
      # hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
      # # Membuat pengguna baru
      # # 2. Buat User baru
      # user_admin = User(
      #     username='admin',
      #     password=hashed_password,  # Gunakan hashing
      #     active=True,
      #     fs_uniquifier=str(uuid.uuid4())
      # )

      # # 3. Commit User dan Role dulu ke DB agar dapat ID-nya
      # db.session.add(role_admin)
      # db.session.add(user_admin)
      # db.session.commit()

      # # 4. Buat relasi UserRoles
      # user_role = UserRoles(user_id=user_admin.id, role_id=role_admin.id)
      # db.session.add(user_role)
      # db.session.commit()

      # print("Seeder selesai: user 'admin' dengan role 'admin' ditambahkan.")
    app.run(host="0.0.0.0", debug=True, port=4040)