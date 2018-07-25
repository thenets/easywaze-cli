'''
This file instanciate a child class to export files from the MySql database
to json.

It can be imported and used as a parent class to any other exportation method.

It has the following variables that can be used:

# Export
self.tables -- list :: selected tables to be exported
self.time_range -- int :: range of time given the final date
self.final_date -- datetime :: last day to be exported
self.initial_date  -- datetime :: first day to be exported
self.chunksize -- int :: maximum number of files in one operation
self.output_path -- string :: dump path 
self.logging -- bollean :: activate logging
self.columns -- list :: columns at MySql database
self.queries -- list :: list of sql queries to select data given the time range
self.engine_mysql -- slalchemy.engine :: engine connected to MySql
self.name -- string :: name of the export base on the time range

'''
import sqlalchemy as sa
import os
import errno
import shutil
import json
import fire
import tqdm

# Local Imports
from prepare import Export


class Json(Export):

    def to_json(self):
        """Dump files from MySql in json format. 
            It saves the files at:
                'app/dumps/json/<initial-date>--to--<final-date>/'
            with the name:
                '{table}--{start_time}--{timezone}--{idx}.json'
        Keyword Arguments:
            output_path {str} -- dump path (default: {'app/dumps/json/'})
        """

        self.output_path = self.output_path + 'json/'
        self.output_path = self.create_pathname(self.output_path)

        # Create path if it does not exists
        try:
            os.makedirs(self.output_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        # Dump json

        for table in tqdm.tqdm(self.tables, desc='Dumping data to json'):
            for chunk in self.perform_query(table):
                for row in chunk:
                    filename = self.create_filename(
                                            table, 
                                            self.select(row, by='start_time'),
                                            self.select(row, by='timezone'),
                                            self.select(row, by='id'))
                    json.dump(
                        json.loads(
                            self.select(row, by='raw_json')
                            ),
                        open(
                            os.path.join(self.output_path, filename) + '.json', 
                            'w', 
                            encoding='utf8'), 
                        ensure_ascii=False)

    def clear_json(self):

        shutil.rmtree(self.output_path)

if __name__ == '__main__':

    fire.Fire(Json)