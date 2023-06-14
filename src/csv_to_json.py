import configparser 
import os , sys 
import pandas as pd 
import json
import uuid
import psycopg2
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

class ETLRun(): 
    def __init__( self, env) :         
        self.env = env
        self.runid = uuid.uuid1()
        self.config = self.load_config()  

    def load_config(self): 
        config = configparser.ConfigParser()
        filepath  = 'superhero_' + self.env + '_config.ini' 
        config.read( filepath ) 
        config['DEFAULT']['root'] = os.getcwd()
        with open ( filepath , 'w' ) as configfile: 
            config.write(configfile)
        return config 
        
class dq_check: 
    @staticmethod
    def check_file_exists(filename): 
        input_file_match_flag = os.path.exists(filename) 
        return input_file_match_flag 

class pg_db():
    def __init__(self, database, user, password, host, port):
        # connect to the database
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        etl_logger.info("create table comics if not found")
        self.run_sql('./scripts/create_table_comics.sql')

        etl_logger.info("create role postgres if not found")
        self.run_sql('./scripts/create_role_postgres.sql')

        
    def load_data(self, insert_statement, data):
        
        # connect to the database
        conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port= self.port)        
        # create a cursor
        cur = conn.cursor()
        sql = insert_statement
        
        for record in data:
            record = json.dumps(record)
            sql = (insert_statement % record)
            # execute the INSERT statement
            cur.execute(sql)
        # commit the changes to the database
        conn.commit()
        # close the cursor and connection
        cur.close()

    def run_sql(self, sql_statement):
        # Open and read the file as a single buffer
        with open(sql_statement, 'r') as fd:
            sqlFile = fd.read()
            fd.close()
        # connect to the database
        conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port= self.port)        
        # create a cursor
        cur = conn.cursor()
        sql = sqlFile

        # execute the INSERT statement
        cur.execute(sql)
        # commit the changes to the database
        conn.commit()
        # close the cursor and connection
        cur.close()

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler(LOG_FILE):
   file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name, LOG_FILE):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler(LOG_FILE))
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger
        
def merge_datasets(df1,df2,df3):
    # merge csv files into single pandas dataframe
    df = pd.merge(df1, df2,  on=["comicID"], how="left")
    df = pd.merge(df, df3,  on=["characterID"], how="left")
    # df = pd.merge(df, df4,  left_on=["name"], right_on=["Name"], how="left")
    return df
    
def clean_dataset(df):
    df["year"] = pd.to_numeric((df.title.str.split("(", expand = True)[1]
                            .str.split(")", expand = True)[0]), errors='coerce').fillna(0).astype(int)
    df["issueNumber"] = df["issueNumber"].astype(int)
    df["characterID"] = df["characterID"].fillna(0).astype(int)
    df["description"] = df["description"].str.replace("'","")
    df["title"] = df["title"].str.replace("'","")
    df["name"] = df["name"].str.replace("'","")
    return df

def transform_dataset(df):
    j = (df.groupby(['comicID','title','year','issueNumber','description'])
       .apply(lambda x: x[['characterID','name' ]].to_dict('records'))
       .reset_index()
       .rename(columns={0:'Charaters'})
       .to_json(orient='records'))
    j_data = json.loads(j)

    return json.dumps(j_data, indent=4)

def load_data_stg(ds, stg_path):
    with open(stg_path, 'w') as output:
        output.write(ds)


if __name__ == '__main__':
    env = sys.argv[1]
    delim = ","

    # initialise the ETL run
    csv_run = ETLRun(env)

    FORMATTER = logging.Formatter(u"%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    LOG_FILE = csv_run.config['LOG']['log_file']
    LOG_LEVEL = csv_run.config['LOG']['log_level']    
    etl_logger = get_logger("superheroComic",LOG_FILE)
    etl_logger.info("start of ETL run for environment %s", env)

    # import csv files 
    delim = ","
    comic_file = Path(csv_run.config['DATA']['comics_ds'])
    characters_file = Path(csv_run.config['DATA']['characters_ds'])
    characters_comic_file = Path(csv_run.config['DATA']['characters_comic_ds'])
    character_stats_file = Path(csv_run.config['DATA']['character_stats_ds'])
    extra_file = Path(csv_run.config['DATA']['extra_file'])
    stg_file = Path(csv_run.config['STG']['superhero_comic_stg'])
    
    

    etl_logger.info("running pre ETL checks")
    if not dq_check.check_file_exists(comic_file):
        etl_logger.error("comic file dataset missing")
    if not dq_check.check_file_exists(extra_file):
        etl_logger.warning("extra file dataset is missing")
    etl_logger.info("pre ETL checks passed")

    etl_logger.info("Reading all comics data " + str(comic_file))
    # read csv file in pandas dataframe
    df1 = pd.read_csv(comic_file)

    etl_logger.info("Reading comics and characters in those comics data " + str(characters_comic_file))
    # read csv file in pandas dataframe
    df2 = pd.read_csv(characters_comic_file)

    etl_logger.info("Reading characters data " + str(characters_file))
    # read csv file in pandas dataframe
    df3 = pd.read_csv(characters_file)

    etl_logger.info("Reading characters stats data " + str(character_stats_file))
    # read csv file in pandas dataframe
    df4 = pd.read_csv(character_stats_file)

    etl_logger.info("merging CSV files into pandas dataframe ")
    df = merge_datasets(df1,df2,df3)

    etl_logger.info("data cleansing started ")
    df = clean_dataset(df)

    etl_logger.info("data transformation started")
    x_ds = transform_dataset(df)

    etl_logger.info("loading data into staging layer")
    load_data_stg(x_ds, stg_file)

    database=csv_run.config['DB']['database']
    user=csv_run.config['DB']['user']
    password=csv_run.config['DB']['password']
    host=csv_run.config['DB']['host'] 
    port=csv_run.config['DB']['port']

    etl_logger.info("check if staging data exists")
    # read JSON data from file
    if not dq_check.check_file_exists(stg_file):
        etl_logger.error("staging data not found")
        sys.exit()

    with open(stg_file) as f:
        data = json.load(f)

    etl_logger.info("writing data from staging layer to postgre database")
    db = pg_db(database=database, user=user, password=password, host=host, port= port)
    sql = "INSERT INTO comics (comicdata) VALUES ('%s')"
    db.load_data(sql, data)

    etl_logger.info("data load done")
    etl_logger.info("end of ETL")