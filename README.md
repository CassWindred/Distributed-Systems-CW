# Distributed-Systems-CW
## Requirements:
The program was written using Python 3.8, and requires the Pyro4 python library.
## Running The Program
The program consists of 5 python scripts,
three of which are near-identical Back End
servers.

To begin with, the Pyro4 Nameserver must be
initiated using the command:  
`python -m Pyro4.naming`

Then, one or more Back End servers must be started up, these backup servers are as follows:  
`BackEndServerAlpha.py`, `BackEndServerBeta.py`, `BackEndServerGamma.py`

Once all of the servers are ready (they will print a ready message to the console when done setting up)
you may start up `FrontEndServer.py`, this will connect to all running Back-End servers, designate one as the
primary, and then wait for connections from a client. It also manages requests to other components, described
later. 

Once the Front End server prints its ready message, you may start up  `Client.py`, it will request
input from the user and then establish a connection with the Front End server. From there, follow the
prompts provided by the Client in order to view restruants, make orders and so on.

From here on, each time an order is made, or a user "logs in", the primary Back End server will propogate
all changes to the other running back-end servers, and if one of the Back End servers stops running, another
Back End server will automatically be redesignated as the primary. The process of identifying down servers
and redesignating the primary can take some time on Windows systems, but it much faster on Linux. 

## External Services
Two external services are used by the program. Firstly, the Postcodes.io service is used to validate the
postcode entered by the user, if the service fails the program is able to recover, and if the postcode
is invalid, the user is required to enter a valid postcode. Secondly, the Bing Maps API is used to find the
distance, both in terms of driving miles, and driving hours, between the user location and a given restruant
location, thus giving an estimate of when food may arrive when ordered. Again, the program is able to recover
should the service fail or be inaccessible, or if the entered address is invalid. 