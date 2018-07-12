from sqlalchemy import create_engine

# db = create_engine('mysql://root:root@db:8000/db')

engine = create_engine(
      "mysql+pymysql://root:root@db/waze?host=db?port=3306")
