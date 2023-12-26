#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import or_
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://konduruneha@localhost:5432/fyyurDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref='venue', lazy=False)
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.BOOLEAN)
    seeking_description = db.Column(db.String(900))

    def __repr__(self):
      return f'<Venue: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, shows: {self.shows}, genres: {self.genres}, website: {self.website}, seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(900))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref='artist', lazy=False)
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.BOOLEAN)
    seeking_description = db.Column(db.String(900))

    def __repr__(self):
      return f'<Artist: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, shows: {self.shows}, website: {self.website}, seeking_venue: {self.seeking_venue}, seeking_description: {self.seeking_description}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  _tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time= db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)

  def __repr__(self):
    return f'<Show {self.id}, start_time: {self.start_time}, artist_id: {self.artist_id}, venue_id: {self.venue_id}>'    

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # Group venues based on city and state
  data=[]
  grouped_venues = {}
  venues = Venue.query.all()
  for venue in venues:
    city = venue.city
    state = venue.state
    key = city + "_" + state
    venue_data = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(list(filter(lambda x: x.start_time > datetime.today(),
                                                  venue.shows))),
        }
    if key not in grouped_venues:
        grouped_venues[key] = {"city": city, "state": state, "venues": []}
    
    grouped_venues[key]["venues"].append(venue_data)

  for venue in grouped_venues:
      data.append(grouped_venues[venue])

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(
  Venue.name.ilike('%{}%'.format(search_term))).all()

  data = []
  for venue in venues:
    venue_data = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(venue.shows)
        }
    data.append(venue_data)

  response = {
           'count': len(data),
           'data':data
  }

  return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if not venue:
    abort(404)  # Return a 404 error if the venue with the provided ID doesn't exist
    
  # Extract past and upcoming shows using list comprehensions
  past_shows = list(filter(lambda show: show.start_time < datetime.now(), venue.shows))
  past_shows = [
            {
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.isoformat()
            } for show in past_shows]
  upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), venue.shows))
  upcoming_shows = [
            {
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.isoformat()
            } for show in upcoming_shows]

  # Construct venue data dictionary
  data = {
            "id": venue_id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows)
        }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  try:
        venue_details = Venue()
        venue_details.facebook_link = request.form['facebook_link']
        tmp_genres = request.form.getlist('genres')
        venue_details.name = request.form['name']
        venue_details.state = request.form['state']
        venue_details.city = request.form['city']
        venue_details.address = request.form['address']
        venue_details.genres = ','.join(tmp_genres)
        venue_details.phone = request.form['phone']
        venue_details.image_link = request.form['image_link']
        venue_details.website = request.form['website_link']
        venue_details.seeking_description = request.form['seeking_description']

  # on successful db insert, flash success
        db.session.add(venue_details)
        db.session.commit()

  except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
  finally:
        
        db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        if error:
            flash('An error occured. Venue ' + request.form['name'] + ' Could not be listed!')
        else:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    venue= Venue.query.get(venue_id)

    if venue is None:
        return abort(404)

    try:
        db.session.delete(venue)
        shows = list(venue.shows)
        for show in shows:
            db.session.delete(show)
        db.session.commit()
        flash(f'Venue {venue.name} was successfully deleted!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(f'An error occured. Venue {venue.name} Could not be deleted!')
    finally:
      db.session.close()
    return redirect(url_for('index'))
        

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  result = request.form.get('search_term')

  if result:
    search_results = Artist.query.filter(or_(
        Artist.name.ilike(f'%{result}%'),
        Artist.genres.ilike(f'%{result}%'),
    )).all()
  else:
    search_results = []

  response = {
    'count': len(search_results),
    'data': search_results,
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  past_shows = list(filter(lambda show: show.start_time < datetime.now(), artist.shows))
  past_shows = [
            {
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': show.start_time.isoformat()
            } for show in past_shows]
  upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), artist.shows))
  upcoming_shows = [
            {
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': show.start_time.isoformat()
            } for show in upcoming_shows]

  data = {
            "id": artist_id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows)
        }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        artist.genres = ','.join(tmp_genres)
        artist.website = request.form['website_link']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.seeking_description = request.form['seeking_description']
        db.session.add(artist)
        db.session.commit()
  except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
  finally:
      db.session.close()
      if error:
            flash('An error occured while updating details of Artist ' + request.form['name'])
      else:
            flash('Details of Artist ' + request.form['name'] + ' updated successfully!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)

    error = False
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        venue.genres = ','.join(tmp_genres)  # convert list to string
        venue.facebook_link = request.form['facebook_link']
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be updated.')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

    error = False
    try:
        artist_details = Artist()
        artist_details.seeking_description = request.form['seeking_description']
        artist_details.seeking_venue = True if request.form['seeking_venue'] == 'y' else False
        artist_details.name = request.form['name']
        artist_details.city = request.form['city']
        artist_details.state = request.form['state']
        artist_details.facebook_link = request.form['facebook_link']
        artist_details.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        artist_details.genres = ','.join(tmp_genres)
        artist_details.website = request.form['website_link']
        artist_details.image_link = request.form['image_link']
        db.session.add(artist_details)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
      # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        if error:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      # on successful db insert, flash success
        else:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()

  data = []
  for show in shows:
        data.append({
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.isoformat()
        })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
        show_details = Show()
        show_details.start_time = request.form['start_time']
        show_details.venue_id = request.form['venue_id']
        show_details.artist_id = request.form['artist_id']

        db.session.add(show_details)
        db.session.commit()
  except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
  finally:
        db.session.close()
          # TODO: on unsuccessful db insert, flash an error instead.
          # e.g., flash('An error occurred. Show could not be listed.')
          # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        if error:
            flash('An error occurred. Requested show could not be listed.')
        # on successful db insert, flash success
        else:
            flash('Requested show was successfully listed')
        return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
