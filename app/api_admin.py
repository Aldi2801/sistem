from . import app,mysql,db
from flask import render_template, request, jsonify, redirect, url_for,session
import os,textwrap, locale, json, uuid, time
import pandas as pd
from PIL import Image
from io import BytesIO
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

def do_image(do, table, id):
    try:
        if do == "tambah":
            file = request.files['gambar']
            if file:
                return resize_and_save_image(file)
            else:
                return  jsonify({"status": True,"msg":"default.jpg"})
        elif do == "delete":
            filename = get_image_filename(table, id)
            delete_image(filename)
            return True
        elif do == "edit":
            file = request.files['gambar']
            filename = get_image_filename(table, id)
            delete_image(filename)
            return resize_and_save_image(file, table, id)
    except Exception as e:
        print(str(e))
        return str(e)

def resize_and_save_image(file, table=None, id=None):
    img = Image.open(file).convert('RGB').resize((600, 300))
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    random_name = uuid.uuid4().hex + ".jpg"
    destination = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
    img.save(destination)
    if table and id:
        con = mysql.connection.cursor()
        con.execute(f"UPDATE {table} SET gambar = %s WHERE id = %s", (random_name, id))
        mysql.connection.commit()
        return True
    else:
        return random_name
   
def get_image_filename(table, id):
    con = mysql.connection.cursor()
    con.execute(f"SELECT gambar FROM {table} WHERE id = %s", (id,))
    result = con.fetchone()
    return result[0] if result else None

def delete_image(filename):
    if filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(image_path):
            os.remove(image_path)

def fetch_data_and_format(query):
    con = mysql.connection.cursor()
    con.execute(query)
    data = con.fetchall()
    column_names = [desc[0] for desc in con.description]
    info_list = [dict(zip(column_names, row)) for row in data]
    return info_list

def fetch_years(query):
    con = mysql.connection.cursor()
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
    info_list = fetch_data_and_format("SELECT * FROM sejarah_desa")
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
        info=fetch_data_and_format("SELECT * FROM sejarah_desa WHERE id = 1")
        return render_template("admin/editsejarah.html",info=info)
    
#visimisi
@app.route('/admin/visimisi')
def adminvisimisi():
    info_list = fetch_data_and_format("SELECT * FROM sejarah_desa")
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
    info_list=fetch_data_and_format("SELECT * FROM berita order by id DESC")
    return render_template("admin/berita.html", info_list = info_list)

@app.route('/admin/tambah_berita', methods=['POST'])
@jwt_required()
def tambah_berita():
    con = mysql.connection.cursor()
    judul = request.form['judul']
    link = '_'.join(filter(None, [judul.replace("#", "").replace("?", "").replace("/", "").replace(" ", "_")]))
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
        status = do_image("edit","berita",id)
        if status == True:
            con.execute("UPDATE berita SET judul = %s, deskripsi = %s WHERE id = %s",(judul,deskripsi,id))
            mysql.connection.commit()
            return jsonify({"msg" : "SUKSES"})
        else:
            return jsonify({"msg":status})
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
        status = do_image("delete","anggota",id)
        print(status)
        if status == True:
            con.execute("DELETE FROM anggota WHERE id = %s", (id,))
            mysql.connection.commit()
            return jsonify({"msg": "SUKSES"})
        else:
            return jsonify({"msg": status})
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
    info_list=fetch_data_and_format("SELECT * FROM tanah")
    info_list2=fetch_data_and_format("SELECT * FROM wilayah")
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
    info_list=fetch_data_and_format("SELECT * FROM monografi")
    return render_template("admin/monografi.html", info_list = info_list)

@app.route('/admin/monoedit', methods=['POST'])
@jwt_required()
def adminmonoedit():
    con = mysql.connection.cursor()
    form_data = request.form
    fields = ['jpenduduk', 'jkk', 'laki', 'perempuan', 'jkkprese', 'jkkseja', 'jkkkaya', 'jkksedang', 'jkkmiskin', 'islam', 'kristen', 'protestan', 'katolik', 'hindu', 'budha']
    query = f"UPDATE monografi SET {' = %s, '.join(fields)} = %s WHERE id = 1"
    con.execute(query, tuple(form_data[field] for field in fields))
    mysql.connection.commit()
    return redirect(url_for("adminmono"))
    
#anggota
@app.route('/admin/anggota')
def adminanggota():
    info_list=fetch_data_and_format("SELECT * FROM anggota order by id")
    return render_template("admin/anggota.html", info_list = info_list)

@app.route('/admin/tambah_anggota', methods=['POST'])
@jwt_required()
def tambah_anggota():
    con = mysql.connection.cursor()
    form_data = request.form
    fields = ['nama_lengkap', 'jabatan', 'niap', 'ttl', 'agama', 'golongan', 'pendidikan_terakhir', 'nomorsk', 'tanggalsk', 'masa_jabatan', 'status']
    try:
        random_name = do_image("tambah","anggota","")
        query = f"INSERT INTO anggota ({', '.join(fields + ['gambar'])}) VALUES ({', '.join(['%s'] * (len(fields) + 1))})"
        con.execute(query, tuple(form_data[field] for field in fields) + (random_name,))
        mysql.connection.commit()
        return jsonify({"msg" : "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})
##edit_anggota
@app.route('/admin/edit_anggota', methods=['POST'])
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
        print(do_image("edit","anggota",id))
        con.execute("UPDATE anggota SET nama_lengkap = %s, jabatan = %s, niap = %s, ttl = %s, agama = %s, golongan = %s, pendidikan_terakhir = %s, nomorsk = %s, tanggalsk = %s, masa_jabatan = %s, status = %s WHERE id = %s",
        (nama_lengkap,jabatan,niap,ttl,agama,golongan,pendidikan_terakhir,nomorsk,tanggalsk,masa_jabatan,status,id))
        mysql.connection.commit()
        return jsonify({"msg" : "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})

#Galeri
@app.route('/admin/galeri')
def admindgaleri():
    info_list=fetch_data_and_format("SELECT * FROM galeri order by id DESC")
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
    info_list=fetch_data_and_format("SELECT * FROM vidio order by id DESC")
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
    list_agenda=fetch_data_and_format("SELECT * FROM agenda")
    return render_template('admin/agenda.html',list_agenda=list_agenda)
@app.route('/delete-agenda/<id>',methods=["DELETE"])
@jwt_required()
def agenda_delete(id):
    con = mysql.connection.cursor()
    con.execute("DELETE FROM agenda WHERE id = %s", (id,))
    mysql.connection.commit()
    return jsonify({"msg" : "SUKSES"})
@app.route('/tambah-agenda',methods=["POST"])
@jwt_required()
def agenda_tambah():
    con = mysql.connection.cursor()
    id = request.form['id']
    judul = request.form['judul']
    try:
        do_image("tambah","agenda","")
        con.execute("INSERT INTO agenda SET judul = %s WHERE id = %s",(judul,id))
        mysql.connection.commit()
        return jsonify({"msg" : "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/edit-agenda',methods=["PUT"])
@jwt_required()
def agenda_edit():
    con = mysql.connection.cursor()
    id = request.form['id']
    title = request.form['title']
    jam_mulai = request.form['jam_mulai']
    jam_selesai = request.form['jam_selesai']
    pemimpin_kegiatan = request.form['pemimpin_kegiatan']
    keterangan = request.form['keterangan']
    try:
        do_image("edit","agenda",id)
        con.execute("UPDATE agenda SET title = %s, start = %s, end = %s, pemimpin_kegiatan = %s, keterangan = %s WHERE id = %s",(title,jam_mulai,jam_selesai,pemimpin_kegiatan,keterangan,id))
        mysql.connection.commit()
        return jsonify({"msg" : "SUKSES"})
    except Exception as e:
        return jsonify({"error": str(e)})