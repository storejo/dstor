from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)

app.secret_key = 'dstore2011'

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# إنشاء قاعدة البيانات

def init_db():

    conn = sqlite3.connect('store.db')

    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price TEXT,
        image TEXT,
        category TEXT,
        old_price TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        price TEXT,
        customer TEXT,
        address TEXT,
        payment TEXT,
        status TEXT
    )
    ''')

    conn.commit()

    conn.close()

init_db()

# الصفحة الرئيسية

@app.route('/')
def home():

    conn = sqlite3.connect('store.db')

    c = conn.cursor()

    c.execute('SELECT * FROM products ORDER BY id DESC')

    products = c.fetchall()

    conn.close()

    return render_template('index.html', products=products)

# إنشاء حساب

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        conn = sqlite3.connect('store.db')

        c = conn.cursor()

        c.execute(
            'INSERT INTO users (email,password) VALUES (?,?)',
            (email,password)
        )

        conn.commit()

        conn.close()

        return redirect('/login')

    return render_template('register.html')

# تسجيل الدخول

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        conn = sqlite3.connect('store.db')

        c = conn.cursor()

        c.execute(
            'SELECT * FROM users WHERE email=? AND password=?',
            (email,password)
        )

        user = c.fetchone()

        conn.close()

        if user:

            session['user'] = email

            return redirect('/')

    return render_template('login.html')

# الأدمن

@app.route('/admin-login', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        password = request.form['password']

        if password == 'dstore2011':

            session['admin'] = True

            return redirect('/admin')

    return render_template('admin_login.html')

@app.route('/admin')
def admin():

    if 'admin' not in session:
        return redirect('/admin-login')

    conn = sqlite3.connect('store.db')

    c = conn.cursor()

    c.execute('SELECT * FROM products ORDER BY id DESC')

    products = c.fetchall()

    conn.close()

    return render_template('admin.html', products=products)

# إضافة منتج

@app.route('/add-product', methods=['POST'])
def add_product():

    if 'admin' not in session:
        return redirect('/admin-login')

    name = request.form['name']

    price = request.form['price']

    old_price = request.form['old_price']

    category = request.form['category']

    image = request.files['image']

    filename = secure_filename(image.filename)

    image_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
    )

    image.save(image_path)

    db_path = 'uploads/' + filename

    conn = sqlite3.connect('store.db')

    c = conn.cursor()

    c.execute(
        '''
        INSERT INTO products
        (name,price,image,category,old_price)
        VALUES (?,?,?,?,?)
        ''',
        (name,price,db_path,category,old_price)
    )

    conn.commit()

    conn.close()

    return redirect('/admin')

# حذف منتج

@app.route('/delete-product/<int:id>')
def delete_product(id):

    conn = sqlite3.connect('store.db')

    c = conn.cursor()

    c.execute('DELETE FROM products WHERE id=?', (id,))

    conn.commit()

    conn.close()

    return redirect('/admin')

# الطلبات

@app.route('/order', methods=['POST'])
def order():

    product = request.form['product']

    price = request.form['price']

    customer = request.form['customer']

    address = request.form['address']

    payment = request.form['payment']

    conn = sqlite3.connect('store.db')

    c = conn.cursor()

    c.execute(
        '''
        INSERT INTO orders
        (product,price,customer,address,payment,status)
        VALUES (?,?,?,?,?,?)
        ''',
        (product,price,customer,address,payment,'قيد التجهيز')
    )

    conn.commit()

    conn.close()

    return redirect('/orders')

@app.route('/orders')
def orders():

    conn = sqlite3.connect('store.db')

    c = conn.cursor()

    c.execute('SELECT * FROM orders ORDER BY id DESC')

    orders = c.fetchall()

    conn.close()

    return render_template('orders.html', orders=orders)

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)