from to_json import Json
from to_postgis import Postgis
import fire


class Call(Postgis):
    pass

if __name__ == '__main__':
    fire.Fire(Call)