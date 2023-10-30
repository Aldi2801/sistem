from . import app,mysql
from flask import render_template, request, jsonify
import os

#get
@app.route('/dana', methods=['GET'])
def get_dana():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM dana")
    surat = con.fetchall()
    info_list = []
    for sistem in surat:
        list_data = {
            'id': str(sistem[0]),
            'tahun': str(sistem[1]),
            'dana': str(sistem[2]),
            'digunakan': str(sistem[3]),
            'sisah': str(sistem[4])
        }
        info_list.append(list_data)
    return jsonify(info_list)

#input


@app.route('/admin/edit_dana', methods=['POST'])
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
def hapus_dana():
    con = mysql.connection.cursor()
    id = request.form['id']
    con.execute("DELETE FROM dana WHERE id = %s",(id))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")
