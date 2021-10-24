
import mysql.connector as mysql

def criar_bd_tabelas():
  db = mysql.connect(
    host = "localhost",
    user = "admin",
    password = "12345678"
  )

  cursor = db.cursor()

  cursor.execute("CREATE DATABASE if not exists rede_social")
  print('banco de dados criado')
  # cursor.execute("SHOW DATABASES LIKE 'rede_social'")
  # database = cursor.fetchone() 
  
  # print(database)
  
  db = mysql.connect(
    host = "localhost",
    user = "admin",
    password = "12345678",
    database = "rede_social"
  )
  
  cursor = db.cursor()
  
  cursor.execute("CREATE TABLE IF NOT EXISTS administradores( id_administrador int(11) NOT NULL AUTO_INCREMENT, nome varchar(255) NOT NULL, senha varchar(255) NOT NULL, email varchar(255) NOT NULL UNIQUE,foto_de_perfil LONGBLOB ,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id_administrador))")
  cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id_usuario int(11) NOT NULL AUTO_INCREMENT,nome varchar(255) NOT NULL,senha varchar(255) NOT NULL,email varchar(255) NOT NULL UNIQUE,foto_de_perfil LONGBLOB ,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (id_usuario),CONSTRAINT UC_usuario UNIQUE (email))")
  cursor.execute("CREATE TABLE IF NOT EXISTS grupos (id_grupo int(11) NOT NULL AUTO_INCREMENT,nome varchar(255) NOT NULL UNIQUE,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (id_grupo))")
  cursor.execute("CREATE TABLE IF NOT EXISTS funcoes(id_funcao int(11) NOT NULL AUTO_INCREMENT,descricao varchar(255) NOT NULL UNIQUE,PRIMARY KEY (id_funcao))")
  cursor.execute("CREATE TABLE IF NOT EXISTS grupos_usuarios(id_grupo_usuario int(11) NOT NULL AUTO_INCREMENT,id_usuario int(11) NOT NULL,id_grupo int(11) NOT NULL,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (id_grupo_usuario),CONSTRAINT grupos_usuarios_fk_1 FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,CONSTRAINT grupos_usuarios_fk_2 FOREIGN KEY (id_grupo)REFERENCES grupos (id_grupo) ON DELETE CASCADE)")
  cursor.execute("CREATE TABLE IF NOT EXISTS amigos(id_amigos int(11) NOT NULL AUTO_INCREMENT,id_usuario1 int(11) NOT NULL,id_usuario2 int(11) NOT NULL,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (id_amigos),CONSTRAINT amigos_fk_1 FOREIGN KEY (id_usuario1)REFERENCES usuarios (id_usuario) ON DELETE CASCADE,CONSTRAINT amigos_fk_2 FOREIGN KEY (id_usuario2)REFERENCES usuarios (id_usuario) ON DELETE CASCADE)")
  cursor.execute("CREATE TABLE IF NOT EXISTS banidos(id_banidos int(11) NOT NULL AUTO_INCREMENT,id_administrador int(11) NOT NULL, email varchar(255) NOT NULL UNIQUE ,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (id_banidos),CONSTRAINT banidos_fk_2 FOREIGN KEY (id_administrador)REFERENCES administradores (id_administrador) ON DELETE CASCADE)")
  cursor.execute("CREATE TABLE IF NOT EXISTS funcoes_administradores(id_funcao_administrador int(11) NOT NULL AUTO_INCREMENT,id_funcao int(11) NOT NULL,id_administrador int(11) NOT NULL,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (id_funcao_administrador),CONSTRAINT funcoes_fk_1 FOREIGN KEY (id_administrador)REFERENCES administradores (id_administrador) ON DELETE CASCADE,CONSTRAINT funcoes_fk_2 FOREIGN KEY (id_funcao)REFERENCES funcoes (id_funcao) ON DELETE CASCADE)")
  cursor.execute("CREATE TABLE IF NOT EXISTS postagens_usuarios(id_postagens_usuarios int(11) NOT NULL AUTO_INCREMENT,id_usuario int(11) NOT NULL,descricao varchar(255) NOT NULL,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (id_postagens_usuarios),CONSTRAINT postagens_usuarios_fk FOREIGN KEY (id_usuario)REFERENCES usuarios (id_usuario) ON DELETE CASCADE)")
  cursor.execute("CREATE TABLE IF NOT EXISTS postagens_administradores(id_postagens_administradores int(11) NOT NULL AUTO_INCREMENT,id_administrador int(11) NOT NULL,descricao varchar(255) NOT NULL,criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (id_postagens_administradores),CONSTRAINT postagens_administradores_fk FOREIGN KEY (id_administrador)REFERENCES administradores (id_administrador) ON DELETE CASCADE)")  
  print('tabelas criadas')
  
  # cursor.execute("SHOW TABLES")

  # tables = cursor.fetchall() 

  # for table in tables:
  #   print(table)
  
def preencher_bd_tabelas():
  db = mysql.connect(
    host = "localhost",
    user = "admin",
    password = "12345678",
    database = "rede_social"
  )
  
  cursor = db.cursor()
  
  sql = "INSERT INTO administradores (nome, senha, email) VALUES (%s, %s, %s)"
  val = [
    ('Andre','senhaandre','andre@gmail.com'),
    ('Rafael','senharafael','rafael@gmail.com'),
    ('Jorge','senhajorge','jorge@gmail.com'),
    ('Maristela','senhamaristela','maristela@gmail.com'),
    ('Ruben','senharuben','ruben@gmail.com'),
  ]
  cursor.executemany(sql, val)
  print("inserido em administradores")
  sql = "INSERT INTO usuarios (nome, senha, email) VALUES (%s, %s, %s)"
  val = [
    ('Carlos','senhacarlos','carlos@gmail.com'),
    ('Roger','senharoger','roger@gmail.com'),
    ('Junior','senhajunior','junior@gmail.com'),
    ('Maria','senhamaria','maria@gmail.com'),
    ('Rita','senharita','rita@gmail.com'),
  ]
  cursor.executemany(sql, val)
  print("inserido em usuarios")
  cursor.execute("INSERT INTO grupos (nome) VALUES ('Alunos')")
  cursor.execute("INSERT INTO grupos (nome) VALUES ('Professores')")
  cursor.execute("INSERT INTO grupos (nome) VALUES ('Solteiros')")
  cursor.execute("INSERT INTO grupos (nome) VALUES ('Churrasco')")
  cursor.execute("INSERT INTO grupos (nome) VALUES ('Futebol')")
  # sql = "INSERT INTO grupos (nome) VALUES (%s)"
  # val = [
  #   ('Alunos'),
  #   ('Professores'),
  #   ('Solteiros'),
  #   ('Churrasco'),
  #   ('Futebol'),
  # ]
  # cursor.executemany(sql, val)
  cursor.execute("INSERT INTO funcoes (descricao) VALUES ('Criar Grupos')")
  cursor.execute("INSERT INTO funcoes (descricao) VALUES ('Editar Grupos')")
  cursor.execute("INSERT INTO funcoes (descricao) VALUES ('Editar Usuarios')")
  cursor.execute("INSERT INTO funcoes (descricao) VALUES ('Deletar Grupos')")
  cursor.execute("INSERT INTO funcoes (descricao) VALUES ('Banir Usuarios')")
  sql = "INSERT INTO postagens_usuarios (id_usuario, descricao) VALUES (%s, %s)"
  val = [
    (1,'Hoje o dia foi belo'),
    (2,'#Lula2022'),
    (1,'Que cheiro de terra molhada'),
    (1,'#Bolsonaro2022'),
    (3,'Chuva!!!!'),
  ]
  cursor.executemany(sql, val)
  sql = "INSERT INTO postagens_administradores (id_administrador, descricao) VALUES (%s, %s)"
  val = [
    (1,'Pode banir ele'),
    (2,'Tenha dó!'),
    (1,'Por favor, sem palavras chulas'),
    (1,'Eu sei onde você mora'),
    (3,'Fica ligado!'),
  ]
  cursor.executemany(sql, val)
  sql = "INSERT INTO grupos_usuarios (id_usuario, id_grupo) VALUES (%s, %s)"
  val = [
    (1,2),
    (3,4),
    (4,2),
    (5,3),
    (1,4),
  ]
  cursor.executemany(sql, val)
  sql = "INSERT INTO amigos (id_usuario1, id_usuario2) VALUES (%s, %s)"
  val = [
    (1,4),
    (1,2),
    (2,4),
    (5,1),
    (3,2),
  ]
  cursor.executemany(sql, val)
  sql = "INSERT INTO funcoes_administradores (id_funcao, id_administrador) VALUES (%s, %s)"
  val = [
    (1,2),
    (2,4),
    (4,5),
    (3,3),
    (5,1),
  ]
  cursor.executemany(sql, val)
  # INSERIR NA TABELA BANIDOS
  # sql = "INSERT INTO banidos (id_funcao, id_administrador) VALUES (%s, %s)"
  # val = [
  #   (1,2),
  #   (1,4),
  #   (2,5),
  #   (5,3),
  #   (2,1),
  # ]
  # cursor.executemany(sql, val)

  db.commit()
  
  

def main():
  # db = mysql.connect(
  #   host = "localhost",
  #   user = "admin",
  #   password = "12345678",
  # )
  # cursor = db.cursor()
  # sql = "DROP DATABASE rede_social"
  # cursor.execute(sql)
  criar_bd_tabelas()
  preencher_bd_tabelas()
if __name__ == "__main__":
  main()