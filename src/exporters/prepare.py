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
self.output_path -- string :: dump path 
self.logging -- boolean :: activate logging
self.force_export -- boolean :: If true, export all
self.columns -- list :: columns at MySql database
self.queries -- list :: list of sql queries to select data given the time range
self.engine_mysql -- slalchemy.engine :: engine connected to MySql
self.name -- string :: name of the export base on the time range

'''

from datetime import datetime, timedelta
import sqlalchemy as sa
import os
import sys
from sqlalchemy import (VARCHAR, Text, BigInteger, INTEGER, TIMESTAMP, JSON, 
                        BOOLEAN, Column, Float, ForeignKey)
import logging
import tqdm

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
                chunksize=10000,
                output_path='app/dumps/',
                logging=False,
                force_export=False
                ):
        
        self.tables = tables
        self.time_range = time_range
        self.final_date = (datetime.now() + timedelta(days=1)
                             if final_date is None 
                             else self.to_datetime(final_date))
        self.initial_date = (datetime.now() - timedelta(days=time_range)
                                if time_range is not None 
                                else self.to_datetime(initial_date))
        self.chunksize = chunksize
        self.output_path = output_path
        self.logging = logging
        self.force_export = force_export

        self.columns = ['id', 
                        'start_time_millis', 
                        'end_time_millis', 
                        'start_time', 
                        'end_time', 
                        'timezone', 
                        'raw_json']

        self.queries = self.make_query_from_date()

        # Use waze db
        self.engine_mysql = create_mysql_engine(logging=self.logging)
        self.engine_mysql.execute('USE waze')

    @staticmethod
    def to_datetime(date):
        """Converts MySql from string to datetime
        
        Arguments:
            date {string} -- 
        
        Returns:
            datetime -- datetime on '%Y-%m-%d'
        """
        return datetime.strptime(date, '%Y-%m-%d')

    @staticmethod
    def to_mysql_date(date):
        """Converts from datetime to string 
        
        Arguments:
            date {datetime} -- 
        
        Returns:
            str -- date on '%Y-%m-%d'
        """
        return datetime.strftime(date, '%Y-%m-%d')
    

    def make_query_from_date(self, column='*'):
        """Prepare queries to MySql database based on the date interval
        and tables selected
        
        Returns:
            dict -- key: table name, value: sql query
        """

        query = {}
        for table in self.tables:
            query[table] = """
                                SELECT {column}
                                FROM `{table}`
                                WHERE `start_time`
                                    BETWEEN '{initial_date}'
                                    AND '{final_date}'
                        """.format(
                            table=table,
                            initial_date=self.to_mysql_date(self.initial_date),
                            final_date=self.to_mysql_date(self.final_date),
                            column=column
                        )

        return query


    def get_non_existent_ids(self, existent_ids, query_ids):
        """Get the ids that where not exported yet
        
        Arguments:
            existent_ids {dict} -- dict of existent ids by table. Or already
            exported.
            query_ids {dict} -- dict of query ids by table
        
        Returns:
            dict -- dict of non existent ids by table
        """
        non_existent = {}

        for table in self.tables:
            exist = set(existent_ids[table])
            query = set(query_ids[table])
            non_existent[table] = list(query - query.intersection(exist))

        return non_existent

    def make_query_from_ids(self, ids):
        """Prepare queries to MySql database based on a id list
        
        Returns:
            dict -- key: table name, value: sql query
        """

        # Check if all data was exported. If so, exit program
        
        query = {}
        to_remove = []

        for table in self.tables:
            if len(ids[table]):
                query[table] = """
                        SELECT *
                        FROM `{table}`
                        WHERE `id`
                            IN ({ids})
                """.format(
                    table=table,
                    ids=','.join(map(str, ids[table]))
                )
            else:
                to_remove.append(table)

        self.tables = [e for e in self.tables if e not in to_remove]

        if len(self.tables) == 0:
            self.exit('all-data-already-exported')

        return query

    def get_new_data(self, existing_ids):

        self.queries = self.make_query_from_date(column='id')

        query_ids = {}
        for table in tqdm.tqdm(self.tables, desc='Checking repeated data'):
            for i, chunk in enumerate(self.perform_query(table)):
                if i:
                    query_ids[table] = query_ids[table] +\
                                     [self.select('id') for row in chunk]
                else:
                    query_ids[table] = [row[0] for row in chunk]

        non_existing_ids = self.get_non_existent_ids(existing_ids, query_ids)

        self.queries = self.make_query_from_ids(non_existing_ids)


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

    def exit(self, reason):

        if reason == 'all-data-already-exported':
            print('All data already exported')
            sys.exit(0)
        else:
            sys.exit(0)


