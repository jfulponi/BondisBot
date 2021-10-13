import requests
# from requests.auth import HTTPBasicAuth
import tweepy
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point  # , Polygon

try:
    # Se pueden incluir keys + secrets en un archivo env.py
    from env import (
        consumer_key, consumer_secret, access_token, access_token_secret,
        client_GCBA, client_secret_GCBA
    )
except ImportError:
    consumer_key = "CONSUMER_TWITTER"
    consumer_secret = "CONSUMER_SECRET_TWITTER"
    access_token = "ACCESS_TWITTER"
    access_token_secret = "ACCESS_TOKEN_TWITTER"
    client_GCBA = "API_ID_GCBA"
    client_secret_GCBA = "API_SECRET_GCBA"


def hello_pubsub(_event, _context):
    # Twitter Developer Tokens
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    tweepy_api = tweepy.API(auth)

    bondis_url = f"https://apitransporte.buenosaires.gob.ar/colectivos/vehiclePositionsSimple?client_id={client_GCBA}&client_secret={client_secret_GCBA}"
    r = requests.get(bondis_url)
    df = pd.read_json(r.content)

    KM_PER_MILE = 1.6
    bondis_count = len(df)
    bondiest_line = df["route_short_name"].str.replace(r"\D", "").value_counts().index[0]
    bondis_speed = df[df["speed"] > 0]["speed"]
    vel_med_inst = KM_PER_MILE * bondis_speed.mean().round(2)
    vel_max =      KM_PER_MILE * max(bondis_speed)
    perc_85_vel =  KM_PER_MILE * np.percentile(bondis_speed, 85)

    tweet_text = (
        f'La cantidad de bondis circulando en la Región Metropolitana de Buenos Aires (RMBA) es de {bondis_count}, '
        f'siendo la línea con más bondis la {bondiest_line}. La velocidad media instantánea es de {vel_med_inst:.2f} km/h, '
        f'la máxima es de {vel_max:.2f} km/h y el percentil 85 de velocidad es de {perc_85_vel:.2f} km/h.'
    )

    geometry = [Point(xy)
                for xy in zip(-abs(df['longitude']), -abs(df['latitude']))]
    geo_df = gpd.GeoDataFrame(df, geometry=geometry)
    fig, ax = plt.subplots(figsize=(20, 20))
    geo_df.plot(column='speed', ax=ax, alpha=0.5, legend=False, markersize=10)
    # add title to graph
    plt.title('Bondis en el AMBA - en @BondisBot by @juanif__',
              fontsize=15, fontweight='bold')
    # set latitiude and longitude boundaries for map display
    plt.xlim(-58.75, -58.2)
    plt.ylim(-34.86, -34.4)
    fn = '/tmp/foo.png'
    plt.savefig(fn)

    res = tweepy_api.media_upload(fn)
    tweepy_api.update_status(status=tweet_text, media_ids=[str(res.media_id)])


if __name__ == "__main__":
    hello_pubsub(None, None)
