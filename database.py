
import mysql.connector as connector

config = {
  'user': 'root',
  'password': 'L@g0n1c0',
  'host': 'localhost',
  'database': 'rede_social' # tirar para estabelecer conexao, colocar para acessar o baanco de dados
}

db = connector.connect(**config)
cursor = db.cursor()