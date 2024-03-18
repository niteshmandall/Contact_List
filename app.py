import psycopg2
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_login import UserMixin
import jwt 
from functools import wraps

secret_key = 'niteshnk123'

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    contact_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

# -----------------------------DATABASE--------------------------------------------

def ceate_token(user_id):
    payload = {'user_id': user_id}
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def verify_token(token):
    try: 
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None 

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')


        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        user_info = verify_token(token)
        if not user_info:
            return jsonify({'message' : 'Invalid Token'}), 401
        
        return func(*args, **kwargs)
    
    return wrapper


@app.route('/protected', methods=['GET'])
@jwt_required
def protected_route():
    return jsonify({'message': 'This is a protected route'})








@app.route('/')
def hello() :
    # return 'Hello, Starting......'
    return jsonify({'success': True ,'message' : 'Login successful'})


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    # ceate_token(user)

    if(user):
        login_user(user)
        if(current_user):
            user_id = current_user.user_id
            token = ceate_token(user_id)
        return jsonify({'success': True ,'message' : 'Login successful', 'token': token})
    else:
        return jsonify({'success': False , 'message ' : 'Invalid credentials'}), 401



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'User registered successfully'})


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


@app.route('/delete', methods=['DELETE'])
@login_required
def delete_user():
    if current_user:
        user_id = current_user.user_id

        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()

        logout_user

        return jsonify({ 'success' : True, 'message': 'User deleted successfully'})
    
    else:
        return jsonify({'success' : false, 'message' : 'User not fount' }), 404



@app.route('/update_password', methods=['POST'])
@login_required
def update_user():
    user = current_user

    current_password = request.json.get('current_password')
    new_password = request.json.get('new_password')

    if(user.password == current_password):
        user.password = new_password
        db.session.commit()
        return jsonify({ 'success' : 'New Password updated.'})
    else:
        return jsonify({ 'success': False, 'message': 'Incorrect current Password'})



@app.route('/add_conatact', methods=['POST', 'DELETE', 'PUT'])
@login_required
def contact():
    if request.method == 'POST':
        if current_user:
            user_id = current_user.user_id

            data = request.get_json()
            contact_name = data.get('contact_name')
            phone_number = data.get('phone_number')

            new_contact = Contact(user_id = user_id, contact_name=contact_name, phone_number=phone_number)
            db.session.add(new_contact)
            db.session.commit()

            return jsonify({ "success": True, 'message': "Contact added successfully"})
        else:
            return jsonify({ 'message': 'User not found'}), 404
    
    elif request.method == 'DELETE':
        if current_user:
            user_id = current_user.user_id

            data = request.get_json()
            contact_name = data.get('contact_name')
            phone_number = data.get('phone_number')

            contact = Contact.query.filter_by(contact_name=contact_name, phone_number=phone_number).first()

            if contact:
                db.session.delete(contact)
                db.session.commit()
                return jsonify({ "success": True, 'message': "Contact Deleted successfully"})
            else:
                return jsonify({ 'message': 'User not found'}), 404
            
    elif request.method == 'PUT':
        if current_user:
            user_id = current_user.user_id

            data = request.get_json()
            contact_name = data.get('contact_name')
            phone_number = data.get('phone_number')
            updated_number = data.get('new_number')

            contact = Contact.query.filter_by(contact_name=contact_name, phone_number=phone_number).first()

            if contact:
                contact.phone_number = updated_number
                # db.session.delete(contact)
                db.session.commit()
                return jsonify({ "success": True, 'message': "Contact Updated successfully"})
            else:
                return jsonify({ 'message': 'User not found'}), 404













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