import os

from flask import Flask, request, render_template, flash
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists

#Start Flask app and MySQL session
app = Flask(__name__)
app.secret_key = 'thisisasecret'
engine = create_engine()
Base = declarative_base()
Session = sessionmaker(bind = engine)
Session.configure(bind = engine)
session = Session()

#User class which contains id, name, and age
class User(Base):

    __tablename__ = 'people'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    age = Column(Integer)
    
    #If this class is printed, display this text
    def __repr__(self):
        return "User(id = '%i', name = '%s', age = '%i')" % (self.id, self.name, self.age)

#Index page
@app.route('/', methods = ['GET'])
def indexpage():
    return render_template('index.html')

#Search page
@app.route('/search', methods = ['GET', 'POST'])
def searchpage():

    output = None

    #Queries for results based on input; input won't be empty
    if request.method == 'POST':
        if 'SBName' in request.form:
            output = searchByName(request.form['SBName'])
        elif 'SBAge' in request.form:
            output = searchByAge(request.form['SBAge'])
        elif 'SBID' in request.form:
            output = searchByID(request.form['SBID'])
        
    #Dummy iterator for GET or None outputs
    if output is None:
        output = []

    return render_template('search.html', users = output)

#Insert page
@app.route('/insert', methods = ['GET', 'POST'])
def addpage():
    
    if request.method == 'POST':
        name = request.form['AddName']
        age = request.form['AddAge']
        id = addUser(name, age)
        flash('User %s, Age %s was successfully added with the ID of %i' % (name, age, id))

    return render_template('insert.html')

#Remove page
@app.route('/remove', methods = ['GET', 'POST'])
def removepage():

    if request.method == 'POST':
        id = request.form['RemoveID']
        removeUser(id)
        
    return render_template('remove.html')

#View database page
@app.route('/viewall', methods = ['GET'])
def viewallpage():

    return render_template('viewall.html', users = session.query(User))

#Search for users by name and yields each valid outputs
def searchByName(x):
 
    if session.query(exists().where(User.name == x)).scalar():
        for instance in session.query(User).filter(User.name == x):
            yield instance

#Search for users by age and yields each valid outputs
def searchByAge(x):

    for instance in session.query(User).filter(User.age == x):
        yield instance

#Search for users by id and returns the only valid output
def searchByID(x):

    x = int(x)
    if session.query(exists().where(User.id == x)).scalar():
        return session.query(User).filter(User.id == x)
    
#Inserts new user into database
def addUser(x, y):

    session.add(User(id = None, name = x, age = y))
    session.commit()
    nextID = session.query(User).order_by(User.id.desc()).limit(1)
    nextID = nextID[::-1]
    nextID = nextID[0].id

    return nextID

#Based on ID, removes user base from database
def removeUser(x):

    x = int(x)
    if session.query(exists().where(User.id == x)).scalar():
        session.delete(session.query(User).get(x))
        flash('User with the ID of %s has been removed from the database' % (x))
    else:
        flash('No such user with the ID of %s' % (x))

if __name__ == '__main__':
    app.run(debug = True)