from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku
from passlib.hash import sha256_crypt
from datetime import datetime
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
heroku = Heroku(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
# --Database Models--


class Member(db.Model):
    __tablename__ = 'members'


id = db.Column(db.Integer, primary_key=True, autoincrement=True)
email = db.Column(db.String(255), unique=True, nullable=False)
username = db.Column(db.String(50), unique=True)
password_hash = db.Column(db.String(100))
firstname = db.Column(db.String(50), unique=False)
lastname = db.Column(db.String(50), unique=False)
registered_on = db.Column(db.DateTime, nullable=False)


class MemberSchema(ma.ModelSchema):
    class Meta:
        model = Member
        fields = ('id', 'username', 'email')


member_schema = MemberSchema(strict=True, only=('id', 'username'))
members_schema = MemberSchema(strict=True, many=True)
# --Views--


@app.route('/')
def index():
    return jsonify({'message': 'ok'}), 200
# list users


@app.route('/api/user', methods=['GET'])
def list_users():
    all_users = Member.query.all()
    result = members_schema.dump(all_users)
    return jsonify(result.data)
# get user


@app.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    user = Member.query.get(id)
    result = member_schema.dump(user)
    return jsonify(result.data)
# add user


@app.route('/api/user', methods=['POST'])
def add_user():
    email = request.json['email']
    username = request.json['username']
    password_hash = sha256_crypt.encrypt(request.json['password'])
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    new_user = Member(email=email, username=username, password_hash=password_hash,
                      firstname=firstname, lastname=lastname, registered_on=datetime.utcnow())
    try:
        db.session.add(new_user)
        db.session.commit()
        result = member_schema.dump(Member.query.get(new_user.id))
        return jsonify({'member': result.data})
    except:
        db.session.rollback()
        result = {'message': 'error'}
        return jsonify(result)
# update user


@app.route('/api/user/<int:id>', methods=['PUT'])
def update_user(id):
    user = Member.query.get(id)
    username = request.json['username']
    email = request.json['email']
    user.email = email
    user.username = username
    db.session.commit()
    return member_schema.jsonify(user)
# delete user


@app.route('/api/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = Member.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': '{} has been deleted'.format(user.username)})


if __name__ == '__main__':
    app.run()
