'''
This file contains capture exportation methods to:
- to_postgre -- postgre 
- to_json    -- json
'''
from datetime import datetime, timedelta
import sqlalchemy as sa
import os
from sqlalchemy import (VARCHAR, Text, BigInteger, INTEGER, TIMESTAMP, JSON, 
                        BOOLEAN, Column, Float, ForeignKey)

# Local imports
from app.utils import create_mysql_engine, create_postgis_engine


class Export(object):
    """
    Exports captured waze data according to a time interval 
    to a given format.

    Parameters
    ----------
    tables : list, default ['irregularities', 'jams', 'alerts']
        List with the desired waze table data.
    time_range : {int, None}, default 30
        Displace the date backwards given a final_date. It has preference
        over initial_date.
        
        * int : number of days to go backwards.

        * None : disables time_range
    final_date: datetime, default None 
        Final date to collect data. 

        * None : datetime.datetime.now() is set.
    initial_date: datetime, optional
        Initial date to collect data. time_range has to be set to None.
        
        * None : datetime.datetime.now() - timedelta(days=30) is set.
    chunksize : int, default 10000
        Maximum number of rows loaded to memory. Decrease it if your computer
        has low memory availability.
    """

    def __init__(self, 
                tables=['irregularities', 'jams', 'alerts'],
                time_range=30,
                final_date=None,
                initial_date=None, 
                chunksize=10000
                ):
        
        self.tables = tables
        self.time_range = time_range
        self.final_date = (datetime.now() + timedelta(days=2)
                             if final_date is None 
                             else final_date)
        self.initial_date = (datetime.now() - timedelta(days=time_range)
                                if time_range is not None 
                                else initial_date)
        self.chunksize = chunksize

        self.columns = ['id', 
                        'start_time_millis', 
                        'end_time_millis', 
                        'start_time', 
                        'end_time', 
                        'timezone', 
                        'raw_json']

        self.queries = self.make_query()

        # Use waze db
        self.engine_mysql = create_mysql_engine()
        self.engine_mysql.execute('USE waze')


    @staticmethod
    def to_mysql_date(date):
        return datetime.strftime(date, '%Y-%m-%d')
    

    def make_query(self):

        query = {}
        for table in self.tables:
            query[table] = """
                                SELECT *
                                FROM `{table}`
                                WHERE `start_time`
                                    BETWEEN '{initial_date}'
                                    AND '{final_date}'
                        """.format(
                            table=table,
                            initial_date=self.to_mysql_date(self.initial_date),
                            final_date=self.to_mysql_date(self.final_date),
                        )

        return query


    def perform_query(self, table):

        with self.engine_mysql.connect() as con:
             
            result = con.execution_options(stream_results=True).\
                        execute(self.queries[table])
            while True:
                chunk = result.fetchmany(self.chunksize)
                if not chunk:
                    break
                yield chunk


    def select(self, row, by='id'):

        return row[self.columns.index(by)]


    @staticmethod
    def create_filename(table, start_time, timezone, idx):
        
        timezone = timezone.replace('/', '-')

        return '{table}--{start_time}--{timezone}--{idx}'.format(
                                            table=table,
                                            start_time=start_time,
                                            timezone=timezone,
                                            idx=idx
                                            )
    def generate_name(self):

        self.name = '{initial_date}--to--{final_date}'.format(
                        initial_date=self.to_mysql_date(self.initial_date),
                        final_date=self.to_mysql_date(self.final_date))


    def create_pathname(self, output_path):
        
        self.generate_name()

        return os.path.join(output_path, self.name)

