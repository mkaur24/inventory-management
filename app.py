from __future__ import print_function # In python 2.7
import sys
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd,sjsfhugsbdchvh'

@app.route('/')
def index():
    conn = get_db_connection()
    report = conn.execute('SELECT * FROM report').fetchall()
    conn.close()
    return render_template('index.html', report=report)

@app.route('<p>/r', methods=("GET"))
def r(p,s):
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
        if 'location_id' in request.form:
            location_name = request.form['location_name']
            location_id = request.form['location_id']
            if not location_name:
                flash('Name is required!')
            else:
                conn = get_db_connection()
                conn.execute('UPDATE locationn SET location_name= ? WHERE location_id=?',(location_name,location_id))
                conn.execute('UPDATE report SET location_name= ? WHERE location_name=?',(location_name,location_id))
                conn.commit()
                conn.close()
                return redirect(url_for('locationn'))
        else:
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
    r = conn.execute('SELECT * FROM report').fetchall()
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
                    s=conn.execute('SELECT qty FROM product WHERE prod_name = ?',(prod_name,)).fetchone()
                    conn = get_db_connection()
                    if s['qty']<int(qty):
                        flash('Quantity cannot be moved. Not available!')    
                    else:
                        if from_l=='NULL':
                            conn = get_db_connection()
                            res=conn.execute('SELECT * from report WHERE p=?',(prod_name,))
                            f=0
                            for i in res:
                                f=1
                            if f==1:
                                sa=conn.execute('SELECT SUM(qty) as sum FROM report WHERE p = ?',(prod_name,)).fetchone()
                                s=conn.execute('SELECT qty FROM product WHERE prod_name = ?',(prod_name,)).fetchone()
                                print(s['qty'])
                                print(sa['sum'])
                                o=s['qty']-sa['sum']
                                print(o)
                                conn = get_db_connection()
                                if o<int(qty):
                                    flash('Quantity cannot be moved. Not available!') 
                                else:
                                    conn.execute('INSERT INTO movement (prod_name,qty,from_l,to_l) VALUES (?,?,?,?)', (prod_name,qty,from_l,to_l))
                                    res=conn.execute('SELECT * from report WHERE p=? and wh=?',(prod_name,to_l))
                                    f=0
                                    for i in res:
                                        f=1
                                    if f==0:
                                        conn.execute('INSERT INTO report VALUES (?,?,?)',(prod_name,to_l,qty))
                                    else:
                                        conn.execute('UPDATE report SET qty= qty+? WHERE p =? AND wh=?',(qty,prod_name,to_l))
                                    conn.commit()
                                    conn.close()
                            else:
                                conn = get_db_connection()
                                s=conn.execute('SELECT qty FROM product WHERE prod_name = ?',(prod_name,)).fetchone()
                                print(s['qty'])
                                conn = get_db_connection()
                                if s['qty']<int(qty):
                                    flash('Quantity cannot be moved. Not available!') 
                                else:
                                    conn.execute('INSERT INTO movement (prod_name,qty,from_l,to_l) VALUES (?,?,?,?)', (prod_name,qty,from_l,to_l))
                                    res=conn.execute('SELECT * from report WHERE p=? and wh=?',(prod_name,to_l))
                                    f=0
                                    for i in res:
                                        f=1
                                    if f==0:
                                        conn.execute('INSERT INTO report VALUES (?,?,?)',(prod_name,to_l,qty))
                                    else:
                                        conn.execute('UPDATE report SET qty= qty+? WHERE p =? AND wh=?',(qty,prod_name,to_l))
                                    conn.commit()
                                    conn.close()
                        elif to_l=='NULL':
                            conn = get_db_connection()
                            res=conn.execute('SELECT * from report WHERE p=? AND wh=?',(prod_name,from_l))
                            f=0
                            for i in res:
                                f=1
                            if f==1:
                                s=conn.execute('SELECT qty FROM report WHERE p = ? AND wh=?',(prod_name,from_l)).fetchone()
                                if s['qty']<int(qty):
                                    flash('Quantity cannot be moved. Not available at the source location!')
                                else:
                                    conn.execute('INSERT INTO movement (prod_name,qty,from_l,to_l) VALUES (?,?,?,?)', (prod_name,qty,from_l,to_l))
                                    res=conn.execute('SELECT * from report WHERE p=? and wh=?',(prod_name,from_l))
                                    conn.execute('UPDATE report SET qty= qty-? WHERE p =? AND wh=?',(qty,prod_name,from_l))
                                    conn.execute('UPDATE product SET qty= qty-? WHERE prod_name =?',(qty,prod_name))
                            else:
                                flash('Quantity cannot be moved. Not available at the source location!')
                            conn.commit()
                            conn.close()
                        else:
                            conn = get_db_connection()
                            res=conn.execute('SELECT * from report WHERE p=? AND wh=?',(prod_name,from_l))
                            f=0
                            for i in res:
                                f=1
                            if f==1:
                                s=conn.execute('SELECT qty FROM report WHERE p = ? AND wh=?',(prod_name,from_l)).fetchone()
                                if s['qty']<int(qty):
                                    flash('Quantity cannot be moved. Not available at the source location!')
                                else:
                                    conn.execute('INSERT INTO movement (prod_name,qty,from_l,to_l) VALUES (?,?,?,?)', (prod_name,qty,from_l,to_l))
                                    res=conn.execute('SELECT * from report WHERE p=? and wh=?',(prod_name,to_l))
                                    f=0
                                    for i in res:
                                        f=1
                                    if f==0:
                                        conn.execute('INSERT INTO report VALUES (?,?,?)',(prod_name,to_l,qty))
                                        conn.execute('UPDATE report SET qty= qty-? WHERE p =? AND wh=?',(qty,prod_name,from_l))
                                    else:
                                        conn.execute('UPDATE report SET qty= qty+? WHERE p =? AND wh=?',(qty,prod_name,to_l))
                                        conn.execute('UPDATE report SET qty= qty-? WHERE p =? AND wh=?',(qty,prod_name,from_l))
                                conn.commit()
                                conn.close()
                            else:
                                flash('Quantity cannot be moved. Not available at the source location!')
                    return redirect(url_for('transfers'))
    return render_template('transfers.html', m=m, p=p,l=l, r=r)

@app.route('/<lid>/edit', methods=('GET', 'POST'))
def edit(lid):
    conn = get_db_connection()
    l = conn.execute('SELECT * FROM locationn WHERE location_name = ?',(lid,)).fetchone()
    conn.close()
    if request.method == 'POST':
            location_name = request.form['location_name']
            if not location_name:
                flash('Name is required!')
            else:
                conn = get_db_connection()
                conn.execute('UPDATE locationn SET location_name= ? WHERE location_name=?',(location_name,l['location_name']))
                conn.execute('UPDATE movement SET to_l= ? WHERE to_l=?',(location_name,l['location_name']))
                conn.execute('UPDATE movement SET from_l= ? WHERE from_l=?',(location_name,l['location_name']))
                conn.execute('UPDATE report SET wh= ? WHERE wh=?',(location_name,l['location_name']))
                conn.commit()
                conn.close()
                return redirect(url_for('locationn'))
    return render_template('edit.html', l=l)

@app.route('/<pid>/pedit', methods=('GET', 'POST'))
def pedit(pid):
    conn = get_db_connection()
    p = conn.execute('SELECT * FROM product WHERE prod_name = ?',(pid,)).fetchone()
    conn.close()
    if request.method == 'POST':
            prod_name = request.form['prod_name']
            qty=request.form['qty']
            conn = get_db_connection()
            if not prod_name:
                flash('Name is required!')
            elif not qty:
                flash('Quantity is required!')
            else:
                res=conn.execute('SELECT * from report WHERE p=?',(prod_name,))
                f=0
                for i in res:
                    f=1
                if f==1:
                    s=conn.execute('SELECT SUM(qty) as sum FROM report WHERE p = ?',(pid,))
                    for i in s:
                        if int(i['sum'])>int(qty):
                            flash('Quantity cannot be decreased. It is less than the quantity already alloted to loctions')
                            return redirect(url_for('products'))
                        else:
                            conn.execute('UPDATE product SET prod_name= ?, qty=? WHERE prod_name=?',(prod_name,qty,p['prod_name']))
                            conn.execute('UPDATE movement SET prod_name= ? WHERE prod_name=?',(prod_name,p['prod_name']))
                            conn.execute('UPDATE report SET p= ? WHERE p=?',(prod_name,p['prod_name']))
                            conn.commit()
                            conn.close()
                            return redirect(url_for('products'))
                else:
                    print('here')
                    conn.execute('UPDATE product SET prod_name= ?, qty=? WHERE prod_name=?',(prod_name,qty,p['prod_name']))
                    conn.execute('UPDATE movement SET prod_name= ? WHERE prod_name=?',(prod_name,p['prod_name']))
                    conn.execute('UPDATE report SET p= ? WHERE p=?',(prod_name,p['prod_name']))
                    conn.commit()
                    conn.close()
            return redirect(url_for('products'))
    return render_template('pedit.html', p=p)

