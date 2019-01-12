
def removeSpaceAndStrip(s):
	return s.replace("\t", "").replace("\n", "").strip()

def readFile(file):
	f = open(file, 'r')
	data = f.read()
	return data.split('\n')

def notif():
	print(n)