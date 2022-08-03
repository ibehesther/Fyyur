#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from asyncio.windows_events import NULL
from distutils.command.sdist import show_formats
import os
import json
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for, jsonify
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

import models as models 
from models import app, db



db.create_all()
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  venues = models.Venue.query.order_by(db.desc('id')).limit(10).all()
  artists = models.Artist.query.order_by(db.desc('id')).limit(10).all()
  return render_template('pages/home.html', venues = venues, artists = artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]

  try:
    venues = models.Venue.query.all()
    for venue in venues:
      location = {
        "city" : venue.city,
        "state" : venue.state,
        "venues" : []
      }
      venues_in_location = models.Venue.query.filter_by(city = venue.city, state = venue.state ).all()
      location["venues"] = venues_in_location
      if location in data:
        continue
      else:
        data.append(location)     
  except:
    return jsonify({'Error' : 'Something wrong happened!'})
      
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = models.Venue.query.filter(models.Venue.name.ilike('%'+search_term+'%')).all()
  response = {
    "count" : len(venues),
    "data" : []
  }
  for venue in venues:
    data = {
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows" : 0
    }
    response["data"].append(data)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = models.Venue.query.get(venue_id)
  today = datetime.now()
  venue_past_shows = db.session.query(models.Show).join(models.Venue).filter(models.Show.venue_id == venue_id).filter(models.Show.start_time < today).all()
  venue_upcoming_shows = db.session.query(models.Show).join(models.Venue).filter(models.Show.artist_id == venue_id).filter(models.Show.start_time > today).all()
  data = {
    "id" : venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
 
  for show in venue_past_shows:
    print(show.artist)
    past_show_details = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      # "start_time": "2035-04-15T20:00:00.000Z"
    }
    data["past_shows"].append(past_show_details)
  for show in venue_upcoming_shows:  
    upcoming_show_details = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      # "start_time": "2035-04-15T20:00:00.000Z"
    }
    data["upcoming_shows"].append(upcoming_show_details)
  data['past_shows_count'] = len(venue_past_shows)
  data['upcoming_shows_count'] = len(venue_upcoming_shows)    
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    form = VenueForm(request.form)
    venue = models.Venue(name = form.name.data, city = form.city.data, state = form.state.data, address = form.address.data,
    phone = form.phone.data, genres = form.genres.data, 
    image_link= form.image_link.data, facebook_link = form.facebook_link.data, 
    website_link= form.website_link.data, seeking_talent= form.seeking_talent.data,
    seeking_description = form.seeking_description.data
    )
    if form.validate(): 
      db.session.add(venue)
      db.session.commit()
    else:
      error = True
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error == True:
       flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    else :
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
     # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
     
# -------------------------------------------------------------------------------------
# Delete Venue
# -------------------------------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['DELETE', 'GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = models.Venue.query.get(venue_id)
    venue_name = venue.name
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True  
    db.session.rollback()
  finally:
    db.session.close()
    if error == True:
      flash('An error occured! ' + venue_name + ' could not be deleted')  
    else:
      flash(venue_name + " was successfully deleted!")
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists = models.Artist.query.order_by('id').all()
  for artist in artists:
    artist_info = {
      "id" : artist.id,
      "name" : artist.name
    }
    data.append(artist_info)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form["search_term"]
  artists = models.Artist.query.filter(models.Artist.name.ilike('%'+search_term+'%')).all()
  response = {
    "count" : len(artists),
    "data" : []
  }
  for artist in artists:
    artist_info = {
      "id" : artist.id,
      "name" : artist.name,
      "num_upcomig_shows" : 0
    }
    response["data"].append(artist_info)
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
 
  artist = models.Artist.query.get(artist_id)
  today = datetime.now()
  artist_past_shows = db.session.query(models.Show).join(models.Artist).filter(models.Show.artist_id == artist_id).filter(models.Show.start_time < today).all()
  artist_upcoming_shows = db.session.query(models.Show).join(models.Artist).filter(models.Show.artist_id == artist_id).filter(models.Show.start_time > today).all()
  data = {
    "id" : artist.id,
    "name" : artist.name,
    "genres" : artist.genres,
    "city" : artist.city,
    "state": artist.state,
    "phone" : artist.phone,
    "website_link" : artist.website_link,
    "seeking_venue" : artist.seeking_venue,
    "facebook_link" : artist.facebook_link,
    "image_link" : artist.image_link,
    "past_shows" : [],
    "upcoming_shows" : [],
    "past_shows_count": 0,
    "upcoming_shows_count" : 0
  }
  for show in artist_past_shows:
    print(show.venue)
    past_show_details = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      # "start_time": "2035-04-15T20:00:00.000Z"
    }
    data["past_shows"].append(past_show_details)

  for show in artist_upcoming_shows:
    upcoming_show_details = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      # "start_time": "2035-04-15T20:00:00.000Z"
    }
    data["upcoming_shows"].append(upcoming_show_details)

  data['past_shows_count'] = len(artist_past_shows)
  data['upcoming_shows_count'] = len(artist_upcoming_shows) 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = models.Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try :
    artist = models.Artist.query.get(artist_id)
    form = ArtistForm(request.form)
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data
    db.session.commit()
  except :
    db.session.rollback()
  finally:
    db.session.close()    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(request.form)
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  venue = models.Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try :
    form = VenueForm(request.form)
    venue = models.Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = form.genres.data 
    venue.address = form.address.data 
    venue.city = form.city.data 
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
  except:
    db.session.rollback()
  finally: 
    db.session.close()    
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
  form = ArtistForm(request.form)
  artist = models.Artist(name = form.name.data, city = form.city.data, state = form.state.data,
  phone = form.phone.data, genres = form.genres.data, 
  image_link= form.image_link.data, facebook_link = form.facebook_link.data, 
  website_link= form.website_link.data, seeking_venue= form.seeking_venue.data,
  seeking_description = form.seeking_description.data)
  try :
    print(artist.website_link)
    if form.validate():
      db.session.add(artist)
      db.session.commit()
    else :
      error = True  
  except:
    error = True
    db.session.rollback()    
  finally:
    db.session.close()
    if error == True:
      flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

# -------------------------------------------------------------------------------------
# Delete Artist
# -------------------------------------------------------------------------------------
@app.route('/artists/<artist_id>/delete', methods=['DELETE', 'GET'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    artist = models.Artist.query.get(artist_id)
    # shows = models.Show.query.filter_by(artist_id = artist_id).all()
    artist_name = artist.name
    db.session.delete(artist) 
    db.session.commit()
  except:
    error = True  
    db.session.rollback()
  finally:
    db.session.close()
    if error == True:
      flash('An error occured! ' + artist_name + ' could not be deleted')  
    else:
      flash(artist_name + " was successfully deleted!")
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = models.Show.query.order_by(db.desc(models.Show.start_time)).all()
  for show in shows:
    venue = models.Venue.query.get(show.venue_id)
    artist = models.Artist.query.get(show.artist_id)
    show_info= {
      "venue_id" : venue.id,
      "venue_name" : venue.name,
      "artist_id" : artist.id,
      "artist_name" : artist.name,
      "artist_image_link" : artist.image_link,
      "start_time" : str(show.start_time)
    }
    data.append(show_info)
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

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  try:
    form = ShowForm(request.form)
    if form.validate():
      artist_id = int(form.artist_id.data)
      venue_id = int(form.venue_id.data)
      venue = models.Venue.query.get(venue_id)
      artist = models.Artist.query.get(artist_id)
      if venue and artist:
        show = models.Show(artist_id=artist_id, venue_id=venue_id, start_time=form.start_time.data)
        db.session.add(show)
        db.session.commit()
      else:
        error = True
    else:
      error = True  
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()  
    if error == True:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
  return render_template('pages/home.html')

# ----------------------------------------------------------------
# Book Venue for show
# ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/book', methods=['GET'])
def book_venue(venue_id):
  form = ShowForm()
  form.venue_id.data = venue_id
  return render_template('forms/new_show.html', form=form)

@app.route('/venues/<int:venue_id>/book', methods=['POST'])
def book_venue_submission(venue_id):
  error = False
  try:
    form = ShowForm(request.form)
    if form.validate():
      artist_id = int(form.artist_id.data)
      venue_id = int(form.venue_id.data)
      venue = models.Venue.query.get(venue_id)
      artist = models.Artist.query.get(artist_id)
      if venue and artist:
        show = models.Show(artist_id = artist_id, venue_id = venue_id, start_time = form.start_time.data)
        db.session.add(show)
        db.session.commit()
      else:
        error = True
    else:
      error = True  
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()  
    if error == True:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
  return render_template('pages/home.html')
  

# ----------------------------------------------------------------
# Book Artist for show
# ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/book', methods=['GET'])
def book_artist(artist_id):
  form = ShowForm()
  form.artist_id.data = artist_id
  return render_template('forms/new_show.html', form=form)

@app.route('/artists/<int:artist_id>/book', methods=['POST'])
def book_artist_submission(artist_id):
  error = False
  try:
    form = ShowForm(request.form)
    if form.validate():
      artist_id = int(form.artist_id.data)
      venue_id = int(form.venue_id.data)
      venue = models.Venue.query.get(venue_id)
      artist = models.Artist.query.get(artist_id)
      if venue and artist:
        show = models.Show(artist_id=artist_id, venue_id=venue_id, start_time=form.start_time.data)
        db.session.add(show)
        db.session.commit()
      else:
        error = True
    else:
      error = True  
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()  
    if error == True:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
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
    app.debug = True
    app.run()

# # Or specify port manually:

# if __name__ == '__main__':
#     app.debug = True
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)

