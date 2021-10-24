# Store this code in 'app.py' file
import os
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_login import login_required
from database import criar_bd_tabelas, preencher_bd_tabelas
from werkzeug.utils import secure_filename
import re
import io 
import base64
from PIL import Image

# criar_bd_tabelas()
# preencher_bd_tabelas()

app = Flask(__name__)
  
app.secret_key = 'your secret key'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'rede_social'

# Permitindo upload de imagens
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])  
  
  
mysql = MySQL(app)

# funcao que pega a extensao da imagem
def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                session["system"] = system
                session['id'] = account['id_usuario']
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT foto_de_perfil FROM usuarios where id_usuario = %s', (session['id'], ))
                foto_perfil = cursor.fetchone()
                print("FOTO DE PERFIL", foto_perfil)
                if foto_perfil[0]:
                    result = "contem"
                else:
                    result = "vazio"
                session["result"] = result
                #return render_template('usuario.html', msg = msg)
                return redirect(url_for('dashboard_usuario', usuario = session['username']))
            else:
                session["system"] = system
                session['id'] = account['id_administrador']
                cursor.execute('SELECT id_funcao from funcoes_administradores where id_administrador = %s', (session['id'],))
                ids_func = cursor.fetchall();
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (session['id'], ))
                foto_perfil = cursor.fetchone()
                print("FOTO DE PERFIL", foto_perfil)
                if foto_perfil[0]:
                    result = "contem"
                else:
                    result = "vazio"
                session["result"] = result
                # print("TIPO Coluna:",type(ids_func[0]))
                lista_funcoes = [] 
                for linha in ids_func:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
    id_usuario = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM usuarios where id_usuario = %s', (id_usuario, ))
    foto_perfil = cursor.fetchone()  
    
    if foto_perfil[0]:
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    return render_template('usuario.html', foto_perfil=foto_perfil, resultado = result)

@app.route('/dashboard_admin/<string:admin>', methods=['GET', 'POST'])
def dashboard_admin(admin):
    lista_funcoes = session.get('functions')
    id_admin = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foto_de_perfil FROM administradores where id_administrador = %s', (id_admin, ))
    foto_perfil = cursor.fetchone()
    print("FOTO DE PERFIL", foto_perfil)
    if foto_perfil[0]:
        foto_perfil = foto_perfil[0]
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    return render_template('administrador.html',descricao_funcao = lista_funcoes, foto_perfil=foto_perfil, resultado = result)

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
    return render_template('criar_grupo.html', msg = msg, descricao_funcao = funcoes, admin = admin, resultado = session['result'])

@app.route('/procurar_editar_grupo_template/<string:admin>', methods =['GET', 'POST'])
def procurar_editar_grupo_template(admin):
    funcoes = session.get('functions')
    return render_template('procurar_grupo.html', admin = admin , descricao_funcao = funcoes)

@app.route('/editar_grupo_template', methods =['GET', 'POST'])
def editar_grupo_template():
    # POST request
    msg = ''
    funcoes = session.get('functions')
    if request.method == 'POST':
        grupos = request.get_json()
        for linha in grupos.items():
            arr = linha[1]
        print(arr)
        return render_template('editar_grupo.html', msg = msg, grupo = arr, descricao_funcao = funcoes)

@app.route('/editar_grupo', methods =['GET', 'POST'])
def editar_grupo():
    # POST request
    msg = ''
    funcoes = session.get('functions')
    if request.method == 'POST' and 'nome' in request.form:
        nome = request.form['nome']
        grupo_nome = request.form['grupo']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT nome FROM grupos WHERE nome = %s', (nome, ))
        result = cursor.fetchone()
        if (result == None):
            print("Foi")
            cursor.execute("UPDATE grupos SET nome = %s WHERE nome = %s", (nome, grupo_nome, ))
            mysql.connection.commit()
            msg = 'nome do grupo alterado com sucesso!'
        elif():
            msg = 'Esse nome para grupo já existe. Tente outro'
    return render_template('procurar_grupo.html', msg = msg, descricao_funcao = funcoes)
        
    
@app.route('/procurar_deletar_grupo_template/<string:admin>', methods =['GET', 'POST'])
def procurar_deletar_grupo_template(admin):
    funcoes = session.get('functions')
    return render_template('deletar_grupo.html', admin = admin , descricao_funcao = funcoes)

@app.route('/deletar_grupo', methods =['GET', 'POST'])
def deletar_grupo():
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
    
@app.route('/procurar_banir_usuario_template/<string:admin>', methods =['GET', 'POST'])
def procurar_banir_usuario_template(admin):
    funcoes = session.get('functions')
    return render_template('banir_usuario.html', admin = admin , descricao_funcao = funcoes)

@app.route('/procurar_editar_usuario_template/<string:admin>', methods =['GET', 'POST'])
def procurar_editar_usuario_template(admin):
    funcoes = session.get('functions')
    return render_template('procurar_usuario.html', admin = admin , descricao_funcao = funcoes)

@app.route('/editar_usuario_template', methods =['GET', 'POST'])
def editar_usuario_template():
    # POST request
    msg = ''
    funcoes = session.get('functions')
    if request.method == 'POST':
        usuarios = request.get_json()
        for linha in usuarios.items():
            arr = linha[1]
        print(arr)
        return render_template('editar_usuario.html', msg = msg, usuario = arr, descricao_funcao = funcoes)
    
@app.route('/editar_usuario', methods =['GET', 'POST'])
def editar_usuario():
    # POST request
    msg = ''
    funcoes = session.get('functions')
    if request.method == 'POST' and 'nome' in request.form:
        nome = request.form['nome']
        usuario_nome = request.form['usuario']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT nome FROM usuarios WHERE nome = %s', (nome, ))
        result = cursor.fetchone()
        if (result == None):
            cursor.execute("UPDATE usuarios SET nome = %s WHERE nome = %s", (nome, usuario_nome, ))
            mysql.connection.commit()
            msg = 'nome do usuario alterado com sucesso!'
        else:
            msg = 'Esse nome para usuario já existe. Tente outro'
    return render_template('procurar_usuario.html', msg = msg, descricao_funcao = funcoes)

@app.route('/banir_usuario', methods =['GET', 'POST'])
def banir_usuario():
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
            value_iterator_email = iter(email_usuario)
            email_usuario = next(value_iterator_email)
            cursor.execute("INSERT INTO banidos(id_administrador, email) VALUES (%s, %s)", (id_admin, email_usuario))
            mysql.connection.commit()
            print("ID ADMIN",type(id_admin))
            sql = ("DELETE FROM usuarios WHERE nome = %s")
            cursor.execute(sql, (item, ))
            mysql.connection.commit()
            msg = 'Usuário(s) banido(s) com sucesso!'
        #return 'Sucesss', 200
    return render_template('banir_usuario.html', msg = msg) and 'Sucesss', 200
        

@app.route('/procurar_entrar_grupo_template/<string:usuario>', methods =['GET', 'POST'])
def procurar_entrar_grupo_template(usuario):
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

@app.route('/entrar_grupo', methods =['GET', 'POST'])
def entrar_grupo():
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
            print("IDS GRUPOS:", ids_grupo_existe)
            cursor.execute("SELECT id_grupo FROM grupos where nome = %s", (item, ))
            id_grupo = cursor.fetchone()
            value_iterator_id = iter(id_grupo)
            id_grupo = next(value_iterator_id)
            print("ID GRUPO:", id_grupo)
            flag = 0
            for i in ids_grupo_existe:
                print("IS:", i[0])
                if i[0] == id_grupo:
                    print("Não pode!")
                    msg = 'Usuário já faz parte do grupo!'
                    flag = 1
                    print("PODE!")
            if flag == 0:
                cursor.execute("INSERT INTO grupos_usuarios(id_grupo, id_usuario) VALUES (%s, %s)", (id_grupo, id_usuario))
                mysql.connection.commit()
                msg = 'Usuário entrou com sucesso!'
        #return 'Sucesss', 200
    return render_template('entrar_grupo.html', msg = msg) and 'Sucesss', 200

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

@app.route('/procurar_grupo', methods =['GET', 'POST'])
def procurar_grupo():
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


@app.route('/mostrar_grupos', methods =['GET', 'POST'])
def mostrar_grupos():
    
    cursor = mysql.connection.cursor()
    id_usuario = session['id']
    cursor.execute("SELECT id_grupo FROM grupos_usuarios where id_usuario = %s", (id_usuario, ))
    result_grupos = cursor.fetchall()
    u = []
    for grupo in result_grupos:
        print(type(grupo))
        cursor.execute("SELECT nome FROM grupos where id_grupo = %s", (grupo, ))
        nome = cursor.fetchone()
        u.append(nome)
    return jsonify(u)

@app.route('/procurar_adicionar_usuarios_template/<string:usuario>', methods =['GET', 'POST'])
def procurar_adicionar_usuarios_template(usuario):
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

@app.route('/adicionar_usuario', methods =['GET', 'POST'])
def adicionar_usuario():
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

@app.route('/desfazer_amizade', methods =['GET', 'POST'])
def desfazer_amizade():
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

@app.route('/procurar_usuario', methods =['GET', 'POST'])
def procurar_usuario():
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

@app.route('/mostrar_amigos', methods =['GET', 'POST'])
def mostrar_amigos():
    
    cursor = mysql.connection.cursor()
    id_usuario1 = session['id']
    cursor.execute("SELECT id_usuario2 FROM amigos where id_usuario1 = %s", (id_usuario1, ))
    result_amigos = cursor.fetchall()
    u = []
    for user in result_amigos:
        print(type(user))
        cursor.execute("SELECT nome FROM usuarios where id_usuario = %s", (user, ))
        nome = cursor.fetchone()
        u.append(nome)
    return jsonify(u)

##  Postagens_administrdor  ##

@app.route('/procurar_postagem_administrador', methods =['GET', 'POST'])
def procurar_postagem_administrador():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT descricao FROM postagens_administradores order by criado")
    result_postagem = cursor.fetchall()
    cursor.execute("SELECT id_administrador FROM postagens_administradores order by criado")
    result_administrador = cursor.fetchall()
    u = []
    for user in result_administrador:
        print(type(user))
        cursor.execute("SELECT nome FROM administradores where id_administrador = %s", (user, ))
        nome = cursor.fetchall()
        u.append(nome)
    r = []
    result = list(result_postagem)
    for i in range(len(result_administrador)):
        r.append(u[i]+result[i])
    return jsonify(r)

@app.route('/adicionar_postagens_administrador_template/<string:admin>', methods =['GET', 'POST'])
def adicionar_postagens_administrador_template(admin):
    funcionalidades = session['functions']
    id_administrador = session["id"]
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT foto_de_perfil FROM administradores where id_administrador = %s", (id_administrador, ))
    foto_perfil = cursor.fetchone()
    foto_perfil = foto_perfil[0]
    if foto_perfil:
        print("AQUI")
        reultado = 'contem'
    else:
        reultado = "vazio"
    return render_template('adicionar_postagens_administrador.html', admin = admin, foto_perfil = foto_perfil, descricao_funcao = funcionalidades, resultado=reultado)

@app.route('/adicionar_postagens_administrador', methods =['GET', 'POST'])
def adicionar_postagens_administrador():
    msg = ''  
    if request.method == 'POST' and 'descricao' in request.form:
        descricao = request.form['descricao']
        cursor = mysql.connection.cursor()
        
        cursor.execute("INSERT INTO postagens_administradores(id_administrador, descricao) VALUES(%s, %s)", (session['id'], descricao, ))
        mysql.connection.commit()
        msg = 'Postagem adicionada com sucesso'
    elif request.method == 'POST':
        msg = 'Por favor, não poste nada em branco!'
    return render_template('adicionar_postagens_administrador.html', msg = mostrar_amigos)

## Postagens_usuarios ##

@app.route('/procurar_postagem', methods =['GET', 'POST'])
def procurar_postagem():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT descricao FROM postagens_usuarios order by criado")
    result_postagem = cursor.fetchall()
    cursor.execute("SELECT id_usuario FROM postagens_usuarios order by criado")
    result_usuario = cursor.fetchall()
    u = []
    for user in result_usuario:
        print(type(user))
        cursor.execute("SELECT nome FROM usuarios where id_usuario = %s", (user, ))
        nome = cursor.fetchall()
        u.append(nome)
    r = []
    result = list(result_postagem)
    for i in range(len(result_usuario)):
        r.append(u[i]+result[i])
    return jsonify(r)

@app.route('/adicionar_postagens_template/<string:usuario>', methods =['GET', 'POST'])
def adicionar_postagens_template(usuario):
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

@app.route('/adicionar_postagens', methods =['GET', 'POST'])
def adicionar_postagens():
    msg = ''
    if request.method == 'POST' and 'descricao' in request.form:
        descricao = request.form['descricao']
        cursor = mysql.connection.cursor()
        
        cursor.execute("INSERT INTO postagens_usuarios(id_usuario, descricao) VALUES(%s, %s)", (session['id'], descricao, ))
        mysql.connection.commit()
        msg = 'Postagem adicionada com sucesso'
    elif request.method == 'POST':
        msg = 'Por favor, não poste nada em branco!'
    return render_template('adicionar_postagens.html', msg = msg)



## Upload de imagens ##

@app.route('/upload_form')
def upload_form():
    id_usuario = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT foto_de_perfil FROM usuarios where id_usuario = %s", (id_usuario, ))
    foto_perfil = cursor.fetchone()
    # foto_perfil = foto_perfil[0]
    print("FOTO DE PERFIL", foto_perfil)
    if foto_perfil:
        foto_perfil = foto_perfil.decode('utf-8')
        result = "contem"
    else:
        result = "vazio"
    return render_template('upload.html', foto_perfil = foto_perfil, resultado = result)

@app.route('/upload_de_imagem', methods=['POST'])
def upload_de_imagem():
    id = session['id']
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
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
        flash('Image successfully uploaded and displayed below')
        return render_template('upload.html', foto_perfil=encoded_img_data.decode('utf-8'), tipo_usuario = tipo_usuario)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
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
    # return redirect(url_for('static', foto_perfil="/static/uploads/img_default.png"), code=301)


if __name__ == "__main__":
  app.run(debug = True)