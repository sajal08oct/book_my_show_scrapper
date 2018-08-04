import scrapy
import json
from bms.items import GroupMovieItem, MovieInfoItem, MovieTimeInfoItem, CrewInfoItem, ReviewerInfoItem, \
    CinemaInfoItem
import datetime
import random
import urllib.request
import pickle,gzip

import os
from bms.properties.PropertyReader import PropertyManager
import logging
from twisted.python import log as twisted_log

import pprint


class BMSSpider(scrapy.Spider):
    name = "bms_db"
    propertyManager = PropertyManager()

    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def start_requests(self):
        # gives all the movies of a particular type
        url = 'https://in.bookmyshow.com/serv/getData?cmd=QUICKBOOK&type=MT&getRecommendedData=1&_='
        metaData = []
        with open("../properties/cookie.txt",'r') as file:
            for line in file:
                sts = line.strip("\n")
                dict = {sts.split('#')[0] : sts.split('#')[1]}
                metaData.append(dict)

        for i in range(0, len(metaData)):
            request = scrapy.Request(url=url + str(random.randint(0, 1513699714809)), callback=self.parse_json_data,
                                     cookies=metaData[i],
                                     meta={'cookiejar': i})
            yield request


    def parse_json_data(self, response):
        # parse json

        jsonResponse = json.loads(response.body_as_unicode())
        # self.logger.debug('Parse function called on %s', jsonResponse['moviesData']['BookMyShow']['arrMovies'])
        movieArray = []
        for movieGroup in jsonResponse['moviesData']['BookMyShow']['arrEvents']:
            movie = GroupMovieItem()
            movie['groupId'] = movieGroup['EventGroup']
            movie['groupName'] = movieGroup['EventTitle']
            movie['duration'] = movieGroup['EventGrpDuration']
            movie['genre'] = movieGroup['EventGrpGenre']
            movie['censor'] = movieGroup['EventGrpCensor']
            yield movie
            movie['childMovies'] = []

            for movieInfo in movieGroup['ChildEvents']:

                childMovie = MovieInfoItem()
                childMovie['movieId'] = movieInfo['EventCode']
                childMovie['movieType'] = movieInfo['EventType']
                childMovie['movieLanguage'] = movieInfo['EventLanguage']
                childMovie['movieName'] = movieInfo['EventName']
                childMovie['movieDimension'] = movieInfo['EventDimension']
                childMovie['movieStartDate'] = movieInfo['EventDate']
                childMovie['jsonGenre'] = dict(movieInfo['JsonGenre'])
                # childMovie['movieCensor'] = movieInfo['EventCensor']
                childMovie['movieSynopsis'] = movieInfo['EventSynopsis']
                childMovie['movieDuration'] = movieInfo['EventDuration']
                childMovie['movieTrailerURL'] = movieInfo['EventTrailerURL']

                yield childMovie
                getDataForDays = self.propertyManager.getPropertyAsInteger("number.of.days.info")
                for i in range(getDataForDays):
                    nextDate = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y%m%d")
                    timing_url = "https://in.bookmyshow.com/buytickets/tiger-zinda-hai-bengaluru/movie-bang-" \
                                 + movieInfo['EventCode'] + "-MT/" + nextDate

                    logging.info("getting timing info for url " + timing_url)
                    yield scrapy.Request(url=timing_url, callback=self.parse_movie_timings,
                                         meta={'date': nextDate, 'cookiejar': response.meta['cookiejar']})
                movie['childMovies'].append(dict(childMovie))

                # get meta data for the event
                metaDataUrl = "https://in.bookmyshow.com/bengaluru/movies/tiger-zinda-hai/" + movieInfo['EventCode'];
                logging.info("getting meta for url :" + metaDataUrl)
                yield scrapy.Request(metaDataUrl, callback=self.parse_meta_info,
                                     meta={'movieId': movieInfo['EventCode'],
                                           "groupId": movieGroup['EventGroup'], 'cookiejar': response.meta['cookiejar']})
            movieArray.append(dict(movie))
        for cinemas in jsonResponse['cinemas']['BookMyShow']['aiVN']:
            cinemaItem = CinemaInfoItem()
            cinemaItem['code'] = cinemas['VenueCode']
            cinemaItem['companyCode'] = cinemas['CompanyCode']
            cinemaItem['name'] = cinemas['VenueName']
            cinemaItem['latitude'] = cinemas['VenueLatitude']
            cinemaItem['longitude'] = cinemas['VenueLongitude']
            cinemaItem['address'] = cinemas['VenueAddress']
            cinemaItem['subRegionCode'] = cinemas['VenueSubRegionCode']
            cinemaItem['subRegionName'] = cinemas['VenueSubRegionName']
            yield cinemaItem
        with open('../data/movie.json', 'w+') as outfile:
            json.dump(movieArray, outfile)


    def parse_meta_info(self, response):
        movieId = response.meta['movieId']
        groupId = response.meta['groupId']
        detailsInfo = response.xpath("//div[@class='details']")

        reviewRatingInfo = detailsInfo.xpath("div[@class='review-ratings ']")

        ##########review Rating#################
        reviewAndRating = {}

        heartRating = reviewRatingInfo.xpath(
            "div[@class = 'heart-rating']/span[@class='__percentage']/text()").extract_first().strip('%')
        userVoteCount = reviewRatingInfo.xpath(
            "div[@class = 'heart-rating']/div[@class='__votes']/text()").extract_first().strip()
        reviewAndRating.update({"heartRating": {"rating": heartRating, "userVoteCount": userVoteCount}})

        criticRating = reviewRatingInfo.xpath(
            "div[@class = 'critic-rating']/span[@class='__rating']/ul/@data-value").extract_first().strip()
        reviewAndRating.update({"criticRating": {"averageRating": criticRating}})
        userRating = reviewRatingInfo.xpath(
            "div[@class = 'user-rating']/span[@class='__rating']/ul/@data-value").extract_first().strip()

        reviewAndRating.update({"userRating": {"averageRating": userRating,
                                               "reviews": []}})

        #############cast and crew info##################
        summaryInfo = detailsInfo.xpath("div[@class='summary-reviews']")
        movieInfoTab = summaryInfo.xpath("div[@id='mv-summary']")
        metaDataInfo = {}
        metaDataInfo['synopsis'] = movieInfoTab.xpath(
            "div[@class='synopsis']/blockquote/text()").extract_first().strip()
        castNameList = []
        castNameXpath = movieInfoTab.xpath("div[@id= 'cast']/div[@id='cast-carousel']/div/span")
        for name in castNameXpath:
            castNameList.append(name.xpath("a/div/@content").extract_first())
        metaDataInfo['cast'] = castNameList
        for cast in castNameList:
            crewItem = CrewInfoItem()
            crewItem['movieId'] = movieId
            crewItem['groupId'] = groupId
            crewItem['role'] = 'ACTOR'
            crewItem['name'] = cast
            yield crewItem

        crewNameXpath = movieInfoTab.xpath("div[@id= 'crew']/div[@id='crew-carousel']/div/span")
        crewNameData = {}
        for name in crewNameXpath:
            crewName = name.xpath("a/div/@content").extract_first()

            role = name.xpath("a/div/span[@class='__role']/text()").extract_first()
            # self.logger.debug({crewName:role})
            crewNameData.update({crewName: role})

            roles = role.split("|")[:-1]
            for role in roles:
                crewItem = CrewInfoItem()
                crewItem['movieId'] = movieId
                crewItem['groupId'] = groupId
                crewItem['name'] = crewName
                crewItem['role'] = role.strip().upper()
                yield crewItem
        metaDataInfo['crew'] = crewNameData
        metaDataInfo['rating'] = reviewAndRating

        ###############critic ratings########################
        reviewInfoTab = summaryInfo.xpath("div[@id='mv-critic']")

        criticReveiwRatingsXpath = reviewInfoTab.xpath("div[@class = 'mv-synopsis-review']")

        criticReviewRatingsList = []

        for criticReview in criticReveiwRatingsXpath:
            comment = criticReview.xpath("div[@class='__reviewer-comment']")
            criticReviewData = {}
            reviewLeft = comment.xpath("div[@class= '__reviewer-name-rate']/span[@class= '__reviewer-left']")
            reviewHeading = reviewLeft.xpath("span[@id='critic_']/text()").extract_first().strip()
            criticReviewRating = reviewLeft.xpath(
                "span[@class = '__review-rate ']/span/svg/@data-value").extract_first()

            criticReviewText = comment.xpath("div[@class= '__reviewer-text']/span/text()").extract_first().strip()

            print(criticReviewText)
            criticReviewData.update({"criticName": reviewHeading, "rating": criticReviewRating,
                                     "review": criticReviewText})
            criticReviewRatingsList.append(criticReviewData)

        reviewAndRating.update({"criticRating": {"averageRating": criticRating,
                                                 "reviews": criticReviewRatingsList}})

        for criticReview in criticReviewRatingsList:
            reviewInfo = ReviewerInfoItem()
            print(criticReview)
            reviewInfo['movieId'] = movieId
            reviewInfo['groupId'] = groupId
            reviewInfo['name'] = criticReview['criticName']
            reviewInfo['rating'] = criticReview['rating']
            reviewInfo['reviewerType'] = 'CRITIC'
            reviewInfo['review'] = criticReview['review'].encode('utf8').decode('utf8', 'ignore')
            yield reviewInfo
        ###############user ratings########################
        # userReviewRatingsList = self.get_user_reveiw_list(groupId)
        userReviewUrl = 'https://in.bookmyshow.com/serv/getData.bms?cmd=GETREVIEWSGROUP&eventGroupCode=" + groupId + "&type=UR&pageNum=1&perPage=9&sort=POPULAR'
        userReviewRatingsList = yield scrapy.Request(userReviewUrl, callback=self.parse_user_review_info,
                                                     meta={'movieId': movieId,
                                                           "groupId": groupId, 'cookiejar': response.meta['cookiejar']})

        reviewAndRating.update({"userRating": {"averageRating": userRating,
                                               "reviews": userReviewRatingsList}})

        metaDataInfoTemp = {}
        metaDataInfoTemp[movieId] = metaDataInfo

        self.update_json_object_in_file(metaDataInfoTemp, "../data/metaDataInfo.json")


    def parse_movie_timings(self, response):
        aTags = response.xpath("//a[@class='__showtime-link  time_vrcenter ']")
        timeInfoNode = {}
        nodesRequired = ['href', 'data-session-id', 'data-showtime-code', 'data-showtime-filter-index',
                         'data-cut-off-date-time', 'data-venue-code', 'data-cat-popup']

        for element in aTags:
            movieTimeItem = MovieTimeInfoItem()
            if timeInfoNode.get(element.xpath('@data-event-id').extract_first()) is None:
                timeInfoNode[element.xpath('@data-event-id').extract_first()] = []
            movieTimeItem['movieId'] = element.xpath('@data-event-id').extract_first()

            attributes = {}
            movieTimeItem['movieDate'] = attributes['movieDate'] = response.meta['date']
            for index, attribute in enumerate(element.xpath('@*'), start=1):
                attribute_name = element.xpath('name(@*[%d])' % index).extract_first()
                if (attribute_name in nodesRequired):
                    attribute_name = self.remove_prefix(attribute_name, 'data-')
                    attributes[attribute_name] = attribute.extract()
            movieTimeItem['bookingHref'] = attributes['href']
            movieTimeItem['sessionId'] = attributes['session-id']
            movieTimeItem['showTimeCode'] = attributes['showtime-code']
            movieTimeItem['showTimeFilter'] = attributes['showtime-filter-index']
            movieTimeItem['cutOffDateTime'] = datetime.datetime.strptime(attributes['cut-off-date-time'],
                                                                         "%Y%m%d%H%M").date()
            movieTimeItem['venueCode'] = attributes['venue-code']
            movieTimeItem['priceInfo'] = attributes['cat-popup']
            yield movieTimeItem
            timeInfoNode[element.xpath('@data-event-id').extract_first()].append((attributes))

        self.update_json_object_in_file(timeInfoNode, "../data/movieTime.json")


    def update_json_object_in_file(self, json_object, outfile):
        if os.access(outfile, os.R_OK):
            with open(outfile, 'r+') as f:
                data = json.load(f)
        else:
            data = {}

        data.update((json_object))

        with open(outfile, 'w+') as f:
            json.dump(data, f)


    def remove_prefix(self, str, prefix):
        if str.startswith(prefix):
            return str[len(prefix):]
        else:
            return str


    def get_user_reveiw_list(self, groupId):
        userReviewURL = "https://in.bookmyshow.com/serv/getData.bms?cmd=GETREVIEWSGROUP&eventGroupCode=" + groupId + "&type=UR&pageNum=1&perPage=9&sort=POPULAR"

        userReviewRequest = urllib.request.Request(userReviewURL)
        userReviewResponse = urllib.request.urlopen(userReviewRequest).read()
        userReviewJsonResponse = json.loads(userReviewResponse.decode('utf-8'))

        userReviewRatingsList = []
        for review in userReviewJsonResponse.get("data").get("Reviews"):
            reviewData = {}
            reviewData['reviewTitle'] = review.get("Title")
            reviewData['reviewerName'] = review.get("Name")
            reviewData['rating'] = review.get("Rating")
            reviewData['review'] = review.get("Review")
            userReviewRatingsList.append(reviewData)

        return userReviewRatingsList


    def parse_user_review_info(self, response):
        movieId = response.meta['movieId']
        groupId = response.meta['groupId']
        userReviewRatingsList = []
        for review in response.get("data").get("Reviews"):
            reviewData = {}
            reviewData['reviewTitle'] = review.get("Title")
            reviewData['reviewerName'] = review.get("Name")
            reviewData['rating'] = review.get("Rating")
            reviewData['review'] = review.get("Review")
            userReviewRatingsList.append(reviewData)

        for userReview in userReviewRatingsList:
            reviewInfo = ReviewerInfoItem()
            reviewInfo['movieId'] = movieId
            reviewInfo['groupId'] = groupId
            reviewInfo['name'] = userReview['reviewerName']
            reviewInfo['rating'] = userReview['rating']
            reviewInfo['reviewerType'] = 'USER'
            reviewInfo['review'] = userReview['review'].encode('utf8').decode('utf8', 'ignore')

            yield reviewInfo
        return userReviewRatingsList
