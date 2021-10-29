# Store this code in 'app.py' file
import os
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
import mysql.connector as myconnect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import io 
import base64
from PIL import Image


cnx = myconnect.connect(
    host="127.0.0.1",
    port=3306,
    user="admin",
    password="L@g0n1c0",
    auth_plugin='mysql_native_password',
    database='rede_social')

cur = cnx.cursor()

app = Flask(__name__)
  
app.secret_key = 'your secret key'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'L@g0n1c0'
app.config['MYSQL_DB'] = 'rede_social'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])  
  
mysql = MySQL(app)

# Permitindo upload de imagens
def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Redireciona o usuario/administrador para seus respectivos dashboards, 
# alem de inserir cookies para armazenar informacoes importantes
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    """Função que permite o login do usuário ou do administrador"""
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
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['username'] = account['nome']
            session['password'] = account['senha']
            msg = 'Entrou!'
            if(system == "usuario"):
                session["system"] = system
                session['id'] = account['id_usuario']
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT foto_de_perfil FROM usuarios where id_usuario = %s', (session['id'], ))
                foto_perfil = cursor.fetchone()
                if foto_perfil[0]:
                    result = "contem"
                else:
                    result = "vazio"
                session["result"] = result
                return redirect(url_for('dashboard_usuario', usuario = session['username']))
            else:
                session["system"] = system
                session['id'] = account['id_administrador']
                cursor.execute('SELECT id_funcao from funcoes_administradores where id_administrador = %s', (session['id'],))
                ids_func = cursor.fetchall();
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (session['id'], ))
                foto_perfil = cursor.fetchone()
                if foto_perfil[0]:
                    result = "contem"
                else:
                    result = "vazio"
                session["result"] = result
                lista_funcoes = [] 
                for linha in ids_func:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    values_view = linha.values()
                    value_iterator = iter(values_view)
                    first_value = next(value_iterator)
                   
                    cursor.execute('SELECT descricao FROM funcoes WHERE id_funcao = %s', (first_value, ))
                    descricao_funcao = cursor.fetchone();
                    
                    desc = descricao_funcao.get("descricao")
                 
                    lista_funcoes.append(desc)
                    session['functions'] = lista_funcoes
                
                return redirect(url_for('dashboard_admin', admin = session['username']))
        else:
            msg = 'Nome / senha incorreto(s) !'
    return render_template('login.html', msg = msg)

@app.route('/dashboard_usuario/<string:usuario>', methods=['GET', 'POST'])
def dashboard_usuario(usuario):
    """Função que renderiza o html do usuario, recebe como parametro o nome do usuario"""
    id_usuario = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM usuarios where id_usuario = %s', (id_usuario, ))
    foto_perfil = cursor.fetchone()  
    
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    return render_template('usuario.html', foto_perfil=foto_perfil, resultado = result)

@app.route('/dashboard_admin/<string:admin>', methods=['GET', 'POST'])
def dashboard_admin(admin):
    """Função que renderiza o html do administrador, recebe como parametro o nome do administrador"""
    lista_funcoes = session.get('functions')
    id_admin = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_admin, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    return render_template('administrador.html',descricao_funcao = lista_funcoes, foto_perfil=foto_perfil, resultado = result)

@app.route('/logout')
def logout():
    """Logout da aplicação"""
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Verifica se o nome e/ou email sao repetidos tanto para usuarios como para administradores
# Verifica se o email foi banido para usuarios
@app.route('/register', methods =['GET', 'POST'])
def register():
    """Sign up da aplicação"""
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
                cursor.execute("SELECT email FROM banidos WHERE email = %s", [email, ])
                banido = cursor.fetchone()
                if banido == None:
                    sql = ("INSERT INTO usuarios(nome, senha, email) VALUES (%s, %s, %s)")
                    cursor.execute(sql, (nome, senha, email))
                    mysql.connection.commit()
                    msg = 'Usuário registrado com sucesso!'
                else:
                    msg = 'O usuário com este email foi banido, tente com outro!'
            else:
                sql = ("INSERT INTO administradores(nome, senha, email) VALUES (%s, %s, %s)")
                cursor.execute(sql, (nome, senha, email))
                mysql.connection.commit()
                msg = 'Administrador registrado com sucesso!'
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
    elif request.method == 'POST':
        msg = 'Por favor, preencha o formulário corretamente!'
    return render_template('register.html', msg = msg)

# Administrador cria um novo grupo sem repeti-lo
@app.route('/criar_grupo/<string:admin>', methods =['GET', 'POST'])
def criar_grupo(admin):
    """Função para criar grupo, recebe como parametro o nome do administrador"""
    msg = ''
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (session['id'], ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        resultado = "contem"
    else:
        resultado = "vazio"
    funcoes = session.get('functions')
    if request.method == 'POST' and 'nome' in request.form:
        nome = request.form['nome']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT nome FROM grupos WHERE nome = %s', (nome, ))
        nome_e = cursor.fetchone()
        if not nome:
            msg = 'Por favor, preencha o formulário corretamente!'
        elif not re.match(r'[A-Za-z0-9]+', nome):
            msg = 'Nome deve conter apenas letras e números!'
        else:
            if nome_e == None:
                sql = ("INSERT INTO grupos(nome) VALUES (%s)")
                cursor.execute(sql, (nome, ))
                mysql.connection.commit()
                msg = 'Grupo criado com sucesso!'
            else: 
               msg = 'Este grupo já existe!' 
    elif request.method == 'POST':
        
        msg = 'Por favor, preencha o formulário corretamente!'
    return render_template('criar_grupo.html', msg = msg, descricao_funcao = funcoes, admin = admin, resultado= resultado, foto_perfil=foto_perfil)

# view_procedure
# Lista administradores da aplicacao(view) e mostra a quantidade de administradores(procedure)
@app.route('/listar_administradores/<string:admin>', methods =['GET', 'POST'])
def listar_administradores(admin):
    """Lista administradores cadastrados no banco de dados, recebe administrador como parâmetro"""
    funcoes = session.get('functions')
    id_administrador = session['id']
    cur.callproc('count_administradores', )
    radmin = []
    for result in cur.stored_results():
        radmin.append(result.fetchall())
    countadmin = radmin[1][0]
    countadmin = countadmin[0]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        resultado = "contem"
    else:
        resultado = "vazio"
    cursor.execute('SELECT * FROM view_administradores')
    administradores = cursor.fetchall()
    administradores_array = []
    for adm in administradores:
        administradores_array.append(adm)
    return render_template('listar_administradores.html', admin = admin, descricao_funcao = funcoes, foto_perfil = foto_perfil, resultado = resultado, administradores_array = administradores_array, count_administradores = countadmin)


# Renderiza html para procurar/editar um ou mais grupos na aplicacao
@app.route('/procurar_editar_grupo_template/<string:admin>', methods =['GET', 'POST'])
def procurar_editar_grupo_template(admin):
    """Renderiza html para procurar um ou mais grupos na aplicação, recebe administrador como parâmetro"""
    funcoes = session.get('functions')
    id_administrador = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        resultado = "contem"
    else:
        resultado = "vazio"
    return render_template('procurar_grupo.html', admin = admin , descricao_funcao = funcoes, foto_perfil = foto_perfil, resultado = resultado)

# Renderiza html para editar um grupo na aplicacao
@app.route('/editar_grupo_template', methods =['GET', 'POST'])
def editar_grupo_template():
    """Renderiza html para editar um grupo na aplicação"""
    # POST request
    msg = ''
    id_administrador = session['id']
    funcoes = session.get('functions')
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        grupos = request.get_json()
        for linha in grupos.items():
            arr = linha[1]
        cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
        foto_perfil = cursor.fetchone()
        if foto_perfil[0]:
            foto_perfil = foto_perfil[0]
            foto_perfil = foto_perfil.decode('utf-8')
            resultado = "contem"
        else:
            resultado = "vazio"
        return render_template('editar_grupo.html', msg = msg, grupo = arr, descricao_funcao = funcoes, resultado = resultado, foto_perfil = foto_perfil)

# Executa query de update para um grupo e renderiza html de procurar grupo
@app.route('/editar_grupo', methods =['GET', 'POST'])
def editar_grupo():
    """Executa query de update para um grupo e renderiza html de procurar grupo"""
    # POST request
    msg = ''
    id_administrador = session['id']
    funcoes = session.get('functions')
    if request.method == 'POST' and 'nome' in request.form:
        nome = request.form['nome']
        grupo_nome = request.form['grupo']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT nome FROM grupos WHERE nome = %s', (nome, ))
        result = cursor.fetchone()
        if (result == None):
            cursor.execute("UPDATE grupos SET nome = %s WHERE nome = %s", (nome, grupo_nome, ))
            mysql.connection.commit()
            msg = 'nome do grupo alterado com sucesso!'
        else:
            msg = 'Esse nome para grupo já existe. Tente outro'
        cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
        foto_perfil = cursor.fetchone()
        if foto_perfil[0]:
            foto_perfil = foto_perfil[0]
            foto_perfil = foto_perfil.decode('utf-8')
            resultado = "contem"
        else:
            resultado = "vazio"
    return render_template('procurar_grupo.html', msg = msg, descricao_funcao = funcoes, resultado = resultado, foto_perfil = foto_perfil)
        
# Renderiza html para procurar/deletar um ou mais grupos na aplicacao  
@app.route('/procurar_deletar_grupo_template/<string:admin>', methods =['GET', 'POST'])
def procurar_deletar_grupo_template(admin):
    """Renderiza html para deletar um ou mais grupos na aplicação, recebe administrador como parâmetro"""
    funcoes = session.get('functions')
    id_administrador = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        resultado = "contem"
    else:
        resultado = "vazio"
    return render_template('deletar_grupo.html', admin = admin , descricao_funcao = funcoes, resultado=resultado, foto_perfil=foto_perfil)

# Renderiza html para deletar um grupo na aplicacao
@app.route('/deletar_grupo', methods =['GET', 'POST'])
def deletar_grupo():
    """Renderiza html para deletar um grupo na aplicacao"""
    # POST request
    msg = ''
    if request.method == 'POST':
        grupos = request.get_json()
        for linha in grupos.items():
            arr = linha[1]
        for item in arr:
            sql = ("DELETE FROM grupos WHERE nome = %s")
            cursor = mysql.connection.cursor()
            cursor.execute(sql, (item, ))
            mysql.connection.commit()
            msg = 'Grupo deletado com sucesso!'
        #return 'Sucesss', 200
    return render_template('deletar_grupo.html', msg = msg) and 'Sucesss', 200
 
# Renderiza html para procurar/banir um ou mais usuarios na aplicacao   
@app.route('/procurar_banir_usuario_template/<string:admin>', methods =['GET', 'POST'])
def procurar_banir_usuario_template(admin):
    """Renderiza html para procurar/banir um ou mais usuarios na aplicacao"""
    funcoes = session.get('functions')
    id_administrador = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        resultado = "contem"
    else:
        resultado = "vazio"
    return render_template('banir_usuario.html', admin = admin , descricao_funcao = funcoes, resultado = resultado, foto_perfil = foto_perfil)

# Executa query de delete da tabela usuarios e insere na tabela banidos e renderiza html de procurar usuarios
@app.route('/banir_usuario', methods =['GET', 'POST'])
def banir_usuario():
    """Executa query de delete da tabela usuarios e insere na tabela banidos e renderiza html de procurar usuarios"""
    # POST request
    id_admin = session['id']
    msg = ''
    if request.method == 'POST':
        usuarios = request.get_json()
        cursor = mysql.connection.cursor()
        for linha in usuarios.items():
            arr = linha[1]
            
        for item in arr:
            cursor.execute("SELECT email FROM usuarios where nome = %s", (item, ))
            email_usuario = cursor.fetchone()
            sql = ("DELETE FROM usuarios WHERE nome = %s")
            cursor.execute(sql, (item, ))
            mysql.connection.commit()
            cursor.execute("INSERT INTO banidos(id_administrador, email) VALUES (%s, %s)", (id_admin, email_usuario))
            mysql.connection.commit()
    return render_template('banir_usuario.html', msg = msg) and 'Sucesss', 200

# Retorna JSON dos usuarios banidos
@app.route('/procurar_banir_usuario', methods =['GET', 'POST'])
def procurar_banir_usuario():
    """Retorna JSON dos usuarios banidos"""
    searchbox = "%" + request.values.get("text") + "%"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome FROM usuarios where nome Like %s order by nome", (searchbox, ))
    result = cursor.fetchall()
    return jsonify(result)

# Renderiza html para procurar/editar um usuario na aplicacao   
@app.route('/procurar_editar_usuario_template/<string:admin>', methods =['GET', 'POST'])
def procurar_editar_usuario_template(admin):
    """Renderiza html para procurar/editar um usuario na aplicacao"""
    funcoes = session.get('functions')
    id_administrador = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        resultado = "contem"
    else:
        resultado = "vazio"
    return render_template('procurar_usuario.html', admin = admin , descricao_funcao = funcoes, resultado = resultado, foto_perfil = foto_perfil)

# Renderiza html para editar um usuario na aplicacao   
@app.route('/editar_usuario_template', methods =['GET', 'POST'])
def editar_usuario_template():
    """Renderiza html para editar um usuario na aplicacao"""
    # POST request
    msg = ''
    funcoes = session.get('functions')
    id_administrador = session['id']
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        usuarios = request.get_json()
        for linha in usuarios.items():
            nome_usuario = linha[1]
        arr_usuario = []
        arr_usuario.append(nome_usuario)
        cursor.execute('SELECT id_usuario, email, senha FROM usuarios WHERE nome = %s', (nome_usuario, ))
        result = cursor.fetchone()
        for linha in result:
            arr_usuario.append(linha)
        cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
        foto_perfil = cursor.fetchone()
        if foto_perfil[0]:
            foto_perfil = foto_perfil[0]
            foto_perfil = foto_perfil.decode('utf-8')
            resultado = "contem"
        else:
            resultado = "vazio"
        return render_template('editar_usuario.html', msg = msg, usuario = arr_usuario, descricao_funcao = funcoes, resultado=resultado, foto_perfil = foto_perfil)
  
# Executa query de update da tabela usuarios e renderiza html de procurar usuarios  
@app.route('/editar_usuario', methods =['GET', 'POST'])
def editar_usuario():
    """Executa query de update da tabela usuarios e renderiza html de procurar usuarios"""
    # POST request
    msg = ''
    id_admin = session['id']
    funcoes = session.get('functions')
    if request.method == 'POST' and 'nome' in request.form:
        nome = request.form['nome']
        senha = request.form['senha']
        email = request.form['email']
        nomeAtual = request.form['nomeAtual']
        senhaAtual = request.form['senhaAtual']
        emailAtual = request.form['emailAtual']
        usuario_nome = request.form['nomeAtual']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_usuario FROM usuarios WHERE nome = %s OR email = %s', (nome, email, ))
        id_usuario = cursor.fetchone()
        cursor.execute("SELECT foto_de_perfil FROM administradores where id_administrador = %s", (id_admin, ))
        foto_perfil = cursor.fetchone()
        foto_perfil = foto_perfil[0]
        if foto_perfil:
            foto_perfil = foto_perfil.decode('utf-8')
            result = "contem"
        else:
            
            result = "vazio"

        if (id_usuario == None):
            if nome == "":
                nome = nomeAtual
            if senha == "":
                senha = senhaAtual
            if email == "":
                email = emailAtual
            cursor.execute("UPDATE usuarios SET nome = %s, email = %s, senha = %s WHERE nome = %s", (nome, email, senha, usuario_nome, ))
            mysql.connection.commit()
            cursor.execute('SELECT id_usuario FROM usuarios WHERE nome = %s', (nome, ))
            id_usuario = cursor.fetchone()
            cursor.execute("INSERT INTO editados(id_administrador, id_usuario) VALUES (%s, %s)", (id_admin, id_usuario))
            mysql.connection.commit()
            msg = 'As informações do usuario foram alteradas com sucesso!'
        else:
            msg = 'Esse nome ou email para usuario já existe. Tente outro'
    return render_template('procurar_usuario.html', msg = msg, descricao_funcao = funcoes, resultado = result, foto_perfil = foto_perfil)

# Renderiza html para entrar em um grupo na aplicacao
@app.route('/procurar_entrar_grupo_template/<string:usuario>', methods =['GET', 'POST'])
def procurar_entrar_grupo_template(usuario):
    """Renderiza html para entrar em um grupo na aplicacao"""
    id_usuario = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT foto_de_perfil FROM usuarios where id_usuario = %s", (id_usuario, ))
    foto_perfil = cursor.fetchone()
    foto_perfil = foto_perfil[0]
    if foto_perfil:
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    return render_template('entrar_grupo.html', usuario = usuario, resultado = result, foto_perfil = foto_perfil)

# Executa query para entrar em um grupo na aplicacao e renderiza html de entrar em grupo
@app.route('/entrar_grupo', methods =['GET', 'POST'])
def entrar_grupo():
    """Executa query para entrar em um grupo na aplicacao e renderiza html de entrar em grupo"""
    id_usuario = session['id']
    msg = ''
    if request.method == 'POST':
        grupos = request.get_json()
        cursor = mysql.connection.cursor()
        for linha in grupos.items():
            arr = linha[1]
        for item in arr:
            cursor.execute("SELECT id_grupo FROM grupos_usuarios where id_usuario = %s ", (id_usuario, ))
            ids_grupo_existe = cursor.fetchall()
            cursor.execute("SELECT id_grupo FROM grupos where nome = %s", (item, ))
            id_grupo = cursor.fetchone()
            value_iterator_id = iter(id_grupo)
            id_grupo = next(value_iterator_id)
            flag = 0
            for i in ids_grupo_existe:
                
                if i[0] == id_grupo:
                    
                    msg = 'Usuário já faz parte do grupo!'
                    flag = 1
                    
            if flag == 0:
                cursor.execute("INSERT INTO grupos_usuarios(id_grupo, id_usuario) VALUES (%s, %s)", (id_grupo, id_usuario))
                mysql.connection.commit()
                msg = 'Usuário entrou com sucesso!'
        #return 'Sucesss', 200
    return render_template('entrar_grupo.html', msg = msg) and 'Sucesss', 200

# Executa query para entrar em um grupo na aplicacao e renderiza html de entrar em grupo
@app.route('/sair_grupo', methods =['GET', 'POST'])
def sair_grupo():
    id_usuario = session['id']
    if request.method == 'POST':
        grupos = request.get_json()
        cursor = mysql.connection.cursor()
        for linha in grupos.items():
            arr = linha[1]
        for item in arr:
            cursor.execute("SELECT id_grupo FROM grupos where nome = %s", (item, ))
            id_grupo = cursor.fetchone()
            value_iterator_id = iter(id_grupo)
            id_grupo = next(value_iterator_id)
            cursor.execute("SELECT id_grupo_usuario FROM grupos_usuarios where id_usuario = %s and id_grupo = %s", (id_usuario, id_grupo))
            id_grupo_usuario = cursor.fetchone()
            if id_grupo_usuario != None:
                cursor.execute("DELETE FROM grupos_usuarios WHERE id_usuario = %s and id_grupo = %s", (id_usuario, id_grupo))
                mysql.connection.commit()
                msg = 'Usuário removido do(s) grupo(s) com sucesso!'
        #return 'Sucesss', 200
    return render_template('entrar_grupo.html', msg = msg)

# Retorna JSON da procura do grupo
@app.route('/procurar_grupo', methods =['GET', 'POST'])
def procurar_grupo():
    """Retorna JSON para procurar grupo"""
    id_usuario = session['id']
    searchbox = "%" + request.values.get("text") + "%"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome FROM grupos where nome Like %s order by nome", (searchbox, ))
    result = cursor.fetchall()
    u = []
    for grupo in result:
        cursor.execute("SELECT id_grupo FROM grupos where nome = %s", (grupo[0], ))
        id_grupo = cursor.fetchone()
        cursor.execute("SELECT id_grupo_usuario FROM grupos_usuarios where id_usuario = %s and id_grupo = %s", (id_usuario, id_grupo))
        id_grupo_usuario = cursor.fetchone()
        if id_grupo_usuario == None:
            u.append(grupo[0])
    return jsonify(u)

# Retorna JSON para mostrar grupo
@app.route('/mostrar_grupos', methods =['GET', 'POST'])
def mostrar_grupos():
    """Retorna JSON para mostrar grupo"""
    cursor = mysql.connection.cursor()
    id_usuario = session['id']
    cursor.execute("SELECT id_grupo FROM grupos_usuarios where id_usuario = %s", (id_usuario, ))
    result_grupos = cursor.fetchall()
    u = []
    for grupo in result_grupos:
        
        cursor.execute("SELECT nome FROM grupos where id_grupo = %s", (grupo, ))
        nome = cursor.fetchone()
        u.append(nome)
    return jsonify(u)

# Renderiza html para procurar/adicionar um amigo na aplicacao
@app.route('/procurar_adicionar_usuarios_template/<string:usuario>', methods =['GET', 'POST'])
def procurar_adicionar_usuarios_template(usuario):
    """Renderiza html para procurar/adicionar um amigo na aplicacao"""
    id_usuario = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT foto_de_perfil FROM usuarios where id_usuario = %s", (id_usuario, ))
    foto_perfil = cursor.fetchone()
    foto_perfil = foto_perfil[0]
    if foto_perfil:
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    return render_template('procurar_adicionar_usuario.html', usuario = usuario, resultado = result, foto_perfil = foto_perfil)

# Executa query para adicionar usuario e renderiza html para procurar usuario
@app.route('/adicionar_usuario', methods =['GET', 'POST'])
def adicionar_usuario():
    """Executa query para adicionar usuario"""
    id_usuario1 = session['id']
    if request.method == 'POST':
        usuarios = request.get_json()
        cursor = mysql.connection.cursor()
        for linha in usuarios.items():
            arr = linha[1]
        for item in arr:
            cursor.execute("SELECT id_usuario FROM usuarios where nome = %s", (item, ))
            id_usuario2 = cursor.fetchone()
            value_iterator_id = iter(id_usuario2)
            id_usuario2 = next(value_iterator_id)
            cursor.execute("SELECT id_amigos FROM amigos where id_usuario1 = %s and id_usuario2 = %s", (id_usuario1, id_usuario2))
            id_usuario_amigo = cursor.fetchone()
            if id_usuario_amigo == None and id_usuario2 != id_usuario1:
                cursor.execute("INSERT INTO amigos(id_usuario1, id_usuario2) VALUES (%s, %s)", (id_usuario1, id_usuario2))
                mysql.connection.commit()
                msg = 'Usuário(s) adicionado(s) com sucesso!'
        #return 'Sucesss', 200
    return render_template('procurar_adicionar_usuario.html', msg = msg)

# Executa query para desfazer amizade
@app.route('/desfazer_amizade', methods =['GET', 'POST'])
def desfazer_amizade():
    """Executa query para desfazer amizade"""
    id_usuario1 = session['id']
    if request.method == 'POST':
        usuarios = request.get_json()
        cursor = mysql.connection.cursor()
        for linha in usuarios.items():
            arr = linha[1]
        for item in arr:
            cursor.execute("SELECT id_usuario FROM usuarios where nome = %s", (item, ))
            id_usuario2 = cursor.fetchone()
            value_iterator_id = iter(id_usuario2)
            id_usuario2 = next(value_iterator_id)
            cursor.execute("SELECT id_amigos FROM amigos where id_usuario1 = %s and id_usuario2 = %s", (id_usuario1, id_usuario2))
            id_usuario_amigo = cursor.fetchone()
            if id_usuario_amigo != None and id_usuario2 != id_usuario1:
                cursor.execute("DELETE FROM amigos WHERE id_usuario1 = %s and id_usuario2 = %s", (id_usuario1, id_usuario2))
                mysql.connection.commit()
                msg = 'Usuário(s) removido(s) com sucesso!'
        #return 'Sucesss', 200
    return render_template('procurar_adicionar_usuario.html', msg = msg)

# Retorna JSON para de usuarios pesquisados
@app.route('/procurar_usuario', methods =['GET', 'POST'])
def procurar_usuario():
    """Retorna JSON para de usuarios pesquisados"""
    id_usuario1 = session['id']
    searchbox = "%" + request.values.get("text") + "%"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome FROM usuarios where nome Like %s order by nome", (searchbox, ))
    result = cursor.fetchall()
    u = []
    for user in result:
        cursor.execute("SELECT id_usuario FROM usuarios where nome = %s", (user[0], ))
        id_usuario2 = cursor.fetchone()
        cursor.execute("SELECT id_amigos FROM amigos where id_usuario1 = %s and id_usuario2 = %s", (id_usuario1, id_usuario2))
        id_usuario_amigo = cursor.fetchone()
        if id_usuario_amigo == None and id_usuario2[0] != id_usuario1:
            u.append(user[0])
    return jsonify(u)

# Retorna JSON dos amigos de um determindado usuario
@app.route('/mostrar_amigos', methods =['GET', 'POST'])
def mostrar_amigos():
    """Retorna JSON dos amigos de um determindado usuario"""
    cursor = mysql.connection.cursor()
    id_usuario1 = session['id']
    cursor.execute("SELECT id_usuario2 FROM amigos where id_usuario1 = %s", (id_usuario1, ))
    result_amigos = cursor.fetchall()
    u = []
    for user in result_amigos:
      
        cursor.execute("SELECT nome FROM usuarios where id_usuario = %s", (user, ))
        nome = cursor.fetchone()
        u.append(nome)
    return jsonify(u)

##  Postagens_administrdor  ##

# Retorna JSON das postagens de todos os adminsitradores da rede social
@app.route('/procurar_postagem_administrador', methods =['GET', 'POST'])
def procurar_postagem_administrador():
    """Retorna JSON das postagens de todos os adminsitradores da rede social"""
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT descricao FROM postagens_administradores order by id_postagens_administradores")
    result_postagem = cursor.fetchall()
    cursor.execute("SELECT id_administrador FROM postagens_administradores order by id_postagens_administradores")
    result_administrador = cursor.fetchall()
    u = []
    for user in result_administrador:
    
        cursor.execute("SELECT nome FROM administradores where id_administrador = %s", (user, ))
        nome = cursor.fetchall()
        u.append(nome)
    r = []
    result = list(result_postagem)
    for i in range(len(result_administrador)):
        r.append(u[i]+result[i])
    return jsonify(r)

# Renderiza html das postagens dos administradores
@app.route('/adicionar_postagens_administrador_template/<string:admin>', methods =['GET', 'POST'])
def adicionar_postagens_administrador_template(admin):
    """Renderiza html das postagens dos administradores, recebe administrador como parâmetro"""
    funcionalidades = session['functions']
    id_administrador = session["id"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        resultado = "contem"
    else:
        resultado = "vazio"
    return render_template('adicionar_postagens_administrador.html', admin = admin, foto_perfil = foto_perfil, descricao_funcao = funcionalidades, resultado=resultado)

# Executa query para adicionar postagem de um administrador
@app.route('/adicionar_postagens_administrador', methods =['GET', 'POST'])
def adicionar_postagens_administrador():
    """Executa query para adicionar postagem de uma administrador"""
    msg = ''  
    funcionalidades = session['functions']
    id_administrador = session["id"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_administrador, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        resultado = "contem"
    else:
        resultado = "vazio"
    if request.method == 'POST' and 'descricao' in request.form:
        descricao = request.form['descricao']
        cursor = mysql.connection.cursor()
        
        cursor.execute("INSERT INTO postagens_administradores(id_administrador, descricao) VALUES(%s, %s)", (session['id'], descricao, ))
        mysql.connection.commit()
        msg = 'Postagem adicionada com sucesso'
    elif request.method == 'POST':
        msg = 'Por favor, não poste nada em branco!'
    return render_template('adicionar_postagens_administrador.html', msg = msg, foto_perfil = foto_perfil, descricao_funcao = funcionalidades, resultado=resultado)

## Postagens_usuarios ##

# Retorna JSON das postagens de todos os usuarios da rede social 
@app.route('/procurar_postagem', methods =['GET', 'POST'])
def procurar_postagem():
    """# Retorna JSON das postagens de todos os usuarios da rede social """
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT descricao FROM postagens_usuarios order by id_postagens_usuarios")
    result_postagem = cursor.fetchall()
    cursor.execute("SELECT id_usuario FROM postagens_usuarios order by id_postagens_usuarios")
    result_usuario = cursor.fetchall()
    u = []
    for user in result_usuario:
     
        cursor.execute("SELECT nome FROM usuarios where id_usuario = %s", (user, ))
        nome = cursor.fetchall()
        u.append(nome)
    r = []
    result = list(result_postagem)
    for i in range(len(result_usuario)):
        r.append(u[i]+result[i])
    return jsonify(r)

# Renderiza html das postagens de um usuario
@app.route('/adicionar_postagens_template/<string:usuario>', methods =['GET', 'POST'])
def adicionar_postagens_template(usuario):
    """Renderiza html das postagens de um usuario"""
    id_usuario = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT foto_de_perfil FROM usuarios where id_usuario = %s", (id_usuario, ))
    foto_perfil = cursor.fetchone()
    foto_perfil = foto_perfil[0]
    if foto_perfil:
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    return render_template('adicionar_postagens.html', usuario = usuario, resultado = result, foto_perfil = foto_perfil)

# Executa query para adicionar postagem de um usuario
@app.route('/adicionar_postagens', methods =['GET', 'POST'])
def adicionar_postagens():
    msg = ''
    id_usuario = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT foto_de_perfil FROM usuarios where id_usuario = %s", (id_usuario, ))
    foto_perfil = cursor.fetchone()
    foto_perfil = foto_perfil[0]
    if foto_perfil:
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    if request.method == 'POST' and 'descricao' in request.form:
        descricao = request.form['descricao']
        cursor = mysql.connection.cursor()
        
        cursor.execute("INSERT INTO postagens_usuarios(id_usuario, descricao) VALUES(%s, %s)", (session['id'], descricao, ))
        mysql.connection.commit()
        msg = 'Postagem adicionada com sucesso'
    elif request.method == 'POST':
        msg = 'Por favor, não poste nada em branco!'
    return render_template('adicionar_postagens.html', msg = msg, resultado = result, foto_perfil = foto_perfil)

## Upload de imagens ##

# Renderiza html para upload de uma foto de perfil de um administrador/usuario
@app.route('/upload_form')
def upload_form():
    """Renderiza html para upload de uma foto de perfil de uma administrador/usuario"""
    id = session['id']
    cursor = mysql.connection.cursor()
    if session["system"] == 'usuario':
        cursor.execute("SELECT foto_de_perfil FROM usuarios where id_usuario = %s", (id, ))
    else:
        cursor.execute("SELECT foto_de_perfil FROM administradores where id_administrador = %s", (id, ))
    foto_perfil = cursor.fetchone()
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
      
    else:
        result = "vazio"
    return render_template('upload.html', foto_perfil = foto_perfil, resultado = result, tipo_usuario = session["system"], funcoes = session['functions'])

# Executa a query de update da foto de perfil de um usuario ou administrador
@app.route('/upload_de_imagem', methods=['POST'])
def upload_de_imagem():
    """Executa a query de update da foto de perfil de um usuario ou administrador"""
    id = session['id']
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Nenhuma imagem foi selecionada')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        text, file_extension = os.path.splitext(file.filename)
        filename = Image.open("/home/rafaelnogalha/Imagens/"+file.filename)
        filename = filename.convert('RGB')
        data = io.BytesIO()
        filename.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())
        cursor = mysql.connection.cursor()
        tipo_usuario = session["system"]
        if tipo_usuario == 'usuario':
            cursor.execute("UPDATE usuarios SET foto_de_perfil = %s WHERE id_usuario = %s", (encoded_img_data, id))
        else:
            cursor.execute("UPDATE administradores SET foto_de_perfil = %s WHERE id_administrador = %s", (encoded_img_data, id))
        mysql.connection.commit()
        flash('A imagem foi alterada com sucesso')
        return render_template('upload.html', foto_perfil=encoded_img_data.decode('utf-8'), tipo_usuario = tipo_usuario, funcoes = session['functions'])
    else:
        flash('Extensões de imagens permitidas -> png, jpg, jpeg, gif')
        return redirect(request.url)

# Seleciona a foto de um usuario/administrador
@app.route('/display/<filename>')
def display_image(filename):
    """Seleciona a foto de um usuario/administrador"""
    tipo_usuario = session["system"]
    id = session['id']
    cursor = mysql.connection.cursor()
    if session["result"] == "contem":
        if tipo_usuario == 'usuario':
            cursor.execute("SELECT foto_de_perfil FROM usuarios where id_usuario = %s", (id, ))
        else:
            cursor.execute("SELECT foto_de_perfil FROM administradores where id_administrador = %s", (id, ))
        
        foto_perfil = cursor.fetchone()
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
    return redirect(url_for('static', foto_perfil=foto_perfil), code=301)

if __name__ == "__main__":
  app.run(debug = True)