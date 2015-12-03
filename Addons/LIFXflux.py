import sys, requests, re, os, time
sys.path.append("..")
import httpLIFX as pyFX
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

def cityToLL(string):
	# Hide me!
	key = "YOUR_KEY_HERE"
	url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (string, key)
	response = makeRequest(url)
	latlng = [0, 0]
	response = response.json()
	response = response["results"]
	for i in response:
		c = i["geometry"]
		latlng[0] = c["bounds"]["northeast"]["lat"]
		latlng[1] = c["bounds"]["southwest"]["lng"]
	return latlng

def configConstructor(path):
	config = ConfigParser()
	config.add_section("Settings")
	config.set("Settings", "Address", "")
	config.set("Settings", "Latitude", "")
	config.set("Settings", "Longitude", "")
	config.set("Settings", "Sunset", "")
	config.set("Settings", "Timeout", "")
	config.set("Settings", "LastUpdate", "")
	config.set("Settings", "DayKelvin", "")
	config.set("Settings", "NightKelvin", "")
 
	with open(path, "w") as config_file:
		config.write(config_file)
	return

def getIniValues(iniName, settings):
	config = ConfigParser()
	config.read(iniName)
	value = []
	for i in range(len(settings)):
		value.append(config.get("Settings", settings[i]))
	return value

def kelvinKiller(iniName):
	settings = ["Timeout", "Sunset", "LastUpdate", "DayKelvin", "NightKelvin"]
	values = getIniValues(iniName, settings)
	
	if values[2] != time.strftime("%d/%m/%Y"):
		updateSundown(iniName)
	for i in range(int(values[0])):
		pyFX.changeKelvin(value, 2)
	

	return

def makeRequest(url, data=""):
	try:
		response = requests.get(url+data)
	except:
		print "Connection failed."
	pattern = re.compile("200")
	if not pattern.match(str(response.status_code)):
		print "ERROR: " + response.status_code
		print response.json()
	return response

def setIniVals(iniName, settings, values):
	if len(settings) != len(values):
		print "Argument Error!"
		return
	config = ConfigParser()
	config.read(iniName)
	for i in range(len(settings)):
		config.set("Settings", settings[i], values[i])

	with open(iniName, "w") as config_file:
		config.write(config_file)
	return

def setup(iniName):
	try:
		print "Please enter your nearest town or city:"
		values = []
		response = raw_input("> ")
		latlng = cityToLL(response)
		if latlng[0] == 0 or latlng[1] == 0:
			print "Google API error!"
			return
		values.append(response)
		values.append(latlng[0])
		values.append(latlng[1])
		sd = sundown(latlng[0],latlng[1])
		values.append(sd)
		print "Please enter how long the light fade should be in mins [0-60]"
		response2 = raw_input("> ")
		response2 = pyFX.clamp(int(response2), 0, 60)
		values.append(response2)
		values.append(time.strftime("%d/%m/%Y"))
		print "Please enter daytime temperature, default is 5000 [2500-9000]"
		response3 = raw_input("> ")
		response3 = pyFX.clamp(int(response3), 2500, 9000)
		values.append(response3)
		print "Please enter nighttime temperature, default is 3400 [2500-9000]"
		response4 = raw_input("> ")
		response4 = pyFX.clamp(int(response4), 2500, 9000)
		values.append(response4)
		settings = ["Address", "Latitude", "Longitude", "Sunset", "Timeout", "LastUpdate", "DayKelvin", "NightKelvin"]
		setIniVals(iniName, settings, values)
		print settings, values
	except:
		print "Error!"
		return
	return

def sundown(lat, lng):
	sd = makeRequest("http://api.sunrise-sunset.org/json?", "lat=%f&lng=%f" % (lat, lng))
	sd = sd.json()
	sd = sd["results"]
	return str(sd["sunset"])

def updateSundown(iniName):
	settings = ["Address"]
	values = []
	response = getIniValues(iniName, settings)
	latlng = cityToLL(response[0])
	sd = sundown(latlng[0],latlng[1])
	values.append(sd)
	values.append(time.strftime("%d/%m/%Y"))
	settings.append("LastUpdate")
	setIniVals(iniName, settings, values)
	return

def main():
	iniName = "flux.ini"
	if os.path.isfile(iniName):
		kelvinKiller(iniName)
		return
	else:
		configConstructor(iniName)
		setup(iniName)

if __name__ == "__main__":
    main()