from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TextClause, create_engine, text
import random
from faker import Faker
from flask import Flask, jsonify, render_template

db_string = "postgresql://root:root@localhost:5432/postgres"

engine = create_engine(db_string)

app = Flask(__name__)

@app.route("/user", methods=["GET"])
def get_users():
    users = run_sql_with_results(text("SELECT * FROM users"))
    data=[]
    for row in users:
        user = {
            "id": row[0],
            "firstname": row[1],
            "lastname": row[2],
            "age": row[3],
            "email": row[4],
            "job": row[5]
        }
        data.append(user)
    return jsonify(data)

create_user_table_sql = text("""
CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    age INTEGER,
    email VARCHAR(255) UNIQUE NOT NULL,
    job VARCHAR(255)
)
""")

create_application_table_sql = text("""
CREATE TABLE IF NOT EXISTS Application (
    id SERIAL PRIMARY KEY,
    appname VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    lastconnection TIMESTAMP,
    user_id INTEGER REFERENCES Users(id)
)
""")


def run_sql(query: TextClause):
    with engine.connect() as connection:
        trans = connection.begin() 
        connection.execute(query) 
        trans.commit() 

def run_sql_with_results(query: TextClause):
    with engine.connect() as connection:
        trans = connection.begin() 
        result = connection.execute(query) 
        trans.commit()
        return result


fake= Faker()
def populate_table():
    apps = ['Facebook', 'Twitter', 'Instagram', 'LinkedIn', 'Snapchat']
    for i in range (100):
        firstname= fake.first_name()
        lastname=fake.last_name()
        age= random.randrange(18,90)
        email=fake.email()
        job=fake.job().replace("'", "")
        insert_statement = text(f"""
        INSERT INTO Users (firstname, lastname, age, email, job) 
        VALUES ('{firstname}', '{lastname}', '{age}', '{email}', '{job}')
        RETURNING id
        """)
        # Récupérer l'id
        user_id = run_sql_with_results(insert_statement).scalar()
        

        #get current 
        num_apps = random.randrange(1,5)
        for i in range(num_apps):
            appname = random.choice(apps)
            username= fake.user_name()
            lastconnection = datetime.now()
            insert_statement_app = text(f"""
            INSERT INTO Application (appname, username, lastconnection, user_id) 
            VALUES ('{appname}', '{username}', '{lastconnection}', '{user_id}')
            """)
            run_sql(insert_statement_app)


##### Partie 2 

app2 = Flask(__name__)


app2.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://root:root@localhost:5432/postgres"
app2.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app2)

# Récupération des données 
@app2.route("/user2", methods=["GET"])
def get_users2():
    users2 = run_sql_with_results(text("SELECT * FROM users2"))
    data=[]
    for row in users2:
        user = {
            "id": row[0],
            "firstname": row[1],
            "lastname": row[2],
            "age": row[3],
            "email": row[4],
            "job": row[5]
        }
        data.append(user)
    return jsonify(data)

### Ajout de l'API Web 
@app2.route("/home", methods=["GET"])
def home():
    users = Users2.query.all()
    return render_template("home.html", users=users)


class Users2(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    age = db.Column(db.Integer())
    email = db.Column(db.String(100))
    job = db.Column(db.String(100))

    def __init__(self, firstname,lastname, age, email, job):
        self.firstname = firstname
        self.lastname = lastname
        self.age = age
        self.email = email
        self.job = job

class Application2(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    appname = db.Column(db.String(100))
    username = db.Column(db.String(100))
    lastconnection = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users2.id'))

    def __init__(self, appname,username,lastconnection,  user_id):
        self.appname = appname
        self.username = username
        self.lastconnection = lastconnection
        self.user_id = user_id

### Ajout des valeurs dans les tables

fake= Faker()
def populate_table2():
    apps = ['Facebook', 'Twitter', 'Instagram', 'LinkedIn', 'Snapchat']
    with app2.app_context():
    # Ajout de données à la table Users2
        for i in range(100):
            firstname = fake.first_name()
            lastname = fake.last_name()
            age = random.randint(18, 90)
            email = fake.email()
            job = fake.job().replace("'", "")
            
            # Création d'une instance Users2 avec les valeurs générées
            new_user = Users2(firstname=firstname, lastname=lastname, age=age, email=email, job=job)
            
            # Ajout de l'instance à la session SQLAlchemy
            db.session.add(new_user)
        db.session.commit()
    # Ajout de données à la table Application2
    with app2.app_context():
        all_users = Users2.query.all()  # Récupération de tous les utilisateurs créés
        for user in all_users:
            num_apps = random.randint(1, 5)  # Nombre d'applications pour chaque utilisateur
            for _ in range(num_apps):
                appname = random.choice(apps)
                username = fake.user_name()
                lastconnection = datetime.now()
                user_id = user.id
                
                # Création d'une instance Application2 avec les valeurs générées et l'utilisateur associé
                new_app = Application2(appname=appname, username=username, lastconnection=lastconnection, user_id=user_id)
                
                # Ajout de l'instance à la session SQLAlchemy
                
                db.session.add(new_app)
        
        # Commit des changements à la base de données
        db.session.commit()
        



if __name__ =='__main__':
    # #Create user table 
    # run_sql(create_user_table_sql)
    # #Create Application table
    # run_sql(create_application_table_sql)
    # # populate_table()
    # app.run(host="0.0.0.0", port=8081)
    with app2.app_context():
        db.drop_all()
        db.create_all()  
    populate_table2()
    app2.run(host="0.0.0.0", port=8082) 

