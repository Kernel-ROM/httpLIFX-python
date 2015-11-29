import requests, sys, time, re

def changeBrightness(value):
	value = clamp(value, 1, 100)
	print "Changing brightness to: %s%%" % value
	value = value / float(100)
	data = {"brightness": value}
	makeRequest("lights/all/state", "PUT", data)
	return

def changeColour(colour, delay):
	print "Changing colour to: %s" % colour
	data = {
		'color': colour,
		"duration": delay
		}
	makeRequest("lights/all/state", "PUT", data)
	time.sleep(delay)
	return

def changeKelvin(value, delay):
	value = value[:-1]
	value = clamp(int(value), 2500, 9000)
	print "Changing kelvin to: %sk" % value
	data = {
		'color': "kelvin:"+str(value),
		"duration": delay
		}
	makeRequest("lights/all/state", "PUT", data)
	time.sleep(delay)
	return

def checkOnline():
	response = getStatus()
	if response.status_code != 200:
		print "Connection Error!"
		return False
	q = response.json()
	for i in q:
		if i['connected'] == True:
			return True
		else:
			print "Bulb offline, please turn on manually."
			return False

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def commands(Clist):
	Clist.remove(sys.argv[0])
	for i in range(len(Clist)):
		if Clist[i].isdigit():
			Clist[i] = int(Clist[i])
		else:
			Clist[i] = str(Clist[i])
		if type(Clist[i]) == str:
			Clist[i] = Clist[i].lower()

	for i in range(len(Clist)):
		if Clist[i] == "on":
			power(1)
		elif Clist[i] == "off":
			power(0)
		elif type(Clist[i]) == int:
			changeBrightness(Clist[i])
		elif type(Clist[i]) == str:
			pattern = re.compile("\d{1,5}k")
			if pattern.match(Clist[i]):
				changeKelvin(Clist[i], 1)
				break
			v = makeRequest("color?string="+Clist[i], "GET")
			if v.status_code == 200:
				changeColour(Clist[i], 2)
			elif v.status_code == 422:
				print "Unknown Colour!"
		else:
			print "Unknown command!"
	return


def getStatus():
	response = makeRequest('lights/all', "GET")
	return response

def makeRequest(url, Rtype, data=""):
	# Hide me!
	token = "YOUR_TOKEN_HERE"

	statusCodes = {	207:"Multi-Status - Inspect the response body.",
	400:"Bad Request - Request was invalid.",
	401:"Unautherised - Bad access token.",
	403:"Permission Denied - Bad OAuth Scope",
	404:"Not Found - Selector did not match any lights",
	422:"Unprocessable Entity - Missing or malformed parameters.",
	426:"Upgrade Required - Use HTTPS not HTTP",
	429:"Too many requests!",
	500:"Server Error!",
	502:"Server Error!",
	503:"Server Error!",
	523:"Server Error!" }
	headers = {
		"Authorization": "Bearer %s" % token
	}
	url = "https://api.lifx.com/v1/" + url
	if Rtype.upper() == "GET":
		try:
			response = requests.get(url, headers=headers)
		except:
			print "Connection failed."
	elif Rtype.upper() == "POST":
		try:
			response = requests.post(url, json=data, headers=headers)
		except:
			print "Connection failed."
	elif Rtype.upper() == "PUT":
		try:
			response = requests.put(url, json=data, headers=headers)
		except:
			print "Connection failed."
	pattern = re.compile("20\d")
	if not pattern.match(str(response.status_code)):
		print statusCodes[response.status_code]
		print response.json()
	return response

def power(option):
	status = getStatus()
	q = status.json()
	if option == 1:
		for i in q:
			if i['power'] == 'on':
				print "Bulb is already on!"
			else:
				print "Powering on..."
				makeRequest("lights/all/toggle", "POST")
	elif option == 0:
		for i in q:
			if i['power'] == 'off':
				print "Bulb is already off!"
			else:
				print "Powering off..."
				makeRequest("lights/all/toggle", "POST")
	return

# Initiates LIFX
def main():
	if checkOnline():
		commands(sys.argv)
	else:
		sys.exit(1)

if __name__ == "__main__":
    main()