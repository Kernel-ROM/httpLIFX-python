"""Connect to the LIFX HTTP API & control your bulb over the internet."""
import requests
import sys
import time
import re
import argparse


def changeBrightness(value):
    """Change brightness as a percentage."""
    value = clamp(value, 1, 100)
    print "Changing brightness to: %s%%" % value
    value = value / float(100)
    data = {"brightness": value}
    makeRequest("lights/all/state", "PUT", data)
    return


def changeColour(colour, delay):
    """Validate colour using LIFX API then change it."""
    print "Changing colour to: %s" % colour
    data = {
        "color": colour,
        "duration": delay
    }
    makeRequest("lights/all/state", "PUT", data)
    time.sleep(delay)
    return


def changeKelvin(value, delay):
    """Change warmth of bulb in degrees kelvin."""
    value = value[:-1]
    value = clamp(int(value), 2500, 9000)
    print "Changing kelvin to: %sk" % value
    data = {
        'color': "kelvin:" + str(value),
        "duration": delay
    }
    makeRequest("lights/all/state", "PUT", data)
    time.sleep(delay)
    return


def checkOnline():
    """Check if the bulb is online."""
    response = getStatus()
    if response.status_code != 200:
        print "Connection Error!"
        return False
    q = response.json()
    for i in q:
        if i['connected']:
            return True
        else:
            print "Bulb offline, please turn on manually."
            return False


def clamp(n, minn, maxn):
    """Clamp input between floor and ceiling values."""
    return max(min(maxn, n), minn)


def commands():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Process input commands.')
    parser.add_argument('--power', '-p', help='ON/OFF')
    parser.add_argument('--colour', '-c', help='Change colour of bulb.')
    parser.add_argument('--toggle', '-t', help='Toggle power state.', action='store_true')
    parser.add_argument('--brightness', '-b', help='Value as a percentage.', type=int)
    parser.add_argument('--kelvin', '-k', help='Between 2500 & 9000.', type=int)

    args = parser.parse_args()

    if args.power:
        if args.power.upper() == "ON":
            power(1)
        elif args.power.upper() == "OFF":
            power(0)
        elif args.power.upper() == "TOGGLE":
            powerToggle()
        else:
            print "Unknown command!"

    if args.toggle:
        powerToggle()

    if args.colour:
        v = makeRequest("color?string=" + args.colour, "GET")
        if v.status_code == 200:
            changeColour(args.colour, 2)
        elif v.status_code == 422:
            print "Unknown Colour!"

    if args.brightness:
        changeBrightness(args.brightness)

    if args.kelvin:
        changeKelvin(args.kelvin, 1)
    return


def getStatus():
    """Return the status of the bulb."""
    response = makeRequest('lights/all', "GET")
    return response


def makeRequest(url, Rtype, data=""):
    """Key function used to connect to the LIFX API."""
    # Hide me!
    token = "YOUR_TOKEN_HERE"

    statusCodes = {
        207: "Multi-Status - Inspect the response body.",
        400: "Bad Request - Request was invalid.",
        401: "Unautherised - Bad access token.",
        403: "Permission Denied - Bad OAuth Scope",
        404: "Not Found - Selector did not match any lights",
        422: "Unprocessable Entity - Missing or malformed parameters.",
        426: "Upgrade Required - Use HTTPS not HTTP",
        429: "Too many requests!",
        500: "Server Error!",
        502: "Server Error!",
        503: "Server Error!",
        523: "Server Error!"
    }
    headers = {
        "Authorization": "Bearer %s" % token,
    }
    requrl = "https://api.lifx.com/v1/" + url

    if Rtype.upper() == "GET":
        try:
            response = requests.get(requrl, headers=headers)
        except:
            print "GET connection failed."
            sys.exit(1)

    elif Rtype.upper() == "POST":
        try:
            response = requests.post(requrl, json=data, headers=headers)
        except:
            print "POST connection failed."
            sys.exit(1)

    elif Rtype.upper() == "PUT":
        try:
            response = requests.put(requrl, json=data, headers=headers)
        except:
            print "PUT connection failed."
            sys.exit(1)

    pattern = re.compile("20\d")
    if not pattern.match(str(response.status_code)):
        print statusCodes[response.status_code]
        print response.json()
    return response


def power(option):
    """Change bulb power state with validation."""
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


def powerToggle():
    """Toggle bulb power state."""
    print "Toggling power..."
    makeRequest("lights/all/toggle", "POST")
    return


# Initiates LIFX
def main():
    if checkOnline():
        commands()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
