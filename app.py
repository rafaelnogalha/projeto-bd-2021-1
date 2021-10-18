# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from database import criar_bd_tabelas, preencher_bd_tabelas
import re

# criar_bd_tabelas()
# preencher_bd_tabelas()

app = Flask(__name__)
  
app.secret_key = 'your secret key'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'rede_social'
  
mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'nome' in request.form and 'senha' in request.form:
        nome = request.form['nome']
        senha = request.form['senha']
        tipo_especialidade = request.form['tipo_especialidade']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if (tipo_especialidade == 'usuario'):            
            cursor.execute('SELECT * FROM usuarios WHERE nome = %s AND senha = %s', [nome, senha])
            system = "usuario"
        else:
            cursor.execute('SELECT * FROM administradores WHERE nome = %s AND senha = %s', [nome, senha])
            system = "administrador"
            #role = cursor.fetchone()
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['username'] = account['nome']
            session['password'] = account['senha']
            msg = 'Entrou!'
            if(system == "usuario"):
                session['id'] = account['id_usuario']
                return render_template('usuario.html', msg = msg)
            else:
                session['id'] = account['id_administrador']
                return render_template('administrador.html', msg = msg)
            # return render_template('index.html', msg = msg, system = system)
        else:
            msg = 'Nome / senha incorreto(s) !'
    return render_template('login.html', msg = msg)

#endpoint for search
# @app.route('/pesquisar', methods=['GET', 'POST'])
# def search():
#     if request.method == "POST":
#         usuario = request.form['usuario']
#         # search by author or book
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute("SELECT nome from Usuarios WHERE nome LIKE %s", [usuario])
#         mysql.connection.commit()
#         data = cursor.fetchall()
#         # all in the search box will return all the tuples
#         if len(data) == 0 and usuario == 'all': 
#             cursor.execute("SELECT nome from Usuarios")
#             mysql.connection.commit()
#             data = cursor.fetchall()
#         return render_template('search.html', data=data)
#     return render_template('search.html')

@app.route('/pesquisar', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        usuario = request.form['usuario']
        # search by author or book
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT nome, email from usuarios WHERE nome LIKE %s OR email LIKE %s", (usuario, usuario))
        data = cursor.fetchall()
        print("DATA1: ",data)
        print("DATA1: ",type(data))
        # all in the search box will return all the tuples
        if len(data) == 0 and usuario == 'all': 
            cursor.execute("SELECT nome, email from usuarios")
            data = cursor.fetchall()
            print("DATA2: ",data)
        return render_template('search.html', data=data)
    return render_template('search.html')

# @app.route('/pesquisar')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('id', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))  

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
        nome = request.form['nome']
        senha = request.form['senha']
        email = request.form['email']
        tipo_especialidade = request.form['tipo_especialidade']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if (tipo_especialidade == 'usuario'):            
            cursor.execute('SELECT * FROM usuarios WHERE nome = %s OR email = %s', [nome, email])
        else:
            cursor.execute('SELECT * FROM administradores WHERE nome = %s OR email = %s', [nome, email])
            
        conta = cursor.fetchone()
        if conta:
            msg = 'A conta já existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Email inválido!'
        elif not re.match(r'[A-Za-z0-9]+', nome):
            msg = 'Nome deve conter apenas letras e números!'
        elif not nome or not senha or not email:
            msg = 'Por favor, preencha o formulário corretamente!'
        else:
            if(tipo_especialidade == 'usuario'):
                sql = ("INSERT INTO usuarios(nome, senha, email) VALUES (%s, %s, %s)")
                cursor.execute(sql, (nome, senha, email))
                mysql.connection.commit()
            else:
                sql = ("INSERT INTO administradores(nome, senha, email) VALUES (%s, %s, %s)")
                cursor.execute(sql, (nome, senha, email))
                mysql.connection.commit()
                for key,val in request.form.items():
                  if key.startswith("funcao_"):
                    funcao = key.replace('funcao_', '')
                    cursor.execute('SELECT id_funcao FROM funcoes WHERE descricao = %s', (funcao, ))
                    id_func = cursor.fetchone()
                    values_view = id_func.values()
                    value_iterator = iter(values_view)
                    id_func = next(value_iterator)
                    cursor.execute('SELECT id_administrador FROM administradores WHERE nome = %s', (nome, ))
                    id_admin = cursor.fetchone()
                    values_view = id_admin.values()
                    value_iterator = iter(values_view)
                    id_admin = next(value_iterator)
                    cursor.execute("INSERT INTO funcoes_administradores(id_funcao, id_administrador) VALUES(%s, %s)", (id_func, id_admin, ))    
                    mysql.connection.commit()
            if(tipo_especialidade == 'usuario'):
                msg = 'Usuário registrado com sucesso!'
            else:
                msg = 'Administrador registrado com sucesso!'
    elif request.method == 'POST':
        msg = 'Por favor, preencha o formulário corretamente!'
    return render_template('register.html', msg = msg)


if __name__ == "__main__":
  app.run(debug = True)