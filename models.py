from rs import db

class Profile(db.Model):
  name: db.Column(db.String(50))
  phone: db.Column(db.String(50))
  address: db.Column(db.Text)
  about: db.Column(db.Text)
  vision: db.Column(db.Text)
  mission: db.Column(db.Text)
  link: db.Column(db.Text)

class News(db.Model):
  id: db.Column(db.Integer, primary_key=True)
  title: db.Column(db.String(100))
  content: db.Column(db.Text)
  created_at: db.Column(db.DateTime)
  images: db.Column(db.Text)
  images_caption: db.Column(db.Text)

class Donation(db.Model):
  id: db.Column(db.Integer, primary_key=True)
  name: db.Column(db.String(50))
  phone: db.Column(db.String(50))
  email: db.Column(db.String(50))
  amount:db.Column(db.Integer)
  receipt: db.Column(db.Text)
  submitted_at: db.Column(db.DateTime)
