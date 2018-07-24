from export import Export
import sqlalchemy as sa
import os
import errno
import shutil
import json


class Json(Export):
    
    def to_json(self, output_path='app/dumps/json/'):
        
        self.output_path = self.create_pathname(output_path)

        # Create path if it does not exists
        try:
            os.makedirs(self.output_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        # Dump json

        for table in self.tables:
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


    


#a = To_json().export()