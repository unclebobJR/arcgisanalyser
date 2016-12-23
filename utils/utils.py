from datetime import datetime, timedelta
import calendar

class Utils():
  @staticmethod
  def microTimestamp2HumanReadable(microTimestamp):
    timestamp = microTimestamp / 1000
    ms = str(timestamp)
    utc_dt = datetime.utcfromtimestamp(timestamp)
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    localdt = local_dt.replace(microsecond=utc_dt.microsecond)
    return str(localdt) + "." + ms[-3:]
  
  @staticmethod
  def mergeLogsAtSameDate(currentLog, newLog):
    for key in newLog.keys():
      if newLog[key] != None:
        if Utils.keyHasValueInDict(currentLog, key):
          if key in ["LOG_STATUS", "LOG_HERSTELDATUM", "LOG_DATUM"]:
            currentLog[key] = newLog[key]
          else:
            if currentLog[key] != currentLog[key]:
              currentLog[key] = currentLog[key] + newLog[key]
        else:
          currentLog[key] = newLog[key]  
    return currentLog

  @staticmethod
  def keyHasValueInDict(currentLog, key):
    if currentLog.has_key(key):
      if currentLog[key] == None:
        return False
      else:
        return True
    else:
      return False
