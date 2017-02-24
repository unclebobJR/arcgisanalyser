import requests
import json

class ArcGis(object):
  
  def __init__(self, arcGisURL):
    #self.arcGisURL = 'https://services1.arcgis.com/v6W5HAVrpgSg3vts/ArcGIS/rest/services/OvPortal_v2_Acc/FeatureServer'
    self.arcGisURL = arcGisURL
    self.endURL = '&outFields=*&f=json'
    self.requestURL = None
    
  def setHistorieVanKlakID_URL(self, klakID):
    self.requestURL = self.arcGisURL + '/1/query?where=KLAK_ID=' + str(klakID) + self.endURL
    
  def setMeldingSinds_URL(self, sinds):
    self.requestURL = self.arcGisURL + "/0/query?where= EditDate > '" + sinds + "'" + self.endURL
  
  def getJSON(self, localFile = ""):
    out = {}
    if self.requestURL == None:
      raise Exception("500 Internal Error: request URL is niet gezet")
    else:
      #out = requests.get('http://services1.arcgis.com/v6W5HAVrpgSg3vts/ArcGIS/rest/services/OvPortal_v3_Productie/FeatureServer/1/query?where=EditDate+%3E+%272016-10-15+00%3A32%3A00%27&outFields=*&f=json')
      if localFile != "":
        print (localFile)
        with open(localFile) as data_file:    
          out = json.load(data_file)
          if out.has_key('features'):
            out = out['features']
      else:
        print (self.requestURL)
        response = requests.get(self.requestURL)
        if response.status_code == 200:
          if response.json().has_key('features'):
            out = response.json()['features']
            if out == []:
              raise Exception("404 No element Found: " + str(self.requestURL))
          else:
            error = response.json()['error']
            raise Exception("500 ArcGis verbinding lukt niet, status: " + str(error['code']) + "\n"\
                          + str(error['message']) + "\n" + str(error['details']))
        else:
          raise Exception("500 ArcGis verbinding lukt niet, status: " + str(response.status_code) + "\n"\
                          + str(self.requestURL) + "\n" + str(response.text))
    print(out)
    return out