
def removeSpaceAndStrip(s):
	return s.replace("\t", "").replace("\n", "").strip()

def readFile(file):
	f = open(file, 'r')
	data = f.read()
	return data.split('\n')

def notifError(n):
	print("----------------------------")
	print("\033[91m" + n + "\033[00m")
	print("----------------------------")
def notifSuccess(n):
	print("----------------------------")
	print("\033[92m" + n + "\033[00m")
	print("----------------------------")