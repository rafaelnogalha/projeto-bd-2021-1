CREATE DATABASE IF NOT EXISTS rede_social;

CREATE TABLE IF NOT EXISTS administradores(
  id_administrador int(11) NOT NULL AUTO_INCREMENT,
  nome varchar(255) NOT NULL,
  senha varchar(255) NOT NULL,
  email varchar(255) NOT NULL UNIQUE,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_administrador)
);
CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario int(11) NOT NULL AUTO_INCREMENT,
  nome varchar(255) NOT NULL,
  senha varchar(255) NOT NULL,
  email varchar(255) NOT NULL UNIQUE,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_usuario),
  CONSTRAINT UC_usuario UNIQUE (email)
);
CREATE TABLE IF NOT EXISTS grupos (
  id_grupo int(11) NOT NULL AUTO_INCREMENT,
  nome varchar(255) NOT NULL,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_grupo)
);
CREATE TABLE IF NOT EXISTS funcoes(
  id_funcao int(11) NOT NULL AUTO_INCREMENT,
  descricao varchar(255) NOT NULL UNIQUE,
  PRIMARY KEY (id_funcao)
);

CREATE TABLE IF NOT EXISTS postagens_usuarios(
  id_postagens_usuarios int(11) NOT NULL AUTO_INCREMENT,
  id_usuario int(11) NOT NULL,
  descricao varchar(255) NOT NULL,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_postagens_usuarios),
  CONSTRAINT postagens_fk FOREIGN KEY (id_usuario)
    REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS postagens_administradores(
  id_postagens_administradores int(11) NOT NULL AUTO_INCREMENT,
  id_administrador int(11) NOT NULL,
  descricao varchar(255) NOT NULL,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_postagens_administradores),
  CONSTRAINT postagens_fk FOREIGN KEY (id_administrador)
    REFERENCES administradores (id_administrador) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS grupos_usuarios(
  id_grupo_usuario int(11) NOT NULL AUTO_INCREMENT,
  id_usuario int(11) NOT NULL,
  id_grupo int(11) NOT NULL,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_grupo_usuario),
  CONSTRAINT grupos_usuarios_fk_1 FOREIGN KEY (id_usuario)
    REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
  CONSTRAINT grupos_usuarios_fk_2 FOREIGN KEY (id_grupo)
    REFERENCES grupos (id_grupo) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS amigos(
  id_amigos int(11) NOT NULL AUTO_INCREMENT,
  id_usuario1 int(11) NOT NULL,
  id_usuario2 int(11) NOT NULL,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_amigos),
  CONSTRAINT amigos_fk_1 FOREIGN KEY (id_usuario1)
    REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
  CONSTRAINT amigos_fk_2 FOREIGN KEY (id_usuario2)
    REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS banidos(
  id_banidos int(11) NOT NULL AUTO_INCREMENT,
  id_administrador int(11) NOT NULL,
  id_usuario int(11) NOT NULL,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_banidos),
  CONSTRAINT banidos_fk_1 FOREIGN KEY (id_usuario)
    REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
  CONSTRAINT banidos_fk_2 FOREIGN KEY (id_administrador)
    REFERENCES administradores (id_administrador) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS funcoes_administradores(
  id_funcao_administrador int(11) NOT NULL AUTO_INCREMENT,
  id_funcao int(11) NOT NULL,
  id_administrador int(11) NOT NULL,
  criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_funcao_administrador),
  CONSTRAINT funcoes_fk_1 FOREIGN KEY (id_administrador)
    REFERENCES administradores (id_administrador) ON DELETE CASCADE,
  CONSTRAINT funcoes_fk_2 FOREIGN KEY (id_funcao)
    REFERENCES funcoes (id_funcao) ON DELETE CASCADE
);

