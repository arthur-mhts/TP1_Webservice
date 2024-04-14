from sqlalchemy import create_engine, text

db_string = "postgresql://root:root@localhost:5432/postgres"

engine = create_engine(db_string)

create_table_User = text("""
CREATE TABLE IF NOT EXISTS User_T (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    age INTEGER,
    email VARCHAR(255) UNIQUE NOT NULL,
    job VARCHAR(255)
)
""")

create_table_Application = text("""
CREATE TABLE IF NOT EXISTS Application (
    id SERIAL PRIMARY KEY,
    appname VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    lastconnection TIMESTAMP,
    user_id INTEGER REFERENCES User_T(id)
)
""")

# insert_statement = text("""
#     INSERT INTO films (title, director, year) 
#     VALUES ('Doctor Strange', 'Scott Derrickson', '2016')
# """)

with engine.connect() as connection:
    trans = connection.begin() 
    connection.execute(create_table_User) 
    connection.execute(create_table_Application)
    #connection.execute(insert_statement)
    trans.commit()  
