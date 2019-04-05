#!/usr/bin/env python

# Rumah Sahaja backend

import jwt
import hashlib
import datetime
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
app.config.from_pyfile('rs.cfg')

__DEBUG__ = True
__FrontEndURL__ = "http://localhost:3000"

# set resources and origins access
CORS(app, resources={r"/*": {"origins": __FrontEndURL__}})

db = SQLAlchemy(app)

# MODEL ######################################################################################################################

class Profile(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  phone = db.Column(db.String(50))
  email = db.Column(db.String(50))
  address = db.Column(db.Text)
  about = db.Column(db.Text)
  vision = db.Column(db.Text)
  mission = db.Column(db.Text)
  link = db.Column(db.Text)
  created_at = db.Column(db.DateTime)
  updated_at = db.Column(db.DateTime)

class News(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100))
  content = db.Column(db.Text)
  created_at = db.Column(db.DateTime)
  updated_at = db.Column(db.DateTime)
  images = db.Column(db.Text)
  images_caption = db.Column(db.Text)

class Donation(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  phone = db.Column(db.String(50))
  email = db.Column(db.String(50))
  amount = db.Column(db.Integer)
  receipt = db.Column(db.Text)
  created_at = db.Column(db.DateTime)

# TOKEN ######################################################################################################################

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None

    if 'X-Access-Token' in request.headers:
      token = request.headers['X-Access-Token']

    if not token:
      return jsonify({'message' : 'Token required!'}), 401

    try: 
      data = jwt.decode(token, app.config['SECRET_KEY'])
      verified = data['verified']
    except:
      return jsonify({'message' : 'Token is invalid!'}), 401

    return f(verified, *args, **kwargs)

  return decorated

# LOGIN ######################################################################################################################

@app.route('/login')
def login():
  auth = request.authorization

  if not auth or not auth.username or not auth.password:
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

  m = hashlib.md5()
  m.update(auth.password)

  if app.config['ADMIN_USERNAME'] == auth.username and app.config['ADMIN_PASSWORD'] == m.hexdigest():
    token = jwt.encode({'verified': True, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')})

  return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


# API PROFILE ################################################################################################################

@app.route('/profile', methods=['GET'])
def get_profile():
  profile = Profile.query.first()
  data = jsonify({
    'name': profile.name,
    'phone': profile.phone,
    'email': profile.email,
    'address': profile.address,
    'about': profile.about,
    'vision': profile.vision,
    'mission': profile.mission,
    'link': profile.link
  })
  return data

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile():
  profile = Profile.query.first()
  data = request.get_json()
  profile.name = data['name']
  profile.phone = data['phone']
  profile.email = data['email']
  profile.address = data['address']
  profile.about = data['about']
  profile.vision = data['vision']
  profile.mission = data['mission']
  profile.link = data['link']
  profile.updated_at = datetime.datetime.now()
  db.session.commit()
  return jsonify({ 'status': 200, 'message': 'update success' })

@app.route('/profile', methods=['POST'])
@token_required
def create_profile():
  data = request.get_json()
  news = Profile(name=data['name'],
                 phone=data['phone'],
                 email=data['email'],
                 address=data['address'],
                 about=data['about'],
                 vision=data['vision'],
                 mission=data['mission'],
                 link=data['link'],
                 created_at=datetime.datetime.now())
  db.session.add(news)
  db.session.commit()
  return jsonify({ 'status': 201, 'message': 'create success'})

# API News ####################################################################################################################

@app.route('/news', methods=['GET'])
def get_all_news():
  news = News.query.all()
  def convert_to_json(object):
    return {
      'id': object.id,
      'title': object.title,
      'content': object.content,
      'created_at': object.created_at,
      'updated_at': object.updated_at,
      'images': object.images,
      'images_caption': object.images_caption
    }
  data = jsonify(list(map(convert_to_json, news)))
  return data

@app.route('/news', methods=['POST'])
@token_required
def create_news():
  data = request.get_json()
  news = News(title=data['title'],
              content=data['content'],
              created_at=datetime.datetime.now(),
              images=data['images'],
              images_caption=data['images_caption'])
  db.session.add(news)
  db.session.commit()
  return jsonify({ 'status': 201, 'message': 'create success'})

@app.route('/news', methods=['PUT'])
@token_required
def update_news():
  data = request.get_json()
  news_id = data['id']
  news = News.query.filter_by(id=news_id).first()
  news.title = data['title']
  news.content = data['content']
  news.updated_at = datetime.datetime.now()
  news.images = data['images']
  news.images_caption = data['images_caption']
  db.session.commit()
  return jsonify({ 'status': 200, 'message': 'update success' })

@app.route('/news/<news_id>', methods=['DELETE'])
@token_required
def delete_news(news_id):
  news = News.query.filter_by(id=news_id).first()
  db.session.delete(news)
  db.session.commit()
  return jsonify({ 'status': 200, 'message': 'delete success'})

# API Donation #################################################################################################################

@app.route('/donation', methods=['GET'])
@token_required
def get_all_donations():
  donation = Donation.query.all()
  def convert_to_json(object):
    return {
      'id': object.id,
      'name': object.name,
      'phone': object.phone,
      'email': object.email,
      'amount': object.amount,
      'receipt': object.receipt,
      'created_at': object.created_at
    }
  data = jsonify(list(map(convert_to_json, donation)))
  return data

@app.route('/donation', methods=['POST'])
@token_required
def create_donation():
  data = request.get_json()
  donation = Donation(name=data['name'],
                      phone=data['phone'],
                      email=data['email'],
                      amount=data['amount'],
                      receipt=data['receipt'],
                      created_at=datetime.datetime.now())
  db.session.add(donation)
  db.session.commit()
  return jsonify({ 'status': 201, 'message': 'create success'})

# Main #################################################################################################################

if __name__ == '__main__':
  app.run(debug=__DEBUG__)