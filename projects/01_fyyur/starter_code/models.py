"""
Artist, Venue and Show models
"""
# Imports
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
# Models

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(900))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.BOOLEAN)
    seeking_description = db.Column(db.String(900))
    created_date =  db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Venue: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, shows: {self.shows}, genres: {self.genres}, website: {self.website}, seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}, created_date: {self.created_date}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(900))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.BOOLEAN)
    seeking_description = db.Column(db.String(900))
    created_date =  db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Artist: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, shows: {self.shows}, website: {self.website}, seeking_venue: {self.seeking_venue}, seeking_description: {self.seeking_description}, created_date: {self.created_date}>'

class Show(db.Model):
  _tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time= db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)

  def __repr__(self):
    return f'<Show {self.id}, start_time: {self.start_time}, artist_id: {self.artist_id}, venue_id: {self.venue_id}>'  