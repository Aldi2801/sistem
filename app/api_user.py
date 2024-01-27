from . import app,mysql,db
from flask import render_template, request, jsonify, redirect, url_for,session
import pandas as pd
from PIL import Image
from io import BytesIO
import os,textwrap, locale, json, uuid, time
from datetime import datetime

def fetch_data_and_format(query):
    con = mysql.connection.cursor()
    con.execute(query)
    data = con.fetchall()
    column_names = [desc[0] for desc in con.description]
    info_list = [dict(zip(column_names, row)) for row in data]
    return info_list
#halaman homepage
@app.route('/')
def homepahe():
    thn_dana_list =fetch_data_and_format("SELECT tahun FROM realisasi_pendapatan group by tahun")
    session['list_thn_dana']= thn_dana_list 
    return render_template('index.html')

@app.route('/news')
def userberita():
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
            'tanggal': str(sistem[4]),
            'link': str(sistem[5]),
        }
        info_list.append(list_data)
  
    return render_template('homepage.html',info_list = info_list)
#halaman berita
@app.route('/berita/<link>')
def detail_berita(link):
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM berita where link = %s order by id DESC " , (link,))
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
    return render_template('detail_berita.html',info_list = info_list)
#halaman sejarah
@app.route('/sejarah')
def sejarah():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM sejarah_desa")
    sejarah = con.fetchall()
    info_list = []
    for sistem in sejarah:
        list_data = {
            'id': str(sistem[0]),
            'sejarah': str(sistem[1])
        }
        info_list.append(list_data)
    return render_template("sejarah.html", info_list = info_list)

#halaman visi misi
@app.route('/visi_misi')
def visi_misi():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM sejarah_desa")
    sejarah = con.fetchall()
    info_list = []
    for sistem in sejarah:
        list_data = {
            'id': str(sistem[0]),
            'visi': str(sistem[2]),
            'misi': sistem[3],
        }
        info_list.append(list_data)
    return render_template("visimisi.html", info_list = info_list)

#halaman pemerintahan
@app.route('/pemerintahan_desa')
def pemerintahan_desa():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM anggota order by id")
    anggota = con.fetchall()
    column_names = [desc[0] for desc in con.description]
    info_list = [dict(zip(column_names, row)) for row in anggota]
    return render_template("pemerintahan_desa.html", info_list = info_list)
#halaman dana
@app.route('/dana/<thn>')
def dana_desa(thn):
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM realisasi_pendapatan where tahun = %s order by id",(thn,))
    dana = con.fetchall()
    column_names = [desc[0] for desc in con.description]
    info_list = [dict(zip(column_names, row)) for row in dana]
    con.execute("SELECT * FROM realisasi_belanja where tahun = %s order by id",(thn,))
    dana = con.fetchall()
    column_names = [desc[0] for desc in con.description]
    info_list2 = [dict(zip(column_names, row)) for row in dana]
    con.execute("SELECT * FROM realisasi_pembiayaan where tahun = %s order by id",(thn,))
    dana = con.fetchall()
    column_names = [desc[0] for desc in con.description]
    info_list3 = [dict(zip(column_names, row)) for row in dana]
    return render_template("dana.html", info_list = info_list,info_list2 = info_list2,info_list3 = info_list3, tahun = thn)
#halaman user galeri
@app.route('/galeri')
def galeri():
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
    return render_template("/galeri.html", info_list = info_list)
#halaman monografi
@app.route('/monografi')
def mono():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM monografi")
    mono = con.fetchall()
    column_names = [desc[0] for desc in con.description]
    info_list = [dict(zip(column_names, row)) for row in mono]
    return render_template("user_data_desa/monografi.html", info_list = info_list)
#Halaman geografi
@app.route('/geografi')
def geo():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM wilayah")
    wilayah = con.fetchall()
    column_names = [desc[0] for desc in con.description]
    info_list = [dict(zip(column_names, row)) for row in wilayah]
    return render_template("user_data_desa/geografi.html", info_list=info_list )
#halaman vidio
@app.route('/video')
def vidio():
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
    return render_template("video.html", info_list = info_list)

#get info
@app.route('/info', methods=['GET'])
def get_info():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM sejarah_desa")
    sejarah = con.fetchall()
    info_list = []
    for sistem in sejarah:
        list_data = {
            'id': str(sistem[0]),
            'sejarah': str(sistem[1]),
            'visi': str(sistem[2]),
            'misi': str(sistem[3])
        }
        info_list.append(list_data)
    return jsonify(info_list)



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
