# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BmsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GroupMovieItem(scrapy.Item):
    groupId = scrapy.Field()
    movieGroupId = scrapy.Field()
    groupName = scrapy.Field()
    duration = scrapy.Field()
    genre = scrapy.Field()
    censor = scrapy.Field()
    childMovies = scrapy.Field()


class MovieInfoItem(scrapy.Item):
    movieId = scrapy.Field()
    movieType = scrapy.Field()
    movieLanguage = scrapy.Field()
    movieName = scrapy.Field()
    movieDimension = scrapy.Field()
    movieStartDate = scrapy.Field()
    jsonGenre = scrapy.Field()
    movieCensor = scrapy.Field()
    movieSynopsis = scrapy.Field()
    movieDuration = scrapy.Field()
    movieTrailerURL = scrapy.Field()



'''
    "href": "/booktickets/ADCR/12471",
      "session-id": "12471",
      "showtime-code": "1630",
      "showtime-filter-index": "evening",
      "cut-off-date-time": "201801211430",
      "venue-code": "ADCR",
      "cat-popup": 
'''
class MovieTimeInfoItem(scrapy.Item):
    movieId = scrapy.Field()
    movieDate = scrapy.Field()
    bookingHref = scrapy.Field()
    sessionId = scrapy.Field()
    showTimeCode = scrapy.Field()
    showTimeFilter = scrapy.Field()
    cutOffDateTime = scrapy.Field()
    venueCode = scrapy.Field()
    priceInfo = scrapy.Field()

"""
	id integer auto_increment,
	movie_id varchar(45) ,
	name varchar(100),
	role varchar(100),
	primary key (id)
"""
class CrewInfoItem(scrapy.Item):
    movieId = scrapy.Field()
    groupId = scrapy.Field()
    name = scrapy.Field()
    role = scrapy.Field()
'''
id integer auto_increment,
	name  varchar(100),
	rating double,
	review varchar(2000),
	reviewer_type varchar(20),
	created_on timestamp default current_timestamp(),
	primary key (id)

'''
class ReviewerInfoItem(scrapy.Item):
    name = scrapy.Field()
    groupId = scrapy.Field()
    rating = scrapy.Field()
    review = scrapy.Field()
    reviewerType = scrapy.Field()
    movieId =scrapy.Field()


class CinemaInfoItem(scrapy.Item):
    code = scrapy.Field()
    companyCode = scrapy.Field()
    name = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    address = scrapy.Field()
    subRegionCode = scrapy.Field()
    subRegionName = scrapy.Field()
