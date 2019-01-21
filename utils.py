import requests
import string
# from lxml import html

def removeSpaceAndStrip(s):
	return s.replace("\t", "").replace("\n", "").strip()

def readFile(file):
	f = open(file, 'rb')
	data = f.read()
	return data.split('\r\n')

def notif(n):
	print("[ INFO] " + n)

def getCookiesInUS():
	payload = {"locationType": "LOCATION_INPUT", "zipCode": 10010, "storeContext": "generic", "deviceType":"web", "pageType":"Gateway", "actionSource":"glow"}
	headers = { "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", "accept": "text/html,*/*"}
	r = requests.post("https://www.amazon.com/gp/delivery/ajax/address-change.html", data=payload, headers=headers)

	return requests.utils.dict_from_cookiejar(r.cookies)
def isASCIIString(string):
	try:
		for char in string:
			char.decode("ascii")
	except Exception as e:
		return False
	return True

def printableString(s):
	return ''.join(filter(lambda x: x in string.printable, s))