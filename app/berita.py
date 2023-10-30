from . import app,mysql
from flask import render_template, request, jsonify
import os
import time
from PIL import Image
from io import BytesIO
import uuid


@app.route('/berita', methods=['GET'])
def get_berita():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM berita")
    surat = con.fetchall()
    info_list = []
    for sistem in surat:
        list_data = {
            'id': str(sistem[0]),
            'judul': str(sistem[1]),
            'gambar': str(sistem[2]),
            'deskripsi': str(sistem[3]),
            'tanggal': str(sistem[4])
        }
        info_list.append(list_data)
    return jsonify(info_list)

#input
@app.route('/admin/tambah_berita', methods=['POST'])
def tambah_berita():
    con = mysql.connection.cursor()
    judul = request.form['judul']
    link = judul
    link = link.replace("#", "")
    link = link.replace("?", "")
    link = link.replace("/", "")
    link = link.replace(" ", "_")
    file = request.files['gambar']
    if file:
            img = Image.open(file)
            img = img.convert('RGB')
            # Resize gambar
            width, height = 600, 300  # Atur sesuai kebutuhan Anda
            img = img.resize((width, height))

            # Simpan gambar yang diresize ke BytesIO
            img_io = BytesIO()
            img.save(img_io, 'JPEG', quality=70)
            img_io.seek(0)
            random_name = uuid.uuid4().hex+".jpg"
            destination = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
            img.save(destination)  # Ganti dengan lokasi penyimpanan yang diinginkan
            
            # Gunakan img_io atau file yang telah diresize sesuai kebutuhan Anda
    deskripsi = request.form['deskripsi']
    con.execute("INSERT INTO berita (judul, gambar , deskripsi,link ) VALUES (%s,%s,%s)",(judul,random_name,deskripsi,link))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")




