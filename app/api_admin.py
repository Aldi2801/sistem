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

def do_image(do, table, id):
    try:
        if do == "tambah":
            file = request.files['gambar']
            if file:
                return resize_and_save_image(file)
            else:
                return "default.jpg"

        elif do == "delete":
            filename = get_image_filename(table, id)
            delete_image(filename)
            return True

        elif do == "edit":
            file = request.files['gambar']
            filename = get_image_filename(table, id)
            delete_image(filename)
            return resize_and_save_image(file, table, id)

    except:
        return False

def resize_and_save_image(file, table=None, id=None):
    img = Image.open(file)
    img = img.convert('RGB')
    width, height = 600, 300
    img = img.resize((width, height))

    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)

    random_name = uuid.uuid4().hex + ".jpg"
    destination = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
    img.save(destination)

    if table and id:
        con.execute(f"UPDATE {table} SET gambar = %s WHERE id = %s", (random_name, id))
        mysql.connection.commit()
        return True
    else:
        return random_name

def get_image_filename(table, id):
    con.execute(f"SELECT gambar FROM {table} WHERE id = %s", (id,))
    result = con.fetchone()
    return result[0] if result else None

def delete_image(filename):
    if filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(image_path):
            os.remove(image_path)

def fetch_data_and_format(query):
    con.execute(query)
    dana = con.fetchall()
    info_list = []

    for sistem in dana:
        list_data = {
            'id': str(sistem[0]),
            'no': str(sistem[1]),
            'uraian': str(sistem[2]),
            'anggaran': format_currency(int(sistem[3])),
            'realisasi': format_currency(int(sistem[4])),
            'lebih_kurang': format_currency(int(sistem[5])),
            'tahun': str(sistem[6])
        }
        info_list.append(list_data)
    return info_list
def fetch_years(query):
    con.execute(query)
    data_thn = con.fetchall()
    thn = [{'tahun': str(sistem[6])} for sistem in data_thn]
    return thn

def insert_data_from_dataframe(df, table):
    con = mysql.connection.cursor()
    for index, row in df.iterrows():
        sql = f"INSERT INTO {table} (no, uraian, anggaran, realisasi, `lebih/(kurang)`, tahun) VALUES (%s, %s, %s, %s, %s, %s)"
        con.execute(sql, (row[0], row[1], row[2], row[3], row[4], row[5]))
    mysql.connection.commit()

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
    info_list = []
    for sistem in sejarah:
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
    link = '_'.join(filter(None, [judul.replace("#", "").replace("?", "").replace("/", "").replace(" ", "_")]))
    file = request.files['gambar']
    deskripsi = request.form['deskripsi']
    try: 
        random_name = do_image("tambah","berita","")
        con.execute("INSERT INTO berita (judul, gambar , deskripsi,link ) VALUES (%s,%s,%s,%s)",(judul,random_name,deskripsi,link))
        mysql.connection.commit()
        return jsonify("msg : SUKSES")
    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/admin/edit_berita', methods=['POST'])
@jwt_required()
def edit_berita():
    con = mysql.connection.cursor()
    id = request.form['id']
    judul = request.form['judul']
    deskripsi = request.form['deskripsi']
    try:
        do_image("edit","berita",id)
        con.execute("UPDATE berita SET judul = %s, deskripsi = %s WHERE id = %s",(judul,deskripsi,id))
        mysql.connection.commit()
        return jsonify({"msg" : "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/hapus_berita', methods=['POST'])
@jwt_required()
def hapus_berita():
    con = mysql.connection.cursor()
    id = request.form['id']
    try:
        do_image("delete","berita",id)
        con.execute("DELETE FROM berita WHERE id = %s", (id,))
        mysql.connection.commit()
        return jsonify({"msg": "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})

#hapus anggota
@app.route('/hapus_anggota', methods=['POST'])
@jwt_required()
def hapus_anggota():
    con = mysql.connection.cursor()
    id = request.form['id']
    try:
        do_image("delete","anggota",id)
        con.execute("DELETE FROM anggota WHERE id = %s", (id,))
        mysql.connection.commit()
        return jsonify({"msg": "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})
#Dana
@app.template_filter('format_currency')
def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    return locale.currency(value, grouping=True, symbol='')

@app.route('/admin/dana')
def admindana():
    info_list = fetch_data_and_format("SELECT * FROM realisasi_pendapatan ORDER BY id")
    info_list2 = fetch_data_and_format("SELECT * FROM realisasi_belanja ORDER BY id")
    info_list3 = fetch_data_and_format("SELECT * FROM realisasi_pembiayaan ORDER BY id")
    thn = fetch_years("SELECT * FROM realisasi_pendapatan GROUP BY tahun")

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
    filependapatan = request.files['excellpendapatan']
    filebelanja = request.files['excellbelanja']
    filepembiayaan = request.files['excellpembiayaan']
    if filependapatan:
        df_pendapatan = pd.read_excel(filependapatan)
        insert_data_from_dataframe(df_pendapatan, "realisasi_pendapatan")

    if filebelanja:
        df_belanja = pd.read_excel(filebelanja)
        insert_data_from_dataframe(df_belanja, "realisasi_belanja")

    if filepembiayaan:
        df_pembiayaan = pd.read_csv(filepembiayaan, delimiter=';')
        insert_data_from_dataframe(df_pembiayaan, "realisasi_pembiayaan")
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
        random_name = do_image("tambah","anggota","")
        con.execute("INSERT INTO anggota (nama_lengkap, gambar , jabatan,niap,ttl,agama,golongan,pendidikan_terakhir,nomorsk,tanggalsk,masa_jabatan,status ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(nama_lengkap,random_name,jabatan,niap,ttl,agama,golongan,pendidikan_terakhir,nomorsk,tanggalsk,masa_jabatan,status))
        mysql.connection.commit()
        return jsonify("msg : SUKSES")
    except Exception as e:
        return jsonify({"error": str(e)})
##edit_anggota
@app.route('/admin/edit_anggota', methods=['POST'])
@jwt_required()
def edit_anggota():
    con = mysql.connection.cursor()
    id = request.form['id']
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
        do_image("edit","anggota",id)
        con.execute("UPDATE anggota SET nama_lengkap = %s, jabatan = %s, niap = %s, ttl = %s, agama = %s, golongan = %s, pendidikan_terakhir = %s, nomorsk = %s, tanggalsk = %s, masa_jabatan = %s, status = %s WHERE id = %s",
        (nama_lengkap,jabatan,niap,ttl,agama,golongan,pendidikan_terakhir,nomorsk,tanggalsk,masa_jabatan,status,id))
        mysql.connection.commit()
        return jsonify({"msg" : "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})

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
    try:
        random_name = do_image("tambah","galeri","")
        con.execute("INSERT INTO galeri (judul, gambar , tanggal) VALUES (%s,%s,%s)",(judul,random_name,tanggal))
        mysql.connection.commit()
        return jsonify("msg : SUKSES")
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/admin/edit_galeri', methods=['POST'])
@jwt_required()
def edit_galeri():
    con = mysql.connection.cursor()
    id = request.form['id']
    judul = request.form['judul']
    try:
        do_image("edit","galeri",id)
        con.execute("UPDATE galeri SET judul = %s WHERE id = %s",(judul,id))
        mysql.connection.commit()
        return jsonify({"msg" : "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/hapus_galeri', methods=['POST'])
@jwt_required()
def hapus_galeri():
    con = mysql.connection.cursor()
    id = request.form['id']
    try:
        do_image("delete","galeri",id)
        con.execute("DELETE FROM galeri WHERE id = %s", (id,))
        mysql.connection.commit()
        return jsonify({"msg": "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})
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

# admin agenda 
@app.route('/admin/agenda')
def admin_agenda():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM agenda")
    result = con.fetchall()
    list_agenda = []
    for item in result:
        agenda = {
            "id": str(item[0]),
            "start": str(item[1]),
            "title":str(item[2]),
            "keterangan":str(item[3]),
            "foto":str(item[4]),
            "end":str(item[5]),
            "kategori":str(item[6]),
            "pemimpin_kegiatan":str(item[7])
        }
        list_agenda.append(agenda)
    return render_template('admin/agenda.html',list_agenda=list_agenda)
@app.route('/delete-agenda')
def agenda_delete():
    return jsonify({"msg" : "SUKSES"})
@app.route('/tambah-agenda')
def agenda_tambah():
    return jsonify({"msg" : "SUKSES"})
@app.route('/edit-agenda')
def agenda_edit():
    return jsonify({"msg" : "SUKSES"})