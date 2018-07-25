'''
This file instanciate a child class to export files from the MySql database
a Postgre + GIS database.

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

# Postgis
self.tables_postgis -- dict :: metadata of tables created
'''
import sqlalchemy as sa
from glob import glob
import json
from dateutil import tz
import datetime
from sqlalchemy import (VARCHAR, Text, BigInteger, INTEGER, TIMESTAMP, JSON, 
                        BOOLEAN, Column, Float, ForeignKey, DateTime, select)
from geoalchemy2 import Geometry
import fire
import tqdm

# Local imports
from app.utils import create_postgis_engine
from prepare import Export
from to_json import Json

class Postgis(Json):

    def init_postigis(self):
        """Creates all the tables and schema.
        The table schema is based on the 
        [WazeCCPProcessor](github.com/LouisvilleMetro/WazeCCPProcessor)
        project in order to achieve maximum compatibility.

        It creates a schema: `waze`
        and the tables:

        - jams
        - irregularities
        - alerts
        - roads
        - alert_types
        - coordinates
        - coordinate_type
        """

        if self.force_export:
            try:
                self.engine_postgis.execute('DROP SCHEMA waze CASCADE')
            except:
                pass

        try:
            self.engine_postgis.execute("CREATE SCHEMA waze") #create db
        except:
            pass

        metadata = sa.MetaData(self.engine_postgis)
        self.tables_postgis = {}

        metadata = sa.MetaData(self.engine_postgis)
        
        for table in self.tables:
            self.tables_postgis[table + 'raw'] = sa.Table(
                table, metadata,
                Column("id",                         INTEGER, nullable=False),
                Column("timestamp",                  DateTime, nullable=False),
                Column("city",                       Text, nullable=False),
                Column("raw_json",                   Text, nullable=False),
                schema='raw_import',)


        self.tables_postgis['alerts'] = sa.Table(
            'alerts', metadata,
            Column("id",                              INTEGER,
                                                      primary_key=True,),
            Column("uuid",                            Text, nullable=False,
                                                      index=True),
            Column("pub_millis",                      BigInteger, nullable=False),
            Column("pub_utc_date",                    TIMESTAMP, index=True),
            Column("road_type",                       INTEGER, index=True),
            Column("location",                        JSON),
            Column("location_geo",                    Geometry('POINT')),
            Column("street",                          Text),
            Column("city",                            Text),
            Column("country",                         Text),
            Column("magvar",                          INTEGER),
            Column("reliability",                     INTEGER, index=True),
            Column("report_description",              Text),
            Column("report_rating",                   INTEGER),
            Column("confidence",                      INTEGER, index=True),
            Column("type",                            Text, index=True),
            Column("subtype",                         Text, index=True),
            Column("report_by_municipality_user",     BOOLEAN),
            Column("thumbs_up",                       INTEGER, index=True),
            Column("jam_uuid",                        Text, index=True),
            Column("datafile_id",                     BigInteger, 
                                                      nullable=False,
                                                      index=True), 
            schema='waze',)

        self.tables_postgis['jams'] = sa.Table(
            'jams', metadata,
            Column("id",                              INTEGER, 
                                                      primary_key=True,
                                                      nullable=False),
            Column("uuid",                            Text,
                                                      nullable=False,
                                                      index=True),
            Column("pub_millis",                      BigInteger,
                                                      nullable=False),
            Column("pub_utc_date",                    TIMESTAMP,
                                                      index=True),
            Column("start_node",                      Text),
            Column("end_node",                        Text),
            Column("road_type",                       INTEGER),
            Column("street",                          Text,
                                                      index=True),
            Column("city",                            Text),
            Column("country",                         Text),
            Column("delay",                           INTEGER, index=True),
            Column("speed",                           Float, index=True),
            Column("speed_kmh",                       Float, index=True),
            Column("length",                          INTEGER, index=True),
            Column("turn_type",                       Text),
            Column("level",                           INTEGER, index=True),
            Column("blocking_alert_id",               Text),
            Column("line",                            JSON),
            Column("line_geo",                        Geometry('LINESTRING')),
            Column("type",                            Text, index=True),
            Column("turn_line",                       JSON),
            Column("turn_line_geo",                   Geometry('LINESTRING')),
            Column("datafile_id",                     BigInteger,
                                                      nullable=False,
                                                      index=True),
            schema='waze',)   

        self.tables_postgis['irregularities'] = sa.Table(
            'irregularities', metadata,
            Column("id",                              INTEGER,
                                                      primary_key=True,
                                                      nullable=False),
            Column("uuid",                            Text,
                                                      nullable=False,
                                                      index=True),
            Column("detection_date_millis",           BigInteger, nullable=False),
            Column("detection_date",                  Text),
            Column("detection_utc_date",              TIMESTAMP, index=True),
            Column("update_date_millis",              BigInteger,nullable=False),
            Column("update_date",                     Text),
            Column("update_utc_date",                 TIMESTAMP, index=True),
            Column("street",                          Text, index=True),
            Column("city",                            Text),
            Column("country",                         Text),
            Column("is_highway",                      BOOLEAN),
            Column("speed",                           Float, index=True),
            Column("regular_speed",                   Float, index=True),
            Column("delay_seconds",                   INTEGER, index=True),
            Column("seconds",                         INTEGER, index=True),
            Column("length",                          INTEGER, index=True),
            Column("trend",                           INTEGER, index=True),
            Column("type",                            Text, index=True),
            Column("severity",                        Float, index=True),
            Column("jam_level",                       INTEGER, index=True),
            Column("drivers_count",                   INTEGER),
            Column("alerts_count",                    INTEGER, index=True),
            Column("n_thumbs_up",                     INTEGER, index=True),
            Column("n_comments",                      INTEGER),
            Column("n_images",                        INTEGER),
            Column("line",                            JSON),
            Column("line_geo",                        Geometry('LINESTRING')),
            Column("cause_type",                      Text),
            Column("start_node",                      Text),
            Column("end_node",                        Text),
            Column("datafile_id",                     BigInteger,
                                                      nullable=False,
                                                      index=True),
            schema='waze',)   

        self.tables_postgis['coordinate_type'] = sa.Table(
            'coordinate_type', metadata,
            Column("id",                              INTEGER,
                                                      primary_key=True,
                                                      nullable=False),
            Column("type_name",                       Text,
                                                      nullable=False),
            schema='waze',)   

        self.tables_postgis['coordinates'] = sa.Table(
            'coordinates', metadata,
            Column("id",                              VARCHAR(40),
                                                      primary_key=True,
                                                      nullable=False),
            Column("latitude",                        Float(8), nullable=False),
            Column("longitude",                       Float(8), nullable=False),
            Column("order",                           INTEGER, nullable=False),
            Column("jam_id",                          INTEGER,
                                                      ForeignKey('waze.jams.id')),
            Column("irregularity_id",                 INTEGER,
                                                      ForeignKey('waze.irregularities.id')),
            Column("alert_id",                        INTEGER,
                                                      ForeignKey('waze.alerts.id')),
            Column("coordinate_type_id",              INTEGER,
                                                      ForeignKey('waze.coordinate_type.id')),
            schema='waze',) 

        self.tables_postgis['roads'] = sa.Table(
            'roads', metadata,
            Column("id",                              INTEGER,
                                                      primary_key=True,
                                                      nullable=False),
            Column("value",                           INTEGER, nullable=False),
            Column("name",                            VARCHAR(100),
                                                      nullable=False),
            schema='waze',) 

        self.tables_postgis['alert_types'] = sa.Table(
            'alert_types', metadata,
            Column("id",                              INTEGER,
                                                      primary_key=True,
                                                      nullable=False),
            Column("type",                          Text, nullable=False),
            Column("subtype",                       Text),
            schema='waze',)


        metadata.create_all(self.engine_postgis)
        
        try:
            self.engine_postgis.execute(
                """ALTER TABLE waze.roads
                    ADD CONSTRAINT roads_unique_combo UNIQUE(value, name);""")
        except sa.exc.ProgrammingError:
            pass

        try:
            self.engine_postgis.execute(
                """ALTER TABLE waze.alert_types
                    ADD CONSTRAINT alert_types_unique_combo 
                        UNIQUE(type, subtype);""")
        except sa.exc.ProgrammingError:
            pass

        # Insert elements
        with self.engine_postgis.connect() as conn:
            try:
                conn.execute(self.tables_postgis['coordinate_type'].insert(),
                        [{'id': 1, 'type_name': 'Line'},
                        {'id': 2, 'type_name': 'Turn Line'},
                        {'id': 3, 'type_name': 'Location'}]
                        )
            except sa.exc.IntegrityError:
                pass
            
            try:
                conn.execute(self.tables_postgis['roads'].insert(),
                         [{'value': 1, 'name': 'Streets'},
                         {'value': 2, 'name': 'Primary Street'},
                         {'value': 3, 'name': 'Freeways'},
                         {'value': 4, 'name': 'Ramps'},
                         {'value': 5, 'name': 'Trails'},
                         {'value': 6, 'name': 'Primary'},
                         {'value': 7, 'name': 'Secondary'},
                         {'value': 8, 'name': '4X4 Trails'},
                         {'value': 9, 'name': 'Walkway'},
                         {'value': 10, 'name': 'Pedestrian'},
                         {'value': 11, 'name': 'Exit'},
                         {'value': 12, 'name': '?'},
                         {'value': 13, 'name': '?'},
                         {'value': 14, 'name': '4X4 Trails'},
                         {'value': 15, 'name': 'Ferry crossing'},
                         {'value': 16, 'name': 'Stairway'},
                         {'value': 17, 'name': 'Private road'},
                         {'value': 18, 'name': 'Railroads'},
                         {'value': 19, 'name': 'Runway/Taxiway'},
                         {'value': 20, 'name': 'Parking lot road'},
                         {'value': 21, 'name': 'Service road'}])
            except sa.exc.IntegrityError:
                pass

            try:
                conn.execute(self.tables_postgis['alert_types'].insert(),
        [{'type': 'ACCIDENT', 'subtype': 'ACCIDENT_MINOR'},
        {'type': 'ACCIDENT', 'subtype': 'ACCIDENT_MAJOR'},
        {'type': 'ACCIDENT', 'subtype': 'NO_SUBTYPE'},
        {'type': 'JAM', 'subtype': 'JAM_MODERATE_TRAFFIC'},
        {'type': 'JAM', 'subtype': 'JAM_HEAVY_TRAFFIC'},
        {'type': 'JAM', 'subtype': 'JAM_STAND_STILL_TRAFFIC'},
        {'type': 'JAM', 'subtype': 'JAM_LIGHT_TRAFFIC'},
        {'type': 'JAM', 'subtype': 'NO_SUBTYPE'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_SHOULDER'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_OBJECT'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_POT_HOLE'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_ROAD_KILL'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_SHOULDER_CAR_STOPPED'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_SHOULDER_ANIMALS'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_SHOULDER_MISSING_SIGN'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_FOG'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_HAIL'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_HEAVY_RAIN'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_HEAVY_SNOW'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_FLOOD'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_MONSOON'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_TORNADO'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_HEAT_WAVE'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_HURRICANE'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_WEATHER_FREEZING_RAIN'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_LANE_CLOSED'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_OIL'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_ICE'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_CONSTRUCTION'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_CAR_STOPPED'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'HAZARD_ON_ROAD_TRAFFIC_LIGHT_FAULT'},
        {'type': 'WEATHERHAZARD/HAZARD', 'subtype': 'NO_SUBTYPE'},
        {'type': 'MISC', 'subtype': 'NO_SUBTYPE'},
        {'type': 'CONSTRUCTION', 'subtype': 'NO_SUBTYPE'},
        {'type': 'ROAD_CLOSED', 'subtype': 'ROAD_CLOSED_HAZARD'},
        {'type': 'ROAD_CLOSED', 'subtype': 'ROAD_CLOSED_CONSTRUCTION'},
        {'type': 'ROAD_CLOSED', 'subtype': 'ROAD_CLOSED_EVENT'},])
            except sa.exc.IntegrityError:
                pass

        # Crate indexes

    def parse_json_name(self, raw_path):
        """Parse name of json to get data
        
        Arguments:
            raw_path {string} -- json name as <>.json
        
        Returns:
            str, str, str -- timestamp, datafile_id, timezone
        """
        table, timestamp, timezone, datafile_id = (raw_path.
                                                replace('.json', '').
                                                split('/')[-1].split('--'))

        timezone = timezone.replace('-', '/')

        return timestamp, datafile_id, timezone
    
    def prepare_alerts(self, raws, timestamp, datafile_id, timezone):
        """Prepare data to insert at Postgis
        
        Arguments:
            raws {list} -- list of json load data
            timestamp {str} -- datetime string
            datafile_id {str} -- capture id
            timezone {str} -- timezone
        
        Returns:
            list -- list of dict ready to insert
        """
        new = []
        for raw in raws:
            new.append({
            "uuid":                         raw.get("uuid"),
            "pub_millis":                   raw.get("pubMillis"),
            "pub_utc_date":                 datetime.datetime.strptime(timestamp,
                                            '%Y-%m-%d %H:%M:%S'),
            "road_type":                    raw.get("roadType"),
            "location":                     raw.get("location"),
            "street":                       raw.get("street"),
            "city":                         raw.get("city"),
            "country":                      raw.get("country"),
            "magvar":                       raw.get("magvar"),
            "reliability":                  raw.get("reliability"),
            "report_description":           raw.get("reportDescription"),
            "report_rating":                raw.get("reportRating"),
            "confidence":                   raw.get("confidence"),
            "type":                         raw.get("type"),
            "subtype":                      raw.get("subtype"),
            "report_by_municipality_user":  raw.get("reportByMunicipalityUser"),
            "thumbs_up":                    raw.get("nThumbsUp" ),
            "jam_uuid":                     raw.get("jamUuid"),
            "datafile_id":                  datafile_id,
            })
        return new
    
    def prepare_jams(self, raws, timestamp, datafile_id, timezone):
        """Prepare data to insert at Postgis
        
        Arguments:
            raws {list} -- list of json load data
            timestamp {str} -- datetime string
            datafile_id {str} -- capture id
            timezone {str} -- timezone
        
        Returns:
            list -- list of dict ready to insert
        """
        new = []
        for raw in raws:
            new.append({
            "uuid":                raw.get("uuid"),
            "pub_millis":          raw.get("pubMillis"),        
            "pub_utc_date":        datetime.datetime.strptime(timestamp,
                                            '%Y-%m-%d %H:%M:%S'),
            "start_node":          raw.get("startNode"),            
            "end_node":            raw.get("endNode"),        
            "road_type":           raw.get("roadType"),            
            "street":              raw.get("street"),        
            "city":                raw.get("city"),
            "country":             raw.get("country"),        
            "delay":               raw.get("delay"),        
            "speed":               raw.get("speed"),        
            "speed_kmh":           raw.get("speed"),            
            "length":              raw.get("length"),        
            "turn_type":           raw.get("turnType"),           
            "level":               raw.get("level"),        
            "blocking_alert_id":   raw.get("blockingAlertId"),               
            "line":                raw.get("line"),
            "type":                raw.get("type"),
            "turn_line":           raw.get("turnLine"),       
            "datafile_id":         datafile_id
            }) 
        return new             

    def prepare_irregularities(self, raws, timestamp, datafile_id, timezone):
        """Prepare data to insert at Postgis
        
        Arguments:
            raws {list} -- list of json load data
            timestamp {str} -- datetime string
            datafile_id {str} -- capture id
            timezone {str} -- timezone
        
        Returns:
            list -- list of dict ready to insert
        """
        new = []
        from_zone = tz.tzutc()
        to_zone = tz.gettz(timezone)
        for raw in raws:
            new.append({
            "uuid":                           raw.get("id"), 
            "detection_date_millis":          raw.get("detectionDateMillis"), 
            "detection_date":                 raw.get("detectionDate"),
            "detection_utc_date":             datetime.datetime.
                                              strptime(raw.get('detectionDate'),
                                                    '%a %b %d %H:%M:%S %z %Y').
                                              replace(tzinfo=from_zone).
                                              astimezone(to_zone),
            "update_date_millis":             raw.get("updateDateMillis"),
            "update_date":                    raw.get("updateDate"),
            "update_utc_date":                datetime.datetime.
                                              strptime(raw.get('updateDate'),
                                                    '%a %b %d %H:%M:%S %z %Y').
                                              replace(tzinfo=from_zone).
                                              astimezone(to_zone), 
            "street":                         raw.get("street"),
            "city":                           raw.get("city"),
            "country":                        raw.get("country"),
            "is_highway":                     raw.get("isHighway"),
            "speed":                          raw.get("speed"),
            "regular_speed":                  raw.get("regularSpeed"),
            "delay_seconds":                  raw.get("delaySeconds"),
            "seconds":                        raw.get("seconds"),
            "length":                         raw.get("length"),
            "trend":                          raw.get("trend"),
            "type":                           raw.get("type"),
            "severity":                       raw.get("severity"),
            "jam_level":                      raw.get("jamLevel"),
            "drivers_count":                  raw.get("driversCount"),
            "alerts_count":                   raw.get("alertsCount"),
            "n_thumbs_up":                    raw.get("nThumbsUp"),
            "n_comments":                     raw.get("nComments"),
            "n_images":                       raw.get("nImages"),
            "line":                           raw.get("line"),
            "cause_type":                     raw.get("causeType"),
            "start_node":                     raw.get("startNode"),
            "end_node":                       raw.get("endNode"),
            "datafile_id":                    datafile_id
            }) 
        return new 

    def read_json(self, files, table):
        """Read json data given a table name
        
        Arguments:
            files {list} -- list of files paths
            table {str} -- table name
        
        Returns:
            list or False -- list of json dump data or False if no data
        """
        data = []
        
        if len(files):
            for raw_path in files:
                timestamp, datafile_id, timezone = self.parse_json_name(
                                                                raw_path)
                data = data + (
                        self.prepare[table](json.load(open(raw_path,
                                                    'r', 
                                                    encoding='utf8')),
                                            timestamp, 
                                            datafile_id,
                                            timezone))
            
            return data
        
        else:
            return False

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]
       
    def load_json(self):
        """Load json to Postgis. It chunks data based on self.chunksize
        """
        for table in tqdm.tqdm(self.tables, desc='Loading data to Postgis'):
            files = glob(self.output_path + '/' + table + '*.json')
            
            with self.engine_postgis.connect() as conn:
                for chunk in self.chunks(files, self.chunksize):
                    data = self.read_json(chunk, table)
                    if data:
                        conn.execute(self.tables_postgis[table].insert(), data)

        self.update_geometry_fields()

    def check_existent_data(self):

        existent_ids = {}
        with self.engine_postgis.connect() as conn:
            for table in self.tables:
                res = conn.execute(
                        select([self.tables_postgis[table].c.datafile_id]))
                existent_ids[table] = [row[0] for row in res]

        return existent_ids

    def update_geometry_fields(self):

        for table in self.tables:

            if table == 'alerts':

                self.engine_postgis.execute(
                    """
                    update waze.alerts
                    set location_geo  = (ST_MakePoint(
                                        CAST(location->>'x' as float),
                                        CAST(location->>'y'  as float)))
                    where location_geo is null      
                    """
                )
            
            elif table == 'jams':

                self.engine_postgis.execute(
                    """
                    update waze.jams
                    set line_geo = (select ST_MakeLine(points)
				                    from (
					                select ST_MakePoint(
                                        cast(json_array_elements(line)->>'x' 
                                                as float), 
							            cast(json_array_elements(line)->>'y' 
                                                as float)) as points) as a)	
                    where (line_geo is null) and 
                          (line->0 is not null);     
                    """
                )

                self.engine_postgis.execute(
                    """
                    update waze.jams
                    set turn_line_geo = (select ST_MakeLine(points)
				                        from (select ST_MakePoint(
                                            CAST(json_array_elements(turn_line)
                                                ->>'x' as float), 
							                cast(json_array_elements(turn_line)
                                            ->>'y' as float)) as points) as a)	
                    where (turn_line_geo is null) and 
                          (turn_line->0 is not null);    
                    """
                )

            elif table == 'irregularities':
                
                self.engine_postgis.execute(
                    """
                    update waze.irregularities
                    set line_geo = (select ST_MakeLine(points)
				                        from (select ST_MakePoint(
                                            CAST(json_array_elements(line)
                                                ->>'x' as float), 
							                cast(json_array_elements(line)
                                            ->>'y' as float)) as points) as a)	
                    where (line_geo is null) and 
                          (line->0 is not null);    
                    """
                )


    def to_postgis(self):
        """Prepare Postgis database and insert data. It also erases the
        json dumped files.
        """
        self.engine_postgis = create_postgis_engine(logging=self.logging)
        self.init_postigis()

        # make queries strings 
        # TODO: modify it according to data on postgre
        # self.queries = self.make_query()

        self.prepare = {'alerts': self.prepare_alerts,
                        'jams': self.prepare_jams,
                        'irregularities': self.prepare_irregularities,}

        self.get_new_data(self.check_existent_data())

        self.to_json()

        self.load_json()

        self.clear_json()

if __name__ == '__main__':

    fire.Fire(Postgis)