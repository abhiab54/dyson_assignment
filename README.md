# dyson_assignment

commands to execute
# build images using docker-compose file
docker-compose -f docker-compose.yaml up -d --build

# remove docker containers
docker-compose -f docker-compose.yaml down

flow of data
1. Read cogiguration from config file (.INI)
2. read csv data from (./data/input) 
3. merge csv data into a pandas dataframe
4. data cleansing
5. transform data in JSON format
6. load JSON data in JSON file at staging layer (./data/staging)
7. connect to postgres database
8. create table comics (IF not exists)
9. load data into comics table

CI/CD
1. github actions to trigger pytest cases stored in tests folder
