from utils.utils import Utils

class Melding(object):
  def __init__(self, klakID):
    self.ID = klakID
    self.meldingVerloop = None

  def append(self, verloop):
    self.meldingVerloop = verloop
  
  def __str__(self):
    out = "======== melding: " + str(self.ID) + " ========="
    out = out + str(self.meldingVerloop)
    return out

class MeldingVerloopRegel(object):
  def __init__(self, logDatum, herstelDatum):
    self.logDatum = logDatum
    self.herstelDatum = herstelDatum
    self.status = ""
    self.toelichting = ""
    
  def appendToelichting(self, toelichting):
    if toelichting != None:
      if self.toelichting == "":
        self.toelichting = toelichting.encode('utf-8')
      else:
        self.toelichting = self.toelichting + " " + toelichting.encode('utf-8')
    
  def __str__(self):
    out = "\n"
    out = out + self.status + ' - ' + Utils.microTimestamp2HumanReadable(self.logDatum) + "\n"
    out = out + self.toelichting + "\n"
    out = out + "verwachte hersteldatum: " + Utils.microTimestamp2HumanReadable(self.herstelDatum)
    return out
  
  def __eq__(self, other):
    return ((self.herstelDatum, self.status, self.toelichting) == (other.herstelDatum, other.status, other.toelichting))
  
class MeldingVerloop(object):
  def __init__(self):
    self.regels = []
    
  def append(self, regel):
    if len(self.regels) == 0:
      self.regels.append(regel)
    elif not self.regels[-1] == regel:
      self.regels.append(regel)
  
  def __str__(self):
    out = ""
    for regel in self.regels:
      out = out + "\n" + str(regel)
    return out
