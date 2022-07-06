from . import models

# Herramientas genericas
def getDateYYYYMM(date):
	if date:
		return date.strftime("%Y%m") or ''
	else:
		return ''


def getDateYYYYMMDD(date):
	if date:
		return date.strftime("%Y%m%d") or ''
	else:
		return ''