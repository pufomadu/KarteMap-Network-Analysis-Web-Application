# Import all necessary packages
import pandas as pd
from network import Network
from geopy.distance import lonlat, distance 

#Import csv files
CITY_DATA = 'US City Populations.csv'
AIRPORT_DATA = 'airports.csv'
AIRLINES_DATA = 'airlines.csv'
ROUTES_DATA = 'routes.csv'
IMAGES_DATA = 'states_images.csv'

#This file is used to import data and contain methods that will be used in the main file

#Read data containing the URL for all images
images_df = pd.read_csv(IMAGES_DATA)



# reading and building dataset
city_df = pd.read_csv(CITY_DATA, header=None)
city_df.columns = ['State', 'City', 'Population']
city_names = list(city_df['City'])

airport_df = pd.read_csv(AIRPORT_DATA, header=None)
airport_df.columns = ['Airport_id', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Latitude',
                      'Longitude', 'Altitude', 'Timezone', 'DST', 'Tz database time zone',
                      'type', 'Source']


airport_df['Airport_id'] = pd.to_numeric(airport_df['Airport_id'])
airport_df.drop(airport_df[airport_df['Airport_id'] == r'\N'].index, inplace=True)

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

data = pd.merge(routes_df, airport_df, how = 'left', left_on='Source_airport_id', right_on='Airport_id')
data = data.rename(columns = {'Name': 'Source_Airport', 'City': 'Source_City', 'Latitude': 'Source_Latitude', 'Longitude': 'Source_Longitude', 'Altitude': 'Source_Altitude'})

finalData = pd.merge(data, airport_df, how = 'left', left_on='Destination_airport_id', right_on='Airport_id')
finalData = finalData.rename(columns = {'Name': 'Destination_Airport', 'City': 'Destination_City', 'Latitude': 'Destination_Latitude', 'Longitude': 'Destination_Longitude', 'Altitude': 'Destination_Altitude'})

finalData['Distance'] = finalData.apply(lambda row: distance((lonlat(row['Source_Longitude'], row['Source_Latitude'])),
                                                             (lonlat(row['Destination_Longitude'],
                                                                     row['Destination_Latitude']))).miles, axis=1)
#Transform final data to csv file
finalData.to_csv('~/Desktop/finalData.csv')

#########################################################################################

# Building network of airports to help calculate shortest path
apts = list()
distances = dict()

for _,r in finalData.iterrows():
    apt_s = r['Source_Airport']
    apt_d = r['Destination_Airport']
    distance = float(r['Distance'])

    ## build the list of airports
    if apt_s not in apts:
        apts.append(apt_s)

    if apt_d not in apts:
        apts.append(apt_d)  

    ## build the dictionary based on airports distances
    if apts.index(apt_s) not in distances.keys():
        distances[apts.index(apt_s)] = {apts.index(apt_d): distance}
    if apts.index(apt_d) not in distances[apts.index(apt_s)].keys():
        distances[apts.index(apt_s)][apts.index(apt_d)] = distance

def buildNet():
    ## build network
    network = Network()
    network.add_nodes(apts)
    for connection in distances.items():
        frm = apts[connection[0]]
        for connection_to in connection[1].items():
            network.add_edge(frm, apts[connection_to[0]], connection_to[1])
    return network


#################################################################################################

#method to get state from source or destination airport from multiple dataset to be used to get image
def return_state(airPort):
    city = finalData.loc[finalData['Source_Airport'] == airPort, "Source_City"].values[0]
    state = city_df.loc[city_df['City'] == city, "State"].values[0]
    return state
    
    
# method to return state seal url 
def return_seal_url(airport):
    stateSeal_url = [images_df.loc[images_df['state'] == return_state(airport), 'state_seal_url'].values[0]]
    return stateSeal_url


# method to return state skyline image 
def return_skyline_url(airport):
    skylinebackground_url = [images_df.loc[images_df['state'] == return_state(airport), 'skyline_background_url'].values[0]]
    return skylinebackground_url


if __name__ == '__main__':
    pass
