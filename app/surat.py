from . import app,mysql
from flask import render_template, request, jsonify
import os

#get
@app.route('/surat', methods=['GET'])
def get_surat():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM surat")
    surat = con.fetchall()
    info_list = []
    for sistem in surat:
        list_data = {
            'id': str(sistem[0]),
            'nama': str(sistem[1]),
            'hp': str(sistem[2]),
            'keterangan': str(sistem[3])
        }
        info_list.append(list_data)
    return jsonify(info_list)

@app.route('/tambah_surat', methods=['POST'])
def tambah_surat():
    con = mysql.connection.cursor()
    nama = request.form['nama']
    hp = request.form['hp']
    keterangan = request.form['keterangan']
    con.execute("INSERT INTO surat (nama , hp, keterangan) VALUES (%s,%s,%s)",(nama,hp,keterangan))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")

@app.route('/edit_surat', methods=['POST'])
def edit_surat():
    con = mysql.connection.cursor()
    id = request.form['id']
    nama = request.form['nama']
    hp = request.form['hp']
    keterangan = request.form['keterangan']
    con.execute("UPDATE surat SET nama = %s, hp = %s, keterangan = %s WHERE id = %s",(nama,hp,keterangan,id))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")

@app.route('/hapus_surat', methods=['POST'])
def hapus_surat():
    con = mysql.connection.cursor()
    id = request.form['id']
    con.execute("DELETE FROM surat WHERE id = %s",(id))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")