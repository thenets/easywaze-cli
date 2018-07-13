from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey

# SQLAlquemy tutorial at
# http://docs.sqlalchemy.org/en/latest/core/tutorial.html

#### IMPORTANT
# Create a database called "waze" before continue!

# Create engine
engine = create_engine("mysql+pymysql://root:root@db/waze?host=db?port=3306")

# Try to create table if not exist
metadata = MetaData()
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255)),
    Column('fullname', String(255)),
)
addresses = Table('addresses', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', None, ForeignKey('users.id')),
    Column('email_address', String(255), nullable=False)
)
metadata.create_all(engine)

# Create new query
ins = users.insert().values(name='jack', fullname='Jack Jones')

# DEBUG show the SQL query
# print(str(ins))
# print(str(ins.compile().params))

# Create a connector
conn = engine.connect()

# Execute the insert query
result = conn.execute(ins)

# DEBUG read result
print(result)
print(result.inserted_primary_key)
