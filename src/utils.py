"""
This file contains methods that are useful througth the project
- create_mysql_engine 
"""
import sqlalchemy as sa

def create_mysql_engine(echo=False):
    return sa.create_engine("mysql+pymysql://root:root@easywaze-mysql:3306",
                            echo=echo)

def create_postgis_engine(echo=False):
    return sa.create_engine("postgresql://root:root@easywaze-postgis:5432/easywaze",
                            echo=echo)

if __name__ == '__main__':
    pass