from flask import Flask, render_template,request, redirect, jsonify
from flask_mysqldb import MySQL
import mysql.connector as connector
from mysql.connector import errorcode  
from database import cursor, db

app = Flask(__name__, template_folder='templates')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'L@g0n1c0'
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

@app.route('/', methods = ['GET', 'POST'])
def index():
  create_database()
  create_tables()
  if(request.method == 'POST'):
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    print(nome, email, senha)
    #cursor = mysql.connection.cursor()
    sql = ("INSERT INTO usuarios (nome,email,senha) VALUES (%s,%s,%s)")
    cursor.execute(sql,(nome, email,senha))
    
    db.commit()
    id_usuario = cursor.lastrowid
    print("Usuario criado {}".format(id_usuario))
    return redirect('/usuarios')
  return render_template('index.html')

@app.route('/usuarios')
def usuarios():
  cursor = mysql.connection.cursor()
  resultValue = cursor.execute('SELECT * FROM usuarios')
  if resultValue > 0:
    userDetails = cursor.fetchall()
  #render_template('usuarios.html')
  return jsonify(data=userDetails)

if __name__ == "__main__":
  app.run(debug = True)