import pandas as pd

CITY_DATA = 'US City Populations.csv'
AIRPORT_DATA = 'airports.csv'
AIRLINES_DATA = 'airlines.csv'
ROUTES_DATA = 'routes.csv'


city_df = pd.read_csv(CITY_DATA, header=None)
city_df.columns = ['State', 'City', 'Population']

airport_df = pd.read_csv(AIRPORT_DATA, header=None)
airport_df.columns = ['Airport_id', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Latitude',
                      'Longitude', 'Altitude', 'Timezone', 'DST', 'Tz database time zone',
                      'type', 'Source']


airport_df['Airport_id'] = pd.to_numeric(airport_df['Airport_id'])
airport_df.drop(airport_df[airport_df['Airport_id'] == r'\N'].index, inplace=True)


city_names = list(city_df['City'])
airport_df = airport_df[airport_df['City'].isin(city_names)]
airport_df.drop(airport_df[airport_df['Country'] != 'United States'].index, inplace=True)

routes_df = pd.read_csv(ROUTES_DATA, header=None)
routes_df.columns = ['Airline', 'Airline_id', 'Source airport', 'Source_airport_id',
                     'Destination airport', 'Destination_airport_id', 'Codeshare', 'Stops',
                     'Equipment']


routes_df.drop(routes_df[routes_df['Airline_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Source_airport_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Destination_airport_id'] == r'\N'].index, inplace=True)


routes_df['Airline_id'] = pd.to_numeric(routes_df['Airline_id'])
routes_df['Source_airport_id'] = pd.to_numeric(routes_df['Source_airport_id'])
routes_df['Destination_airport_id'] = pd.to_numeric(routes_df['Destination_airport_id'])

airport_ids = list(airport_df['Airport_id'])
routes_df = routes_df[routes_df['Source_airport_id'].isin(airport_ids)]
routes_df = routes_df[routes_df['Destination_airport_id'].isin(airport_ids)]



if __name__ == '__main__':
    pass
