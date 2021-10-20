# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_login import login_required
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
                #return render_template('usuario.html', msg = msg)
                return redirect(url_for('dashboard_usuario', usuario = session['username']))
            else:
                session['id'] = account['id_administrador']
                cursor.execute('SELECT id_funcao from funcoes_administradores where id_administrador = %s', (session['id'],))
                ids_func = cursor.fetchall();
                print("TIPO:",type(ids_func))
                # print("TIPO Coluna:",type(ids_func[0]))
                lista_funcoes = [] 
                for linha in ids_func:
                    values_view = linha.values()
                    value_iterator = iter(values_view)
                    first_value = next(value_iterator)
                    # print("IDS0:", first_value)
                    # print("IDS0:", type(first_value))
                    cursor.execute('SELECT descricao FROM funcoes WHERE id_funcao = %s', (first_value, ))
                    descricao_funcao = cursor.fetchone();
                    print("descricao_funcao:", descricao_funcao)
                    print("TIPO_desc:", type(descricao_funcao))
                    desc = descricao_funcao.get("descricao")
                    # for desc1 in descricao_funcao:
                    #     print("desc:", desc1[9])
                    #     print("TIPO_descasdasdasd:", type(desc1[9]))
                        
                    lista_funcoes.append(desc)
                    session['functions'] = lista_funcoes
                
                #return render_template('administrador.html', msg = msg, descricao_funcao = lista_funcoes)
                return redirect(url_for('dashboard_admin', admin = session['username']))
            # return render_template('index.html', msg = msg, system = system)
        else:
            msg = 'Nome / senha incorreto(s) !'
    return render_template('login.html', msg = msg)

@app.route('/dashboard_usuario/<string:usuario>', methods=['GET', 'POST'])
def dashboard_usuario(usuario):
    return render_template('usuario.html')

@app.route('/dashboard_admin/<string:admin>', methods=['GET', 'POST'])
def dashboard_admin(admin):
    lista_funcoes = session.get('functions')
    return render_template('administrador.html',descricao_funcao = lista_funcoes)

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


@app.route('/criar_grupo/<string:admin>', methods =['GET', 'POST'])
def criar_grupo(admin):
    msg = ''
    funcoes = session.get('functions')
    
    if request.method == 'POST' and 'nome' in request.form:
        nome = request.form['nome']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not nome:
            msg = 'Por favor, preencha o formulário corretamente!'
        elif not re.match(r'[A-Za-z0-9]+', nome):
            msg = 'Nome deve conter apenas letras e números!'
        else:
            sql = ("INSERT INTO grupos(nome) VALUES (%s)")
            cursor.execute(sql, (nome, ))
            mysql.connection.commit()
            msg = 'Grupo criado com sucesso!'
    elif request.method == 'POST':
        msg = 'Por favor, preencha o formulário corretamente!'
    return render_template('criar_grupo.html', msg = msg, descricao_funcao = funcoes, admin = admin)

@app.route('/procurar_editar_grupo_template/<string:admin>', methods =['GET', 'POST'])
def procurar_editar_grupo_template(admin):
    funcoes = session.get('functions')
    return render_template('procurar_grupo.html', admin = admin , descricao_funcao = funcoes)

@app.route('/procurar_editar_grupo', methods =['GET', 'POST'])
def procurar_editar_grupo():
    searchbox = "%" + request.values.get("text") + "%"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome FROM grupos where nome Like %s order by nome", (searchbox, ))
    result = cursor.fetchall()
    return jsonify(result)
    
@app.route('/procurar_deletar_grupo_template/<string:admin>', methods =['GET', 'POST'])
def procurar_deletar_grupo_template(admin):
    funcoes = session.get('functions')
    return render_template('deletar_grupo.html', admin = admin , descricao_funcao = funcoes)

@app.route('/procurar_deletar_grupo', methods =['GET', 'POST'])
def procurar_deletar_grupo():
    searchbox = "%" + request.values.get("text") + "%"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome FROM grupos where nome Like %s order by nome", (searchbox, ))
    result = cursor.fetchall()
    return jsonify(result)
    
@app.route('/procurar_banir_usuario_template/<string:admin>', methods =['GET', 'POST'])
def procurar_banir_usuario_template(admin):
    funcoes = session.get('functions')
    return render_template('banir_usuario.html', admin = admin , descricao_funcao = funcoes)

@app.route('/procurar_banir_usuario', methods =['GET', 'POST'])
def procurar_banir_usuario():
    searchbox = "%" + request.values.get("text") + "%"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome FROM usuarios where nome Like %s order by nome", (searchbox, ))
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/procurar_editar_usuario_template/<string:admin>', methods =['GET', 'POST'])
def procurar_editar_usuario_template(admin):
    funcoes = session.get('functions')
    print("sadasdfsdfasdfsdSSSDFSDF")
    return render_template('editar_usuario.html', admin = admin , descricao_funcao = funcoes)


@app.route('/procurar_entrar_grupo_template/<string:usuario>', methods =['GET', 'POST'])
def procurar_entrar_grupo_template(usuario):
    return render_template('entrar_grupo.html', usuario = usuario)

@app.route('/procurar_entrar_grupo', methods =['GET', 'POST'])
def procurar_entrar_grupo():
    searchbox = "%" + request.values.get("text") + "%"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome FROM grupos where nome Like %s order by nome", (searchbox, ))
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/procurar_adicionar_usuarios_template/<string:usuario>', methods =['GET', 'POST'])
def procurar_adicionar_usuarios_template(usuario):
    return render_template('entrar_grupo.html', usuario = usuario)

@app.route('/procurar_adicionar_usuarios', methods =['GET', 'POST'])
def procurar_adicionar_usuarios():
    searchbox = "%" + request.values.get("text") + "%"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome FROM usuarios where nome Like %s order by nome", (searchbox, ))
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/adicionar_postagens_template/<string:usuario>', methods =['GET', 'POST'])
def adicionar_postagens_template(usuario):
    return render_template('adicionar_postagens.html', usuario = usuario)

@app.route('/adicionar_postagens', methods =['GET', 'POST'])
def adicionar_postagens():
    msg = ''
    if request.method == 'POST' and 'descricao' in request.form:
        descricao = request.form['descricao']
        cursor = mysql.connection.cursor()
        
        cursor.execute("INSERT INTO postagens_usuarios(id_usuario, descricao) VALUES(%s, %s)", (session['id'], descricao, ))
        mysql.connection.commit()
        msg = 'Postagem adicionada com sucesso'
    else:
        msg = 'Por favor, não poste nada em branco!'
    return render_template('adicionar_postagens.html', msg = msg)


if __name__ == "__main__":
  app.run(debug = True)