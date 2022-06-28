from datetime import datetime
import pandas as pd
from urllib.request import urlopen
from meteostat import Point, Daily
import os
import numpy as np
import requests



def postcode_corrector(postcode):
    '''The function accepts a UK postcode sting and returns corrected postcode with space in it. For example NW118NP --> NW11 8NP'''
    suffix = postcode[-3:]
    prefix = postcode.replace(suffix, "")
    postcode = prefix + ' ' + suffix
    return postcode


def geocoder(postcode):
    '''This function accepts a UK postcode in format NW11 8NP and returns latitude and longitude values for that postcode using nominatim.openstreetmap.org API'''
    geocode_api_url_prefix = 'https://nominatim.openstreetmap.org/search/'
    geocode_api_url_sufix = '?format=json'
    url = geocode_api_url_prefix + postcode + geocode_api_url_sufix
    response = requests.get(url).json()
    if response:
        return response[0]['lat'], response[0]['lon']
    else:
        return 'Not found', 'Not found'


def temperature_fetcher(date, Latitude, Longitude):
    '''This function accepts three parameters, Date, Latitude and Longitude and returns the average day temperature from Meteostat API'''
    if Latitude != "Not found":
        Latitude = float(Latitude)
        Longitude = float(Longitude)
        start = date
        end = date
        location = Point(Latitude, Longitude)
        data = Daily(location, start, end)
        data = data.fetch()
        df = pd.DataFrame(data)
        if len(data) != 0:
            temp = data.iloc[0]['tavg']
            return temp
        else:
            'No data'
    else:
        return 'geocode missing'


def bandfinder(Delivery_day_Temperature):
    '''This function accepts a temprature value as float and returns a character which repesents temperature range band'''
    if Delivery_day_Temperature:
        if Delivery_day_Temperature != 'geocode missing':
            if Delivery_day_Temperature >= -10 and Delivery_day_Temperature <= 4:
                ret = 'A'
                return ret
            elif Delivery_day_Temperature < 10:
                ret = 'B'
                return ret
            elif Delivery_day_Temperature < 16:
                ret = 'C'
                return ret
            elif Delivery_day_Temperature < 19:
                ret = 'D'
                return ret
            elif Delivery_day_Temperature < 24:
                ret = 'E'
                return ret
            elif Delivery_day_Temperature < 30:
                ret = 'F'
                return ret
            elif Delivery_day_Temperature <= 35:
                ret = 'G'
                return ret


if __name__ == "__main__":
    BOXES_INPUT = os.getenv('BOXES_INPUT')
    TEMPERATURE_INPUT = os.getenv('TEMPERATURE_INPUT')
    RESULT_OUTPUT = os.getenv('RESULT_OUTPUT')
    boxes_df = pd.read_csv(BOXES_INPUT)
    temperature_range_df = pd.read_csv(TEMPERATURE_INPUT, index_col=False)

    temperature_range_df['Temperature_band'] = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    boxes_df['delivery_date'] = pd.to_datetime(boxes_df['delivery_date'])

    boxes_df['corrected Postcode'] = boxes_df['postcode'].apply(
        postcode_corrector)

    boxes_df['Latitude'], boxes_df['Longitude'] = zip(*boxes_df['corrected Postcode'].apply(geocoder))

    boxes_df['Delivery_day_Temperature'] = boxes_df[['delivery_date',
                                                     'Latitude', 'Longitude']].apply(lambda x: temperature_fetcher(*x), axis=1)

    boxes2_df = boxes_df.copy()

    boxes3_df = boxes2_df[['box_id', 'delivery_date', 'Box Size',
                           'postcode', 'Delivery_day_Temperature', 'Cool Pouch Size']]

    boxes3_df['Delivery_day_Temperature_adj'] = boxes3_df['Delivery_day_Temperature'].replace(
        {'None': np.nan, 'geocode missing': np.nan})

    func = boxes3_df.fillna(np.nan).groupby('delivery_date').agg('mean')[
        'Delivery_day_Temperature_adj']

    boxes3_df['Delivery_day_Temperature_adj'] = boxes3_df[['delivery_date', 'Delivery_day_Temperature_adj']].apply(
        lambda x: func[x['delivery_date']] if np.isnan(x['Delivery_day_Temperature_adj']) else x['Delivery_day_Temperature_adj'], axis=1)

    boxes3_df['Delivery_day_Temperature_adj'] = boxes3_df['Delivery_day_Temperature_adj'].round(
        decimals=1)

    boxes3_df['Temperature_band'] = boxes3_df['Delivery_day_Temperature_adj'].apply(
        bandfinder)

    boxes3_df['Cool_Pouches_Needed'] = ''

    for index, row in boxes3_df.iterrows():
        pouch = str(row['Cool Pouch Size'])
        temp_band = row['Temperature_band']
        if temp_band:
            boxes3_df['Cool_Pouches_Needed'][index] = int(temperature_range_df.loc[(
                temperature_range_df['Temperature_band'] == temp_band), pouch])

    boxes3_df = boxes3_df[['box_id', 'Box Size', 'delivery_date', 'postcode', 'Delivery_day_Temperature',
                           'Cool Pouch Size', 'Delivery_day_Temperature_adj', 'Cool_Pouches_Needed']]

    boxes3_df.to_csv(RESULT_OUTPUT, index=False)
