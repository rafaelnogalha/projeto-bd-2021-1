from database import criar_bd_tabelas
import app 

def main():
  criar_bd_tabelas()
  app.main()
  
if __name__ == "__main__":
  main()