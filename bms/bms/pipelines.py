# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from bms.models import create_session ,MovieGroup,MovieInfo,MovieTimeInfo, CrewInfo,ReviewInfo,CinemaInfo
from bms.items import GroupMovieItem ,MovieInfoItem , MovieTimeInfoItem , CrewInfoItem ,ReviewerInfoItem,CinemaInfoItem

class BmsPipeline(object):
    def __init__(self):
        self.session = create_session()

    def process_item(self, item, spider):
        if isinstance(item, GroupMovieItem):
            self.insert_group(item)
        elif isinstance(item,MovieInfoItem):
            self.insert_movie_info(item)

        elif isinstance(item,MovieTimeInfoItem):
            self.insert_movie_time_info(item)
        elif isinstance(item , CrewInfoItem):
            self.insert_movie_crew_info(item)
        elif isinstance(item,ReviewerInfoItem):
            self.insert_review_info(item)
        elif isinstance(item,CinemaInfoItem):
            self.insert_cinema_info(item)
        return item


    def insert_movie_time_info(self,item):
        sql_time_info = MovieTimeInfo(**item)
        self.session.add(sql_time_info)
        self.session.commit()
        self.session.close()

    def insert_cinema_info(self,item):
        sql_cinema = CinemaInfo(**item)

        query = self.session.query(CinemaInfo)
        query = query.filter(CinemaInfo.code == item['code'])
        record = query.first()
        if record is None:
            self.session.add(sql_cinema)
            self.session.commit()
        self.session.close()


    def insert_review_info(self,item):
        sql_review_info = ReviewInfo(**item)
        self.session.add(sql_review_info)
        self.session.commit()
        self.session.close()


    def insert_group(self ,item):
        sql_movie_group = MovieGroup(**item)
        query = self.session.query(MovieGroup)
        query = query.filter(MovieGroup.groupId == item['groupId'])
        record = query.first()
        if record is None:
            self.session.add(sql_movie_group)
            self.session.commit()
        self.session.close()


    def insert_movie_info(self,item):
        sql_movie_group = MovieInfo(**item)

        query = self.session.query(MovieInfo)
        query = query.filter(MovieInfo.movieId == item['movieId'])
        record = query.first()
        if record is None:
            self.session.add(sql_movie_group)
            self.session.commit()
        self.session.close()

    def insert_movie_crew_info(self,item):
        sql_crew = CrewInfo(**item)
        self.session.add(sql_crew)
        self.session.commit()
        self.session.close()




