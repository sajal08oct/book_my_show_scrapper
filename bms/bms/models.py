from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, DateTime,Float,Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from scrapy.conf import settings

DeclarativeBase = declarative_base()

'''
 
create table movie_group (
	id integer,
	group_id varchar(45) ,
	group_name varchar(100) ,
	duration  varchar(200) ,
	censor varchar(20) ,
	genre  varchar(200) ,
	synopsis varchar(2000) ,
	primary key (id)
);



'''
class MovieGroup(DeclarativeBase):
    """Sqlalchemy model"""
    __tablename__ = "groups"
    id = Column(Integer)
    groupId = Column('group_id', String(45) , primary_key=True)
    groupName = Column('group_name', String(100), nullable=True)
    duration = Column('duration', String(200))
    censor = Column('censor',String(20))
    genre = Column('genre',String(200))

class MovieInfo(DeclarativeBase):
    """Sqlalchemy model"""
    __tablename__ = "movie"
    movieId = Column('movie_id', String(45) , primary_key=True)
    movieLanguage = Column('movie_language', String(100))
    groupId = Column('group_id', String(45))
    movieName = Column('movie_name', String(200))
    movieDimension = Column('movie_dimension', String(20))
    movieStartDate =  Column('movie_start_date', DateTime)
    jsonGenre =  Column('json_genre', String(500))
    movieSynopsis = Column('synopsis', String(500))
    movieTrailerURL = Column('movie_trailer_url',String(20))
    movieDuration = Column('movie_duration',String(45))
    movieType = Column('movie_type',String(45))


class MovieTimeInfo(DeclarativeBase):
    """Sqlalchemy model"""
    __tablename__ = "movie_time_info"
    id = Column('id', Integer , primary_key=True)
    movieId = Column('movie_id', String(45))
    movieDate =  Column('movie_date', DateTime)
    bookingHref = Column('booking_href', String(200))
    sessionId =  Column('session_id', String(40))
    showTimeCode = Column('show_time_code', String(20))
    showTimeFilter = Column('show_time_filter',String(50))
    cutOffDateTime = Column('cut_off_date_time',DateTime)
    venueCode = Column('venue_code',String(50))
    priceInfo = Column('price_info_json',String(1000))


class CrewInfo(DeclarativeBase):
    __tablename__="crew_info"
    id = Column('id', Integer , primary_key=True)
    movieId = Column('movie_id', String(45))
    groupId = Column('group_id', String(45))
    name = Column('name', String(100))
    role = Column('role', String(100))

class ReviewInfo(DeclarativeBase):
    __tablename__= "review_info"
    id = Column('id', Integer, primary_key=True)
    movieId = Column('movie_id', String(45))
    groupId = Column('group_id', String(45))
    name = Column('name', String(100))
    rating = Column('rating', Float)
    review = Column('review', Text)
    reviewerType = Column('reviewer_type', String(2000))


class CinemaInfo(DeclarativeBase):
    __tablename__ = "cinemas"
    code = Column('code', Integer, primary_key=True)
    companyCode = Column('company_code',String(100))
    name = Column('name', String(200))
    latitude = Column('latitude',String(20))
    longitude = Column('longitude',String(20))
    address = Column('address',String(1000))
    subRegionCode = Column('sub_region_code',String(100))
    subRegionName = Column('sub_region_name',String(100))

def create_session():
    # declare the connecting to the server
    engine = create_engine(settings.get('CONNECTION_STRING')
                           , echo=False)
    # connect session to active the action
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
