from __future__ import print_function
from model.melding import Melding, MeldingVerloop, MeldingVerloopRegel
from utils.utils import Utils
from utils.arcgis import ArcGis
import json

#import pprint
#pp = pprint.PrettyPrinter(indent=2)
#pp.pprint(logstati)

def lamda_handler(event, context):
  klakID = -1
  melding = None
  if event.has_key('queryParams'):
    queryParams = event['queryParams']
    if queryParams.has_key('klakID'):
      klakID = queryParams['klakID']
  elif event.has_key('pathParams'):
    pathParams = event['pathParams']
    if pathParams.has_key('klakID'):
      klakID = pathParams['klakID']
  print("klakID = " + str(klakID))
  melding = NetteMelding(klakID, arcGisURL).getMelding()
  print(melding)
  return melding.json()

class NetteMelding(object):

  def __init__(self, klakID, arcGisURL):
    self.klakID = klakID
    self.arcGis = ArcGis(arcGisURL)
    self.arcGis.setHistorieVanKlakID_URL(klakID)

  def collectHistorie(self):
    historie = {}
    for log in self.arcGis.getJSON():
      klakID = log['attributes']['KLAK_ID']
      logDatum = log['attributes']['LOG_DATUM']
      if not(historie.has_key(klakID)):
        historie[klakID] = {}
      if historie[klakID].has_key(logDatum):
        historie[klakID][logDatum] = Utils.mergeLogsAtSameDate(historie[klakID][logDatum], log['attributes'])
      else:
        historie[klakID][logDatum] = log['attributes']
    return historie
        
  def getMelding(self):
    historie = self.collectHistorie()
    melding = Melding(self.klakID)
    for klakID in historie.keys():
      if int(klakID) == int(self.klakID):
        verloop = MeldingVerloop()
        herstelDatum = -1
        prevHerstelDatum = -1
        ovpStatus = "In behandeling"
        for logDatum in sorted(historie[klakID]):
          log = historie[klakID][logDatum]
          if log['LOG_HERSTELDATUM'] != None:
            herstelDatum = log['LOG_HERSTELDATUM']
          svRegel = MeldingVerloopRegel(logDatum, herstelDatum)
          if log['LOG_STATUS'] == "Ter plaatse":
            ovpStatus = "In behandeling"
            svRegel.status = "In behandeling"
            svRegel.appendToelichting("Monteur ter plaatse")
            verloop.append(svRegel)
          elif log['LOG_STATUS'] == "Prov. hersteld":
            ovpStatus = "In behandeling"
            svRegel.status = "In behandeling"
            svRegel.appendToelichting("Provisorisch Hersteld ")
            svRegel.appendToelichting(log['LOG_PROV_RESULTAAT'])
            svRegel.appendToelichting(log['LOG_PROV_VERVOLG'])
            svRegel.appendToelichting(log['LOG_DEF_OORZAAK'])
            svRegel.appendToelichting(log['LOG_DEF_OPM'])
            verloop.append(svRegel)
          elif log['LOG_STATUS'] == "Doorgeven" and log['LOG_MEETD_REDEN_AFMELDING']:
            ovpStatus = "In behandeling"
            svRegel.status = "3. In behandeling"
            svRegel.appendToelichting(log['LOG_MEETD_REDEN_AFMELDING'])
            verloop.append(svRegel)
          elif log['LOG_STATUS'] == "Afgehandeld":
            ovpStatus = "Afgehandeld"
            svRegel.status = ovpStatus
            svRegel.appendToelichting(log['LOG_DEF_UITG_WERKZ'])
            svRegel.appendToelichting(log['LOG_DEF_OPM'])
            svRegel.appendToelichting(log['LOG_DEF_SOORT_NET'])
            svRegel.appendToelichting(log['LOG_DEF_HERKOMST'])
            svRegel.appendToelichting(log['LOG_DEF_LEIDINGNR'])
            verloop.append(svRegel)
          elif herstelDatum != prevHerstelDatum:
            if prevHerstelDatum != -1:
              svRegel.appendToelichting("Gewijzigde Hersteldatum")
              svRegel.status = ovpStatus
              verloop.append(svRegel)
            prevHerstelDatum = herstelDatum
        melding.append(verloop)
    return melding


if __name__ == "__main__":
    json = lamda_handler({'queryParams':{'klakID':'4134285'}}, None)
    #json = lamda_handler({"pathParams":{'klakID':'414285'}}, None)
    #json = lamda_handler({}, None)
    print(json)

  
  

  
  