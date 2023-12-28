#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    flash, 
    redirect, 
    url_for, 
    abort
    )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import or_, desc
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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
  venues = Venue.query.order_by(desc(Venue.created_date)).limit(10).all()
  artists = Artist.query.order_by(desc(Artist.created_date)).limit(10).all()
  return render_template('pages/home.html', venues = venues, artists = artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
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
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
  filter(
     Show.venue_id == venue_id,
     Show.artist_id == Artist.id,
     Show.start_time < datetime.now()
  ).\
    all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
  filter(
     Show.venue_id == venue_id,
     Show.artist_id == Artist.id,
     Show.start_time > datetime.now()
  ).\
    all()

  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  data = {
      'id': venue.id,
      'name': venue.name,
      'genres': venue.genres,
      'image_link' : venue.image_link,
      'city': venue.city,
      'state': venue.state,
      'address':venue.address,
      'phone':venue.phone,
      'website':venue.website,
      'facebook_link':venue.facebook_link,
      'seeking_description':venue.seeking_description,
      'seeking_talent':venue.seeking_talent,
      'past_shows': [{
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      } for artist, show in past_shows],
      'upcoming_shows': [{
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      } for artist, show in upcoming_shows],
      'past_shows_count': len(past_shows),
      'upcoming_shows_count': len(upcoming_shows)
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

  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
      try:
        venue = Venue(
          facebook_link = form.facebook_link.data,
          name = form.name.data,
          state = form.state.data,
          city = form.city.data,
          address = form.address.data,
          genres = form.genres.data,
          phone = form.phone.data,
          image_link = form.image_link.data,
          website = form.website_link.data,
          seeking_description = form.seeking_description.data,
          seeking_talent = form.seeking_talent.data,
          created_date = datetime.now()
        )

        db.session.add(venue)
        db.session.commit()
      except ValueError as e:
        error = True
        print(e)
        db.session.rollback()
      finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' + request.form['name'] + ' Could not be listed!')
        else:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))
  else:
      message = []
      for field, errors in form.errors.items():
          for error in errors:
              message.append(f"{field}: {error}")
      flash('Please fix the following error: '+', '.join(message))
      return render_template('forms/new_venue.html',form=form)

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
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
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
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
  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
  filter(
     Show.venue_id == Venue.id,
     Show.artist_id == artist_id,
     Show.start_time < datetime.now()
  ).\
    all()

  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
  filter(
     Show.venue_id == Venue.id,
     Show.artist_id == artist_id,
     Show.start_time > datetime.now()
  ).\
    all()

  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  data = {
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres,
      'image_link' : artist.image_link,
      'city': artist.city,
      'state': artist.state,
      'phone':artist.phone,
      'website':artist.website,
      'facebook_link':artist.facebook_link,
      'seeking_description':artist.seeking_description,
      'seeking_venue':artist.seeking_venue,
      'past_shows': [{
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      } for venue, show in past_shows],
      'upcoming_shows': [{
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      } for venue, show in upcoming_shows],
      'past_shows_count': len(past_shows),
      'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  error = False
  form = ArtistForm(request.form, meta={"csrf": False})
  try:
        artist.seeking_description = form.seeking_description.data
        artist.seeking_venue = form.seeking_venue.data
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.facebook_link = form.facebook_link.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.website = form.website_link.data
        artist.image_link = form.image_link.data
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
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form, meta={'csrf': False})
    error = False
    try:
          venue.facebook_link = form.facebook_link.data,
          venue.name = form.name.data,
          venue.state = form.state.data,
          venue.city = form.city.data,
          venue.address = form.address.data,
          venue.genres = form.genres.data,
          venue.phone = form.phone.data,
          venue.image_link = form.image_link.data,
          venue.website = form.website_link.data,
          venue.seeking_description = form.seeking_description.data,
          venue.seeking_talent = form.seeking_talent.data
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
    error = False
    form = ArtistForm(request.form, meta={"csrf": False})
    if form.validate():
      try:
        artist  = Artist(
        seeking_description = form.seeking_description.data,
        seeking_venue = form.seeking_venue.data,
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        facebook_link = form.facebook_link.data,
        phone = form.phone.data,
        genres = form.genres.data,
        website = form.website_link.data,
        image_link = form.image_link.data,
        created_date = datetime.now()
        )
        db.session.add(artist)
        db.session.commit()
      except ValueError as e:
        error = True
        print(e)
        db.session.rollback()
      finally:
        db.session.close()
        if error:
            flash('An error occured. Artist' + request.form['name'] + ' Could not be listed!')
        else:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))
    else:
      message = []
      for field, errors in form.errors.items():
          for error in errors:
              message.append(f"{field}: {error}")
      flash('Please fix the following error: '+', '.join(message))
      return render_template('forms/new_artist.html',form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
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
  error = False
  form = ShowForm(request.form, meta={"csrf": False})
  if form.validate():
    try:
        show  = Show(
        start_time = form.start_time.data,
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data
        )

        db.session.add(show)
        db.session.commit()
    except ValueError as e:
        error = True
        print(e)
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            flash('An error occured. Show Could not be listed!')
        else:
            flash('Show was successfully listed!')
        return redirect(url_for('index'))
  else:
      message = []
      for field, errors in form.errors.items():
          for error in errors:
              message.append(f"{field}: {error}")
      flash('Please fix the following error: '+', '.join(message))
      return render_template('forms/new_show.html',form=form)


@app.errorhandler(400)
def server_error(error):
    return render_template('errors/400.html'), 400

@app.errorhandler(401)
def server_error(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(403)
def server_error(error):
    return render_template('errors/403.html'), 403

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
