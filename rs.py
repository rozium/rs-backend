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

if __name__ == '__main__':
  app.run(debug=True)