import psycopg2
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_login import UserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NKMnk360@localhost/auth'
app.config['SECRET_KEY'] = '12345678'
db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


# -----------------------------DATABASE-----------------------------------------

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def get_id(self):
        return (self.user_id)
    


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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()

    if(user):
        login_user(user)
        return jsonify({'success': True ,'message' : 'Login successful'})
    else:
        return jsonify({'success': False , 'message ' : 'Invalid credentials'}), 401



@app.route('/contacts', methods=['GET'])
@login_required
def contacts():

    if(current_user):
        user_id = current_user.user_id

        contacts = Contact.query.filter_by(user_id=current_user.user_id).all()

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



@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logout successful'})
    


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return jsonify({'success': True, 'user_id': current_user.user_id, 'username': current_user.username})






if __name__ == '__main__':
    app.run(debug=True)