from flask import Flask, render_template,request, session, redirect, url_for
from flask_mysqldb import MySQL
import mysql.connector as connector
from mysql.connector import errorcode 
import MySQLdb.cursors 
from database import cursor, db
import re

app = Flask(__name__, template_folder='templates')

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_senha'] = 'rafael23'
app.config['MYSQL_DB'] = 'rede_social'
mysql = MySQL(app)

def create_database():
  try:
    cursor = mysql.connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(app.config['MYSQL_DB']))
    print("Banco de Dados {} criado!".format(app.config['MYSQL_DB']))
  except connector.Error as err:
    if err.errno == errorcode.ER_DATABASE_EXISTS_ERROR:
      print("Banco de Dados ({}) jah existe".format(app.config['MYSQL_DB']))
    else:
      print(err.msg)

def create_tables():
  cursor = mysql.connection.cursor()
  cursor.execute("USE {}".format(app.config['MYSQL_DB']))
  print("Criando Tabela ...")
  with app.open_resource('schema.sql') as f:
    cursor.execute(f.read())
  mysql.connect.commit()
  
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    create_database()
    create_tables()
    msg = ''
    if request.method == 'POST' and 'nome' in request.form and 'senha' in request.form:
        nome = request.form['nome']
        senha = request.form['senha']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE nome = % s AND senha = % s', (nome, senha ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['nome']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / senha !'
    return render_template('login.html', msg = msg)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'nome' in request.form and 'senha' in request.form and 'email' in request.form :
        nome = request.form['username']
        senha = request.form['senha']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE nome = % s', (nome))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', nome):
            msg = 'Username must contain only characters and numbers !'
        elif not nome or not senha or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO usuarios VALUES (NULL, % s, % s, % s)', (nome, senha, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

if __name__ == "__main__":
  app.run(debug = True)