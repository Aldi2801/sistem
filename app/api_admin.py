from . import app,mysql,db
from flask import render_template, request, jsonify, redirect, url_for,session
import os
import pandas as pd
import textwrap
from PIL import Image
from io import BytesIO
import locale
import uuid
import time
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

#halaman admin
@app.route('/admin/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

#sejarah
@app.route('/admin/infodesa')
def admininfodesa():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM sejarah_desa")
    sejarah = con.fetchall()
    print(sejarah)
    info_list = []
    for sistem in sejarah:
        print(sistem)
        list_data = {
            'id': str(sistem[0]),
            'sejarah': str(sistem[1]),
            'visi': str(sistem[2]),
            'misi': sistem[3]
        }
        info_list.append(list_data)
    return render_template("admin/infodesa.html", info_list = info_list)

#tambah info
@app.route('/tambah_info', methods=['POST'])
@jwt_required()
def tambah_info():
    con = mysql.connection.cursor()
    sejarah = request.form['sejarah']
    visi = request.form['visi']
    misi = request.form['misi']
    con.execute("INSERT INTO sejarah (sejarah , visi, misi) VALUES (%s,%s,%s)",(sejarah , visi, misi))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")

#edit info data
@app.route('/edit_info', methods=['POST'])
@jwt_required()
def edit_info():
    con = mysql.connection.cursor()
    id = request.form['id']
    sejarah = request.form['sejarah']
    visi = request.form['visi']
    
    misi = request.form['misi']
    con.execute("UPDATE sejarah_desa SET sejarah = %s, visi = %s, misi = %s WHERE id = %s",(sejarah,visi,misi,id))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")
@app.route('/admin/edit_sejarah', methods=['GET','POST'])
def edit_sejarah():
    if request.method == 'POST':
        jwt_required()
        con = mysql.connection.cursor()
        sejarah = request.form['sejarah']
        print(str(sejarah))
        con.execute("UPDATE sejarah_desa SET sejarah = %s WHERE id = 1",(str(sejarah),))
        mysql.connection.commit()
        return jsonify("msg : SUKSES")
    else:
        con = mysql.connection.cursor()
        con.execute("SELECT * FROM sejarah_desa WHERE id = 1") 
        info = con.fetchone() 
        return render_template("admin/editsejarah.html",info=info)
    
#visimisi
@app.route('/admin/visimisi')
def adminvisimisi():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM sejarah_desa")
    visi = con.fetchall()
    info_list = []
    for sistem in visi:
        print(sistem)
        list_data = {
            'id': str(sistem[0]),
            'sejarah': str(sistem[1]),
            'visi': str(sistem[2]),
            'misi': sistem[3]
        }
        info_list.append(list_data)
    return render_template("admin/visimisi.html", info_list = info_list)

@app.route('/admin/visiedit', methods=['POST'])
@jwt_required()
def adminvisiedit():
    con = mysql.connection.cursor()
    visi = request.form['visi']
    visi = str(visi)
    con.execute("UPDATE sejarah_desa SET visi= %s WHERE id = 1",(visi,))
    mysql.connection.commit()
    return redirect(url_for("adminvisimisi"))

@app.route('/admin/misiedit', methods=['POST'])
@jwt_required()
def adminmisiedit():
    con = mysql.connection.cursor()
    misi = request.form['misi']
    misi = str(misi)
    con.execute("UPDATE sejarah_desa SET misi= %s WHERE id = 1",(misi,))
    mysql.connection.commit()
    return redirect(url_for("adminvisimisi"))
    
#berita
@app.route('/admin/berita')
def admindberita():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM berita order by id DESC")
    berita = con.fetchall()
    info_list = []
    for sistem in berita:
        des = str(sistem[3])
        des = textwrap.shorten(des,width=75, placeholder="...")
        list_data = {
            'id': str(sistem[0]),
            'judul': str(sistem[1]),
            'gambar': str(sistem[2]),
            'deskripsi': des,
            'deskripsifull': str(sistem[3]),
            'tanggal': str(sistem[4])
        }
        info_list.append(list_data)
    return render_template("admin/berita.html", info_list = info_list)

@app.route('/admin/tambah_berita', methods=['POST'])
@jwt_required()
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

@app.route('/admin/edit_berita', methods=['POST'])
@jwt_required()
def edit_berita():
    con = mysql.connection.cursor()
    id = request.form['id']
    judul = request.form['judul']
    try:
        if request.files['gambar']:
            file = request.files['gambar']
            con.execute("SELECT gambar FROM berita WHERE id = %s", (id,))
            result = con.fetchone()
            if result:
                filename = result[0]
        
            # Delete the image file
                if filename:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        
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
            deskripsi = request.form['deskripsi']
            con.execute("UPDATE berita SET judul = %s, gambar = %s, deskripsi = %s WHERE id = %s",(judul,random_name,deskripsi,id))
            mysql.connection.commit()
            # Gunakan img_io atau file yang telah diresize sesuai kebutuhan Anda
    except:
        deskripsi = request.form['deskripsi']
        con.execute("UPDATE berita SET judul = %s, deskripsi = %s WHERE id = %s",(judul,deskripsi,id))
        mysql.connection.commit()
    return jsonify({"msg" : "SUKSES"})

@app.route('/hapus_berita', methods=['POST'])
@jwt_required()
def hapus_berita():
    con = mysql.connection.cursor()
    id = request.form['id']
    
    # Get the filename of the image associated with the news article
    con.execute("SELECT gambar FROM berita WHERE id = %s", (id,))
    result = con.fetchone()
    if result:
        filename = result[0]
        
        # Delete the image file
        if filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(image_path):
                os.remove(image_path)
    
    # Delete the news article from the database
    con.execute("DELETE FROM berita WHERE id = %s", (id,))
    mysql.connection.commit()
    return jsonify({"msg": "SUKSES"})

#hapus anggota
@app.route('/hapus_anggota', methods=['POST'])
@jwt_required()
def hapus_anggota():
    con = mysql.connection.cursor()
    id = request.form['id']
    
    # Get the filename of the image associated with the news article
    con.execute("SELECT gambar FROM anggota WHERE id = %s", (id,))
    result = con.fetchone()
    if result:
        filename = result[0]
        
        # Delete the image file
        if filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(image_path):
                os.remove(image_path)
    
    # Delete the news article from the database
    con.execute("DELETE FROM anggota WHERE id = %s", (id,))
    mysql.connection.commit()
    return jsonify({"msg": "SUKSES"})
#Dana
@app.template_filter('format_currency')
def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    return locale.currency(value, grouping=True, symbol='')

@app.route('/admin/dana')
def admindana():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM realisasi_pendapatan order by id")
    dana = con.fetchall()
    info_list = []

    for sistem in dana:
        list_data = {
            'id': str(sistem[0]),
            'no': str(sistem[1]),
            'uraian': str(sistem[2]),
            'anggaran': format_currency(int(sistem[3])),  # Menggunakan format_currency untuk mengubah anggaran
            'realisasi': format_currency(int(sistem[4])),  # Menggunakan format_currency untuk mengubah realisasi
            'lebih_kurang': format_currency(int(sistem[5])),  # Menggunakan format_currency untuk mengubah lebih_kurang
            'tahun': str(sistem[6])
        }
        info_list.append(list_data)
        
    con.execute("SELECT * FROM realisasi_belanja  order by id")
    dana = con.fetchall()
    info_list2 = []

    for sistem in dana:
        list_data = {
            'id': str(sistem[0]),
            'no': str(sistem[1]),
            'uraian': str(sistem[2]),
            'anggaran': format_currency(int(sistem[3])),  # Menggunakan format_currency untuk mengubah anggaran
            'realisasi': format_currency(int(sistem[4])),  # Menggunakan format_currency untuk mengubah realisasi
            'lebih_kurang': format_currency(int(sistem[5])),  # Menggunakan format_currency untuk mengubah lebih_kurang
            'tahun': str(sistem[6])
        }
        info_list2.append(list_data)
        
    con.execute("SELECT * FROM realisasi_pembiayaan  order by id")
    dana = con.fetchall()
    info_list3 = []

    for sistem in dana:
        list_data = {
            'id': str(sistem[0]),
            'no': str(sistem[1]),
            'uraian': str(sistem[2]),
            'anggaran': format_currency(int(sistem[3])),  # Menggunakan format_currency untuk mengubah anggaran
            'realisasi': format_currency(int(sistem[4])),  # Menggunakan format_currency untuk mengubah realisasi
            'lebih_kurang': format_currency(int(sistem[5])),  # Menggunakan format_currency untuk mengubah lebih_kurang
            'tahun': str(sistem[6])
        }
        info_list3.append(list_data)
        
    con.execute("SELECT * FROM realisasi_pendapatan group by tahun ")
    data_thn = con.fetchall()
    thn = []

    for sistem in data_thn:
        list_data = {
            'tahun': str(sistem[6])
        }
        thn.append(list_data)
        
    return render_template("admin/dana.html", info_list=info_list, info_list2=info_list2, info_list3=info_list3, tahun=thn)



@app.route('/admin/edit_dana', methods=['POST'])
@jwt_required()
def edit_dana():
    con = mysql.connection.cursor()
    id = request.form['id']
    tahun = request.form['tahun']
    dana = request.form['dana']
    digunakan = request.form['digunakan']
    sisah = request.form['sisah']
    con.execute("UPDATE dana SET tahun = %s, dana = %s, keterangan = %s, sisah = %s WHERE id = %s",(tahun,dana,digunakan,sisah,id))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")

#hapus
@app.route('/admin/hapus_dana', methods=['POST'])
@jwt_required()
def hapus_dana():
    con = mysql.connection.cursor()
    id = request.form['id']
    con.execute("DELETE FROM dana WHERE id = %s",(id))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")

@app.route('/admin/tambah_dana', methods=['POST'])
@jwt_required()
def tambah_dana():
    con = mysql.connection.cursor()
    filependapatan = request.files['excellpendapatan']
    filebelanja  = request.files['excellbelanja']
    filepembiayaan = request.files['excellpembiayaan']
    if filependapatan:
        df = ""
        df = pd.read_excel(filependapatan)
        # Insert data from the DataFrame into MySQL
        for index, row in df.iterrows():
            sql = "INSERT INTO realisasi_pendapatan (no,uraian,anggaran,realisasi,`lebih/(kurang)`,tahun) VALUES (%s, %s, %s,%s,%s,%s)"
            con.execute(sql, (row[0],row[1],row[2],row[3],row[4],row[5]))
    if filebelanja:
        df =""
        df = pd.read_excel(filebelanja)
        # Insert data from the DataFrame into MySQL
        for index, row in df.iterrows():
            sql = "INSERT INTO realisasi_belanja (no,uraian,anggaran,realisasi,`lebih/(kurang)`,tahun) VALUES (%s, %s, %s,%s,%s,%s)"
            con.execute(sql, (row[0],row[1],row[2],row[3],row[4],row[5]))
            mysql.connection.commit()
    if filepembiayaan:
        df = ""
        df = pd.read_csv(filepembiayaan)
        # Insert data from the DataFrame into MySQL
        data = ""
        for index, row in df.iterrows():
            
            data = row[0].split(";")
            sql = "INSERT INTO realisasi_pembiayaan (no,uraian,anggaran,realisasi,`lebih/(kurang)`,tahun) VALUES (%s, %s, %s,%s,%s,%s)"
            con.execute(sql, (data[0],data[1],data[2],data[3],data[4],data[5]))
            mysql.connection.commit()
               
    return redirect(url_for("admindana"))

#geografi
@app.route('/admin/geografi')
def admingeo():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM tanah")
    tanah = con.fetchall()
    info_list = []
    for sistem in tanah:
        list_data = {
            'id': str(sistem[0]),
            'luas': str(sistem[1]),
            'sawahteri': str(sistem[2]),
            'sawahhu': str(sistem[3]),
            'pemukiman': str(sistem[4])
        }
        info_list.append(list_data)
        
    con.execute("SELECT * FROM wilayah")
    wilayah = con.fetchall()
    info_list2 = []
    for sistem2 in wilayah:
        list_data2 = {
            'id': str(sistem2[0]),
            'utara': str(sistem2[1]),
            'selatan': str(sistem2[2]),
            'timur': str(sistem2[3]),
            'barat': str(sistem2[4])
        }
        info_list2.append(list_data2)
        
    return render_template("admin/geografi.html", info_list=info_list, info_list2=info_list2)

@app.route('/admin/wilayah', methods=['POST'])
@jwt_required()
def adminwilayahedit():
        con = mysql.connection.cursor()
        utara = request.form['utara']
        selatan = request.form['selatan']
        timur= request.form['timur']
        barat = request.form['barat']
        print(str(utara))
        print(str(selatan))
        print(str(timur))
        print(str(barat))
        con.execute("UPDATE wilayah SET utara = %s, selatan = %s, timur = %s, barat = %s WHERE id = 1",(str(utara),str(selatan),str(timur),str(barat)))
        mysql.connection.commit()
        return redirect(url_for("admingeo"))
    
@app.route('/admin/tanah', methods=['POST'])
@jwt_required()
def admintanahedit():
        con = mysql.connection.cursor()
        luas = request.form['luas']
        sawahteri = request.form['sawahteri']
        sawahhu= request.form['sawahhu']
        pemukiman = request.form['pemukiman']
        print(str(luas))
        print(str(sawahteri))
        print(str(sawahhu))
        print(str(pemukiman))
        con.execute("UPDATE tanah SET luas = %s, sawahteri = %s, sawahhu = %s, pemukiman = %s WHERE id = 1",(str(luas),str(sawahteri),str(sawahhu),str(pemukiman)))
        mysql.connection.commit()
        return redirect(url_for("admingeo"))


#monografi
@app.route('/admin/monografi')
def adminmono():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM monografi")
    mono = con.fetchall()
    info_list = []
    for sistem in mono:
        list_data = {
            'id': str(sistem[0]),
            'tahun': str(sistem[1]),
            'jpenduduk': str(sistem[2]),
            'jkk': str(sistem[3]),
            'laki': str(sistem[4]),
            'perempuan': str(sistem[5]),
            'jkkprese': str(sistem[6]),
            'jkkseja': str(sistem[7]),
            'jkkkaya': str(sistem[8]),
            'jkksedang': str(sistem[9]),
            'jkkmiskin': str(sistem[10]),
            'islam': str(sistem[11]),
            'kristen': str(sistem[12]),
            'protestan': str(sistem[13]),
            'katolik': str(sistem[14]),
            'hindu': str(sistem[15]),
            'budha': str(sistem[16])
        }
        info_list.append(list_data)
    return render_template("admin/monografi.html", info_list = info_list)

@app.route('/admin/monoedit', methods=['POST'])
@jwt_required()
def adminmonoedit():
        con = mysql.connection.cursor()
        jpenduduk = request.form['jpenduduk']
        jkk = request.form['jkk']
        laki= request.form['laki']
        perempuan = request.form['perempuan']
        jkkprese = request.form['jkkprese']
        jkkseja = request.form['jkkseja']
        jkkkaya = request.form['jkkkaya']
        jkksedang = request.form['jkksedang']
        jkkmiskin = request.form['jkkmiskin']
        islam= request.form['islam']
        kristen= request.form['kristen']
        protestan= request.form['protestan']
        katolik= request.form['katolik']
        hindu= request.form['hindu']
        budha= request.form['budha']
        
        query = """
        UPDATE monografi 
        SET jpenduduk = %s, jkk = %s, laki = %s, perempuan = %s, 
            jkkprese = %s, jkkseja = %s, jkkkaya = %s, jkksedang = %s, 
            jkkmiskin = %s, islam = %s, kristen = %s, protestan = %s, 
            katolik = %s, hindu = %s, budha = %s 
        WHERE id = 1
    """
        con.execute(query, (
        jpenduduk, jkk, laki, perempuan, jkkprese, jkkseja, jkkkaya, jkksedang, 
        jkkmiskin, islam, kristen, protestan, katolik, hindu, budha
    ))
        mysql.connection.commit()
        return redirect(url_for("adminmono"))
    
#anggota
@app.route('/admin/anggota')
def adminanggota():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM anggota order by id")
    anggota = con.fetchall()
    info_list = []
    
    for sistem in anggota:
        list_data = {
            'id': str(sistem[0]),
            'nama_lengkap': str(sistem[1]),
            'gambar': str(sistem[2]),
            'jabatan': str(sistem[3]),
            'niap': str(sistem[4]),
            'ttl': str(sistem[5]),
            'agama': str(sistem[6]),
            'golongan': str(sistem[7]),
            'pendidikan_terakhir': str(sistem[8]),
            'nomorsk': str(sistem[9]),
            'tanggalsk': str(sistem[10]),
            'masa_jabatan': str(sistem[11]),
            'status': str(sistem[12])
        }
        info_list.append(list_data)
        

    return render_template("admin/anggota.html", info_list = info_list)

@app.route('/admin/tambah_anggota', methods=['POST'])
@jwt_required()
def tambah_anggota():
    con = mysql.connection.cursor()
    nama_lengkap = request.form['nama_lengkap']
    try:
        
        if request.files['gambar']:
            file = request.files['gambar']
            print(file)
            img = Image.open(file)
            img = img.convert('RGB')
            # Resize gambar
            width, height = 400, 700 # Atsesuai kebutuhan Anda
            img = img.resize((width, height))
                        

            # Simpan gambar yang diresize BytesIO
            img_io = BytesIO()
            img.save(img_io, 'JPEG', quality=70)
            img_io.seek(0)
            random_name = uuid.uuid4().hex+".jpg"
            print(random_name)
            destination = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
            img.save(destination)  # Ganti dengan lokasi penyimpanan yang diinginkan      
                    # Gunakan img_io atau file yang telah diresize sesuai kebutuhan Anda
        else:
            random_name = "default.jpg"
    except:
        random_name = "default.jpg"
    jabatan = request.form['jabatan']
    niap = request.form['niap']
    ttl = request.form['ttl']
    agama = request.form['agama']
    golongan = request.form['golongan']
    pendidikan_terakhir = request.form['pendidikan_terakhir']
    nomorsk = request.form['nomorsk']
    tanggalsk = request.form['tanggalsk']
    masa_jabatan = request.form['masa_jabatan']
    status = request.form['status']
    
    con.execute("INSERT INTO anggota (nama_lengkap, gambar , jabatan,niap,ttl,agama,golongan,pendidikan_terakhir,nomorsk,tanggalsk,masa_jabatan,status ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(nama_lengkap,random_name,jabatan,niap,ttl,agama,golongan,pendidikan_terakhir,nomorsk,tanggalsk,masa_jabatan,status))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")
##edit_anggota
@app.route('/admin/edit_anggota', methods=['POST'])
@jwt_required()
def edit_anggota():
    con = mysql.connection.cursor()
    id = request.form['id']
    print(id+"\n")
    nama_lengkap = request.form['nama_lengkap']
    jabatan = request.form['jabatan']
    niap = request.form['niap']
    ttl = request.form['ttl']
    agama = request.form['agama']
    golongan = request.form['golongan']
    pendidikan_terakhir = request.form['pendidikan_terakhir']
    nomorsk = request.form['nomorsk']
    tanggalsk = request.form['tanggalsk']
    masa_jabatan = request.form['masa_jabatan']
    status = request.form['status']
    try:
        print("try")
        if request.files['gambar']:
            print("if")
            print(nama_lengkap+"\n"+jabatan+"\n"+niap+"\n"+ttl+"\n"+agama+"\n"+golongan+"\n"+pendidikan_terakhir+"\n"+nomorsk+"\n"+tanggalsk+"\n"+masa_jabatan+"\n"+status)
            file = request.files['gambar']
            con.execute("SELECT gambar FROM anggota WHERE id = %s", (id,))
            result = con.fetchone()
                        
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
            con.execute("UPDATE anggota SET nama_lengkap = %s, gambar = %s, jabatan = %s, niap = %s, ttl = %s, agama = %s, golongan = %s, pendidikan_terakhir = %s, nomorsk = %s, tanggalsk = %s, masa_jabatan = %s, status = %s WHERE id = %s",(nama_lengkap,random_name,jabatan,niap,ttl,agama,golongan,pendidikan_terakhir,nomorsk,tanggalsk,masa_jabatan,status,id))
            mysql.connection.commit()
            # Gunakan img_io atau file yang telah diresize sesuai kebutuhan Anda
    except:
        print("except")
        print(nama_lengkap+"\n"+jabatan+"\n"+niap+"\n"+ttl+"\n"+agama+"\n"+golongan+"\n"+pendidikan_terakhir+"\n"+nomorsk+"\n"+tanggalsk+"\n"+masa_jabatan+"\n"+status)
        con.execute("UPDATE anggota SET nama_lengkap = %s, jabatan = %s, niap = %s, ttl = %s, agama = %s, golongan = %s, pendidikan_terakhir = %s, nomorsk = %s, tanggalsk = %s, masa_jabatan = %s, status = %s WHERE id = %s",
        (nama_lengkap,jabatan,niap,ttl,agama,golongan,pendidikan_terakhir,nomorsk,tanggalsk,masa_jabatan,status,id))
        mysql.connection.commit()
    return jsonify({"msg" : "SUKSES"})

#Galeri
@app.route('/admin/galeri')
def admindgaleri():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM galeri order by id DESC")
    berita = con.fetchall()
    info_list = []
    for sistem in berita:
        list_data = {
            'id': str(sistem[0]),
            'judul': str(sistem[1]),
            'gambar': str(sistem[2]),
            'tanggal': str(sistem[3])
        }
        info_list.append(list_data)
        

    return render_template("admin/galeri.html", info_list = info_list)

@app.route('/admin/tambah_galeri', methods=['POST'])
@jwt_required()
def tambah_galeri():
    con = mysql.connection.cursor()
    judul = request.form['judul']
    tanggal = datetime.now().date()
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
    con.execute("INSERT INTO galeri (judul, gambar , tanggal) VALUES (%s,%s,%s)",(judul,random_name,tanggal))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")

@app.route('/admin/edit_galeri', methods=['POST'])
@jwt_required()
def edit_galeri():
    con = mysql.connection.cursor()
    id = request.form['id']
    judul = request.form['judul']
    try:
        if request.files['gambar']:
            file = request.files['gambar']
            con.execute("SELECT galeri FROM galeri WHERE id = %s", (id,))
            result = con.fetchone()
            if result:
                filename = result[0]
        
            # Delete the image file
                if filename:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        
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
            con.execute("UPDATE galeri SET judul = %s, gambar = %s WHERE id = %s",(judul,random_name,id))
            mysql.connection.commit()
            # Gunakan img_io atau file yang telah diresize sesuai kebutuhan Anda
    except:
        con.execute("UPDATE galeri SET judul = %s WHERE id = %s",(judul,id))
        mysql.connection.commit()
    return jsonify({"msg" : "SUKSES"})

@app.route('/hapus_galeri', methods=['POST'])
@jwt_required()
def hapus_galeri():
    con = mysql.connection.cursor()
    id = request.form['id']
    
    # Get the filename of the image associated with the news article
    con.execute("SELECT gambar FROM galeri WHERE id = %s", (id,))
    result = con.fetchone()
    if result:
        filename = result[0]
        
        # Delete the image file
        if filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(image_path):
                os.remove(image_path)
    
    # Delete the news article from the database
    con.execute("DELETE FROM galeri WHERE id = %s", (id,))
    mysql.connection.commit()
    return jsonify({"msg": "SUKSES"})
#vidio
@app.route('/admin/vidio')
def adminvidio():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM vidio order by id DESC")
    berita = con.fetchall()
    info_list = []
    for sistem in berita:
        list_data = {
            'id': str(sistem[0]),
            'vidio': str(sistem[1])
            
        }
        info_list.append(list_data)
        

    return render_template("admin/vidio.html", info_list = info_list)

@app.route('/admin/edit_vidio', methods=['POST'])
@jwt_required()
def edit_vidio():
    con = mysql.connection.cursor()
    id = request.form['id']
    vidio = request.form['vidio']
    con.execute("UPDATE vidio SET vidio = %s WHERE id = %s",(vidio,id))
    mysql.connection.commit()
    return jsonify({"msg" : "SUKSES"})