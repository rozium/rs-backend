#!/usr/bin/env python

# Rumah Sahaja backend
# created by um

import jwt
import hashlib
import datetime
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from models import Profile, News, Donation

app = Flask(__name__)

# set resources and origins access
CORS(app, resources={r"/login": {"origins": "http://localhost:3000"}, r"/public/*": {"origins": "*"}})

app.config.from_pyfile('rs.cfg')

db = SQLAlchemy(app)

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

@app.route('/test', methods=['GET'])
@token_required
def test(verified):
  return jsonify({'test': 'success'})

# API Profil

@app.route('/profil', methods=['GET'])
def get_profile():
  profile = Profile.query.first()
  data = jsonify({
    'name': profile.name,
    'phone': profile.phone,
    'address': profile.address,
    'vision': profile.vision,
    'mission': profile.mission,
    'link': profile.link
  })
  return data

@app.route('/profil', methods=['PUT'])
def update_profile():
  profile = Profile.query.first()
  data = request.get_json()
  profile.name = data['name']
  profile.phone = data['phone']
  profile.address = data['address']
  profile.vision = data['vision']
  profile.mission = data['mission']
  profile.link = data['link']
  db.session.commit()
  return jsonify({ 'status': 200, 'message': 'update success' })

# API News

@app.route('/news', methods=['GET'])
def get_all_news():
  news = News.query.all()
  def convert_to_json(object):
    return {
      'id': object.id,
      'title': object.title,
      'content': object.content,
      'created_at': object.created_at,
      'images': object.images,
      'images_caption': object.images_caption
    }
  data = jsonify(map(convert_to_json, news))
  return data

@app.route('/news', methods=['POST'])
def create_news():
  data = request.get_json()
  news = News(id=data['id'], title=data['title'], content=data['content'], created_at=data['created_at'], images=data['images'], images_caption=data['images_caption'])
  db.session.add(news)
  db.session.commit()
  return jsonify({ 'status': 201, 'message': 'create success'})

@app.route('/news', methods=['PUT'])
def update_news():
  data = request.get_json()
  news_id = data['id']
  news = News.query.filter_by(id=news_id).first()
  news.title = data['title']
  news.content = data['content']
  news.created_at = data['created_at']
  news.images = data['images']
  news.images_caption = data['images_caption']
  db.session.commit()
  return jsonify({ 'status': 200, 'message': 'update success' })

@app.route('/news/<news_id>', methods=['DELETE'])
def delete_news(news_id):
  news = News.query.filter_by(id=news_id).first()
  db.session.delete(news)
  db.session.commit()
  return jsonify({ 'status': 200, 'message': 'delete success'})

# API Donation

@app.route('/donation', methods=['GET'])
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
      'submitted_at': object.submitted_at
    }
  data = jsonify(map(convert_to_json, donation))
  return data

@app.route('/donation', methods=['POST'])
def create_donation():
  data = request.get_json()
  donation = Donation(id=data['id'], name=data['name'], phone=data['phone'], email=data['email'], amount=data['amount'], receipt=data['receipt'], submitted_at=data['submitted_at'])
  db.session.add(donation)
  db.session.commit()
  return jsonify({ 'status': 201, 'message': 'create success'})

if __name__ == '__main__':
  app.run(debug=True)