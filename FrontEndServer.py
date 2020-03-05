import Pyro4
import asyncio
import requests
import json

Interface = Pyro4.Proxy("PYRONAME:back.interface")  # use name server object lookup uri shortcut


def distanceAPIcall(address1, address2):
    print(f"Getting Distance between \"{address1}\" and \"{address2}\"")
    url = f"http://dev.virtualearth.net/REST/V1/Routes/Driving?wp.0={address1}%2Cwa&wp.1={address2}%2Cwa&avoid=minimizeTolls&distanceUnit=mi&key=L7CjHmVZPbKmelVWL8pu~DWGkwVtxhcPqfBd6Evk7Aw~AqQlqFTm-6iQm6KwJs4dpqW5LJWCO-I8Vn2rk0lFv9FNJ5D21MYDgXeRr82fxVw4"

    response = json.loads(requests.request("GET", url).text)
    if "errorDetails" in response:
        if response["errorDetails"][0] == 'The internal route service returned a timeout error code in the response':
            raise Exception("Distance API Timed Out")
        if response["errorDetails"][0] == "No route was found for the waypoints provided.":
            raise Exception("Failed to find route")
        raise Exception(f"Distance API Exception: {response['errorDetails'][0]}")
    else:
        resource = response["resourceSets"][0]["resources"][0]
        return resource['travelDistance'], resource['travelDurationTraffic']


#print(getdistance("12 Percy Square, Durham, DH1 3PZ", "86 Fuckyou Fuckenu, Fuckslyvania, Fuck, 123 123"))


@Pyro4.expose
class ClientInterface:
    def getrestruants(self, address, postcode):
        return Interface.getrestruants(address, postcode)

    def getmenuitems(self, restruant):
        return Interface.getmenuitems(restruant)

    def getdistance(self, address, postcode, restruant):
        try:
            restruantaddr = Interface.getaddress(restruant)
            return distanceAPIcall(f"{address}, {postcode}", restruantaddr)
        except Exception as err:
            if err == "Distance API Timed Out" or err == "Failed to find route":
                return False, err
            else:
                print(err)
                return False, "Unknown Error"

    def makeorder(self, fulladdress, basket):
        try:
            return True
        except:
            return False

daemon = Pyro4.Daemon()  # make a Pyro daemon
ns = Pyro4.locateNS()  # find the name server
uri = daemon.register(ClientInterface)  # register the greeting maker as a Pyro object
ns.register("front.interface", uri)  # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()  # start the event loop of the server to wait for calls
