from __future__ import print_function
from model.melding import Melding, MeldingVerloop, MeldingVerloopRegel
from utils.utils import Utils
from utils.arcgis import ArcGis
import os
import json

#import pprint
#pp = pprint.PrettyPrinter(indent=2)
#pp.pprint(logstati)

def lamda_handler(event, context):
  klakID = -1
  melding = None
  localFile = ""
  if event.has_key('queryParams'):
    queryParams = event['queryParams']
    if queryParams.has_key('klakID'):
      klakID = queryParams['klakID']
  elif event.has_key('pathParams'):
    pathParams = event['pathParams']
    if pathParams.has_key('klakID'):
      klakID = pathParams['klakID']
  if event.has_key('localfile'):
    localFile = event['localfile']
  print("klakID = " + str(klakID))
  arcGisURL = os.environ['arcgisurl']
  melding = NetteMelding(klakID, arcGisURL, localFile).getMelding()
  print(melding)
  return melding.json()

class NetteMelding(object):

  IN_BEHANDELING = "In behandeling"
  TER_PLAATSE = "Ter plaatse"
  PROVISORISCH_HERSTELD = "Prov. hersteld"
  DOORGEVEN = "Doorgeven"
  VERTRAAGD = "Vertraagd"
  AFGEHANDELD = "Afgehandeld"
  
  def __init__(self, klakID, arcGisURL, localFile = ""):
    self.klakID = klakID
    self.arcGis = ArcGis(arcGisURL)
    self.arcGis.setHistorieVanKlakID_URL(klakID)
    self.localFile = localFile

  def collectHistorie(self):
    historie = {}
    for log in self.arcGis.getJSON(self.localFile):
      klakID = log['attributes']['KLAK_ID']
      logDatum = log['attributes']['LOG_DATUM']/10
      if not(historie.has_key(klakID)):
        historie[klakID] = {}
      if historie[klakID].has_key(logDatum):
        historie[klakID][logDatum] = Utils.mergeLogsAtSameDate(historie[klakID][logDatum], log['attributes'])
      else:
        historie[klakID][logDatum] = log['attributes']
    return historie
        
  def bepaalVerloop(self, log, svRegel, ovpStatus):
    if log['LOG_STATUS'] == self.TER_PLAATSE:
      svRegel.status = self.IN_BEHANDELING
      svRegel.appendToelichting("Monteur ter plaatse")
    elif log['LOG_STATUS'] == self.PROVISORISCH_HERSTELD:
      svRegel.status = self.IN_BEHANDELING
      svRegel.appendToelichting("Provisorisch Hersteld ")
      svRegel.appendToelichting(log['LOG_PROV_RESULTAAT'])
      svRegel.appendToelichting(log['LOG_PROV_VERVOLG'])
      svRegel.appendToelichting(log['LOG_DEF_OORZAAK'])
      svRegel.appendToelichting(log['LOG_DEF_OPM'])
    elif log['LOG_STATUS'] == self.DOORGEVEN:
      if log['LOG_MEETD_REDEN_AFMELDING']:
        svRegel.status = self.IN_BEHANDELING
        svRegel.appendToelichting(log['LOG_MEETD_REDEN_AFMELDING'])
    elif ovpStatus == self.IN_BEHANDELING and log['LOG_STATUS'] in ['Verzonden', 'Doorgeven'] and log['LOG_VERTR_OORZ'] != None and log['LOG_VERTR_OORZ'] != "":
        svRegel.status = self.VERTRAAGD
        svRegel.appendToelichting(log['LOG_VERTR_OORZ'])
        svRegel.appendToelichting(log['LOG_VERTR_TOEL'])
    elif log['LOG_STATUS'] == self.AFGEHANDELD:
      svRegel.status = self.AFGEHANDELD
      svRegel.appendToelichting(log['LOG_DEF_UITG_WERKZ'])
      svRegel.appendToelichting(log['LOG_DEF_OPM'])
      svRegel.appendToelichting(log['LOG_DEF_SOORT_NET'])
      svRegel.appendToelichting(log['LOG_DEF_HERKOMST'])
      svRegel.appendToelichting(log['LOG_DEF_LEIDINGNR'])
    return svRegel
  
  def getMelding(self):
    historie = self.collectHistorie()
    melding = Melding(self.klakID)
    for klakID in historie.keys():
      if int(klakID) == int(self.klakID):
        verloop = MeldingVerloop()
        ovpStatus = self.IN_BEHANDELING
        vorigeHerstelDatum = -1
        for logDatum in sorted(historie[klakID]):
          log = historie[klakID][logDatum]
          print (log['LOG_STATUS'])
          if log['LOG_HERSTELDATUM'] != None:
            svRegel = MeldingVerloopRegel(log['LOG_DATUM'], log['LOG_HERSTELDATUM'])
          else:
            svRegel = MeldingVerloopRegel(log['LOG_DATUM'], vorigeHerstelDatum)
          svRegel = self.bepaalVerloop(log, svRegel, ovpStatus)
          if svRegel.herstelDatum != vorigeHerstelDatum and svRegel.toelichting == '':
              svRegel.appendToelichting("Gewijzigde Hersteldatum")
          vorigeHerstelDatum = svRegel.herstelDatum
          
          if svRegel.status != "":
            verloop.append(svRegel)
            ovpStatus = svRegel.status
          
        melding.append(verloop)
    return melding


if __name__ == "__main__":
    #json = lamda_handler({'queryParams':{'klakID':'4435242'}, 'localfile':'C:\Users\uab910\Downloads\OvPortal_v2_Acc_FeatureServer_1_KLAK_ID=4435242.json'}, None)
    json = lamda_handler({'queryParams':{'klakID':'4445384'}}, None)
    #json = lamda_handler({"pathParams":{'klakID':'414285'}}, None)
    #json = lamda_handler({}, None)
    print(json)

  
  

  
  