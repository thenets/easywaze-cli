'''
This file instanciate the parent class to export files from the MySql database
that stores the captured data.

It can be imported and used as a parent class to any other exportation method.

It has the following variables that can be used:

self.tables -- list :: selected tables to be exported
self.time_range -- int :: range of time given the final date
self.final_date -- datetime :: last day to be exported
self.initial_date  -- datetime :: first day to be exported
self.chunksize -- int :: maximum number of files in one operation
self.columns -- list :: columns at MySql database
self.queries -- list :: list of sql queries to select data given the time range
self.engine_mysql -- slalchemy.engine :: engine connected to MySql
self.name -- string :: name of the export base on the time range

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
        """Converts MySql date format to datetime 
        
        Arguments:
            date {string} -- MySql date
        
        Returns:
            datetime -- datetime object
        """
        return datetime.strftime(date, '%Y-%m-%d')
    

    def make_query(self):
        """Prepare queries to MySql database based on the date interval
        and tables selected
        
        Returns:
            dict -- key: table name, value: sql query
        """

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
        """Execute query on MySql depending on table. It chunks the results
        using the parameter self.chunksize to delimit its size
        
        Arguments:
            table {string} -- table name
        """

        with self.engine_mysql.connect() as con:
             
            result = con.execution_options(stream_results=True).\
                        execute(self.queries[table])
            while True:
                chunk = result.fetchmany(self.chunksize)
                if not chunk:
                    break
                yield chunk


    def select(self, row, by='id'):
        """Easy way to select value from query results based on key
        
        Arguments:
            row {list} -- list with query results
        
        Keyword Arguments:
            by {str} -- column to take the value from (default: {'id'})
        
        Returns:
            depends -- value associated to the query result
        """

        return row[self.columns.index(by)]


    @staticmethod
    def create_filename(table, start_time, timezone, idx):
        """Create filename based on descriptive variables
        
        Arguments:
            table {string} -- table name
            start_time {string} -- timestamp
            timezone {string} -- timezone of the data   
            idx {int} -- unique id from MySql captures  
        
        Returns:
            string -- filename
        """
        
        timezone = timezone.replace('/', '-')

        return '{table}--{start_time}--{timezone}--{idx}'.format(
                                            table=table,
                                            start_time=start_time,
                                            timezone=timezone,
                                            idx=idx
                                            )
    def generate_name(self):
        """Generates the folder name based on the date range. Writes on 
        self.name
        """
        self.name = '{initial_date}--to--{final_date}'.format(
                        initial_date=self.to_mysql_date(self.initial_date),
                        final_date=self.to_mysql_date(self.final_date))


    def create_pathname(self, output_path):
        """Creates path name using the output_path and the self.name
        
        Arguments:
            output_path {string} -- path to save the json files
        
        Returns:
            string -- precise path to save the json files
        """
        self.generate_name()

        return os.path.join(output_path, self.name)

