import psycopg2
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NKMnk360@localhost/auth'
db = SQLAlchemy(app)


# -----------------------------DATABASE-----------------------------------------

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Contact(db.Model):
    __tablename__ = 'contacts'
    contact_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    contact_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

# -----------------------------DATABASE--------------------------------------------




@app.route('/')
def hello() :
    return 'Hello, Starting......'



@app.route('/login', methods=['GET'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()

    if(user):
        return jsonify({'message' : 'Login successful'})
    else:
        return jsonify({'message ' : 'Invalid credentials'})



@app.route('/contacts', methods=['GET'])
def contacts():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    

    if(user):
        user_id = user.user_id

        contacts = Contact.query.filter_by(user_id=user.user_id).all()

        if contacts:
            contacts_list = [
                {
                    'contact_id': contact.contact_id,
                    'contact_name': contact.contact_name,
                    'phone_number': contact.phone_number
                }
                for contact in contacts
            ]
            return jsonify({'contacts' : contacts_list})

        else:
            return jsonify({'message' : 'No contacts found for the user'}), 404

    else:
        return jsonify({'message ' : 'User not found'}), 404


    







if __name__ == '__main__':
    app.run(debug=True)