
import mysql.connector as connector

config = {
  'user': 'admin',
  'password': '12345678',
  'host': 'localhost',
  'database': 'rede_social' # tirar para estabelecer conexao, colocar para acessar o baanco de dados
}

db = connector.connect(**config)
cursor = db.cursor()