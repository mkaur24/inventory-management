from __future__ import print_function # In python 2.7
import sys
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

def get_prodid(prod_name):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM products WHERE prod_name = ?',
                        (prod_name,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/')
def index():
    conn = get_db_connection()
    report = conn.execute('SELECT * FROM report').fetchall()
    conn.close()
    return render_template('index.html', report=report)

@app.route('/products', methods=('GET', 'POST'))
def products():
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM product').fetchall()
    conn.close()
    if request.method == 'POST':
        prod_name = request.form['prod_name']
        qty = request.form['qty']

        if not prod_name:
            flash('Name is required!')
        elif not qty:
            flash("Quantity is required")
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO product (prod_name,qty) VALUES (?, ?)', (prod_name,qty))
            conn.commit()
            conn.close()
            return redirect(url_for('products'))
    return render_template('products.html', product=product)

@app.route('/locationn', methods=('GET', 'POST'))
def locationn():
    conn = get_db_connection()
    locationn = conn.execute('SELECT * FROM locationn').fetchall()
    conn.close()
    if request.method == 'POST':
        location_name = request.form['location_name']

        if not location_name:
            flash('Name is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO locationn (location_name) VALUES (?)', (location_name,))
            conn.commit()
            conn.close()
            return redirect(url_for('locationn'))
    return render_template('locationn.html', locationn=locationn)

@app.route('/transfers', methods=('GET', 'POST'))
def transfers():
    conn = get_db_connection()
    m = conn.execute('SELECT * FROM movement').fetchall()
    p = conn.execute('SELECT * FROM product').fetchall()
    l = conn.execute('SELECT location_name FROM locationn').fetchall()
    conn.close()
    if request.method == 'POST':
        prod_name = request.form['prod_name']
        from_l = request.form['from_l']
        to_l = request.form['to_l']
        qty = request.form['qty']

        if not prod_name:
            flash('Name is required!')
        elif not qty:
            flash("Quantity is required")
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO movement (prod_name,qty,from_l,to_l) VALUES (?,?,?,?)', (prod_name,qty,from_l,to_l))
            b=conn.execute('SELECT * from report WHERE p=? and wh=?',(prod_name,to_l))
            if b[0]:
                conn.execute('INSERT INTO report VALUES (?,?,?)',(prod_name,to_l,qty))
            else:
                conn.execute('UPDATE report SET qty= qty+? WHERE p =? AND wh=?',(qty,prod_name,to_l))

            conn.commit()
            conn.close()
            return redirect(url_for('transfers'))
    return render_template('transfers.html', m=m, p=p,l=l)

