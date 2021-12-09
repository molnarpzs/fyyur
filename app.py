#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import methodcaller
import pdb
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask.scaffold import _matching_loader_thinks_module_is_package
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'''Venue name: {self.name}, 
            city: {self.city}, 
            state: {self.state},
            address: {self.address}, 
            phone: {self.phone}, 
            image: {self.image_link},
            facebook: {self.facebook_link}, 
            genres: {self.genres}, 
            website: {self.website},
            seeking talent: {self.seeking_talent}, 
            description: {self.seeking_description}'''


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'''Artist name: {self.name},
            city: {self.city},
            state: {self.state},
            phone: {self.phone},
            genres: {self.genres},
            image: {self.image_link},
            facebook: {self.facebook_link},
            website: {self.website},
            seeking venue: {self.seeking_venue},
            description: {self.seeking_description}'''


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.String(24), nullable=False)

    def __repr__(self):
        return f'''Show with artist: {self.artist_id} Venue: {self.venue_id} start time: {self.start_time}'''

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/', methods=['GET'])
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    areas = []
    venues = Venue.query.all()
    places = Venue.query.distinct(Venue.city, Venue.state).all()
    for place in places:
        areas.append({
            'city': place.city,
            'state': place.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
            } for venue in venues if venue.city == place.city and venue.state == place.state]
        })
    return render_template('pages/venues.html', areas=areas)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike('%' + search + '%')).all()
    data = []
    for venue in venues:
        data.append({
            'id': venue.id,
            'name': venue.name
        })
    response = {
        'count': len(venues),
        'data': data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search)


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    past_shows = []
    upcoming_shows = []
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.genres = venue.genres.split(",")
    data = venue.__dict__
    data.pop('_sa_instance_state')
    shows = Show.query.filter_by(venue_id=venue.id).all()
    for show in shows:
        item = {}
        artist = Artist.query.filter_by(id=show.artist_id).first()
        item['artist_id'] = artist.id
        item['artist_name'] = artist.name
        item['artist_image_link'] = artist.image_link
        item['start_time'] = show.start_time
        if show.start_time < datetime.now().isoformat():
            past_shows.append(item)
        else:
            upcoming_shows.append(item)
    data['upcoming_shows'] = upcoming_shows
    data['past_shows'] = past_shows
    data['past_show_count'] = len(past_shows)
    data['upcoming_show_count'] = len(upcoming_shows)
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
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            genres=','.join(request.form.getlist('genres')),
            facebook_link=request.form['facebook_link'],
            website=request.form['website_link'],
            seeking_description=request.form['seeking_description']
        )
        if 'seeking_talent' not in request.form:
            venue.seeking_talent = False
        else:
            venue.seeking_talent = True
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    # return render_template('pages/home.html')
    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('The Venue has been successfully deleted!')
    except:
        error = True
        db.session.rollback()
        flash('An error occured. Venue could not be deleted.')
    finally:
        db.session.close()

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []
    for artist in artists:
        item = {}
        item['id'] = artist.id
        item['name'] = artist.name
        data.append(item)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike('%' + search + '%')).all()
    data = []
    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })
    response = {
        'count': len(artists),
        'data': data
    }
    return render_template('pages/search_artists.html', results=response, search_term=search)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data = Artist.query.filter_by(id=artist_id).first().__dict__
    data['genres'] = data['genres'].split(",")
    shows = Show.query.filter_by(artist_id=artist_id).all()
    show_list = []
    for show in shows:
        show_obj = {}
        show_obj['venue_id'] = show.venue_id
        show_obj['venue_name'] = Venue.query.filter_by(
            id=show.venue_id).first().name
        show_obj['venue_image_link'] = Venue.query.filter_by(
            id=show.venue_id).first().image_link
        show_obj['start_time'] = show.start_time
        show_list.append(show_obj)
    past_shows_count = 0
    past_shows = []
    upcoming_shows_count = 0
    upcoming_shows = []
    for item in show_list:
        if item['start_time'] < datetime.now().isoformat():
            past_shows_count += 1
            past_shows.append(item)
        else:
            upcoming_shows_count += 1
            upcoming_shows.append(item)
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = past_shows_count
    data['upcoming_shows_count'] = upcoming_shows_count
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres.split(',')
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
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
        artist.image_link = request.form['image_link']
        artist.genres = ','.join(request.form.getlist('genres'))
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website_link']
        artist.seeking_description = request.form['seeking_description']
        if 'seeking_venue' not in request.form:
            artist.seeking_venue = False
        else:
            artist.seeking_venue = True
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    else:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.genres.data = venue.genres.split(',')
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.address = request.form['address']
        venue.city = request.form['city']
        venue.sate = request.form['state']
        venue.phone = request.form['phone']
        venue.website_link = request.form['website_link']
        venue.facebook_link = request.form['facebook_link']
        venue.seeking_description = request.form['seeking_description']
        venue.image_link = request.form['image_link']
        if 'seeking_talent' not in request.form:
            venue.seeking_talent = False
        else:
            venue.seeking_talent = True
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    else:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
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
        artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            genres=','.join(request.form.getlist('genres')),
            facebook_link=request.form['facebook_link'],
            website=request.form['website_link'],
            seeking_description=request.form['seeking_description']
        )
        if 'seeking_venue' not in request.form:
            artist.seeking_venue = False
        else:
            artist.seeking_venue = True
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    # return render_template('pages/home.html')
    return redirect(url_for('index', methods=['GET']))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    show_list = []
    shows = Show.query.all()
    for show in shows:
        show_list.append({
            'venue_id': show.venue_id,
            'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
            'artist_id': show.artist_id,
            'artist_name': Artist.query.filter_by(id=show.artist_id).first().name,
            'artist_image_link': Artist.query.filter_by(id=show.artist_id).first().image_link,
            'start_time': show.start_time
        })
    return render_template('pages/shows.html', shows=show_list)


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
        start = request.form['start_time']
        show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=('T').join(start.split()) + '.000Z'

        )
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
    # return render_template('pages/home.html')
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
