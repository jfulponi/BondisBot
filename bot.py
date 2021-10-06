import requests
from requests.auth import HTTPBasicAuth 
import pandas as pd
import tweepy
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

def hello_pubsub(event, context):

  consumer_key = 'CONSUMER_TWITTER' 
  consumer_secret = 'CONSUMER_SECRET_TWITTER'
  access_token = "ACCESS_TWITTER"
  access_token_secret = ACCES_TOKEN_TWITTER"
  # Twitter Developer Tokens
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
  auth.set_access_token(access_token, access_token_secret)

  api = tweepy.API(auth)

  client_GCBA = "API_ID_GCBA"
  client_secret_GCBA = "API_SECRET_GCBA"
  url = "https://apitransporte.buenosaires.gob.ar/colectivos/vehiclePositionsSimple?client_id={}&client_secret={}".format(client_GCBA, client_secret_GCBA)
  r = requests.get(url)
  df = pd.read_json(r.content)

  
  final = 'La cantidad de bondis circulando en la Región Metropolitana de Buenos Aires (RMBA) es de {}, siendo la línea con más bondis la {}. La velocidad media instantánea es de {} km/h, la máxima es de {} km/h y el percentil 85 de velocidad es de {} km/h.'.format(len(df), df["route_short_name"].str.replace(r'\D', '').value_counts().index[0], "{:.2f}".format(df[df["speed"]>0]["speed"].mean().round(2)*1.6), "{:.2f}".format(max(df[df["speed"]>0]["speed"])*1.6), "{:.2f}".format(np.percentile(df[df["speed"]>0]["speed"], 85)*1.6))


  geometry = [Point(xy) for xy in zip(-abs(df['longitude']), -abs(df['latitude']))]
  geo_df = gpd.GeoDataFrame(df,
  geometry = geometry)
  fig, ax = plt.subplots(figsize=(20,20))
  geo_df.plot(column='speed',ax=ax,alpha=0.5, legend=False,markersize=10)
  # add title to graph
  plt.title('Bondis en el AMBA - en @BondisBot by @juanif__', fontsize=15,fontweight='bold')
  # set latitiude and longitude boundaries for map display
  plt.xlim(-58.75,-58.2)
  plt.ylim(-34.86,-34.4)
  # show map
  plt.savefig('/tmp/foo.png')
  res = api.media_upload('/tmp/foo.png')
  api.update_status(status = final, media_ids = [str(res.media_id)])
