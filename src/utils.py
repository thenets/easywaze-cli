"""
This file contains methods that are useful througth the project
- create_mysql_engine 
"""
import sqlalchemy as sa

def create_mysql_engine():
    return sa.create_engine("mysql+pymysql://root:root@easywaze-mysql:3306")

def create_postgis_engine():
    return sa.create_engine("postgresql://root:root@easywaze-postgis:5432/easywaze",
                            echo=True)

if __name__ == '__main__':
    pass