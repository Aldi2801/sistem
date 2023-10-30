from . import app,mysql
from flask import render_template, request, jsonify
import os
from flask_jwt_extended import jwt_required, get_jwt_identity


#get info
@app.route('/info', methods=['GET'])
def get_info():
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
            'misi': str(sistem[3])
        }
        info_list.append(list_data)
    return jsonify(info_list)

#tambah info

@app.route('/tambah_info', methods=['POST'], endpoint='tambah_info_endpoint')
# @jwt_required
def tambah_info():
    con = mysql.connection.cursor()
    sejarah = request.form['sejarah']
    visi = request.form['visi']
    misi = request.form['misi']
    con.execute("INSERT INTO sejarah (sejarah , visi, misi) VALUES (%s,%s,%s)",(sejarah , visi, misi))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")


#edit info data
@app.route('/edit_info', methods=['POST'], endpoint='edit_info_endpoint')
# @jwt_required
def edit_info():
    current_user_id = get_jwt_identity()
    con = mysql.connection.cursor()
    id = request.form['id']
    sejarah = request.form['sejarah']
    visi = request.form['visi']
    
    misi = request.form['misi']
    con.execute("UPDATE sejarah_desa SET sejarah = %s, visi = %s, misi = %s WHERE id = %s",(sejarah,visi,misi,id))
    mysql.connection.commit()
    return jsonify("msg : SUKSES")

#get fasilitas
@app.route('/fasilitas', methods=['GET'])
def get_fasilitas():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM fasilitas")
    sejarah = con.fetchall()
    info_list = []
    for sistem in sejarah:
        list_data = {
            'id': str(sistem[0]),
            'fasilitas': str(sistem[1]),
            'kondisi': str(sistem[2])
        }
        info_list.append(list_data)
    return jsonify(info_list)


