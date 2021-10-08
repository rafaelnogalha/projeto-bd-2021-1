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
CREATE TABLE IF NOT EXISTS grupos_usuarios(
    id_grupo_usuario int(11) NOT NULL AUTO_INCREMENT,
    id_usuario int(11) NOT NULL,
    id_grupo int(11) NOT NULL,
    criado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_grupo_usuario),
    CONSTRAINT grupo_usuario_fk_1 FOREIGN KEY (id_usuario)
      REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    CONSTRAINT grupo_usuario_fk_2 FOREIGN KEY (id_grupo)
      REFERENCES grupos (id_grupo) ON DELETE CASCADE
);