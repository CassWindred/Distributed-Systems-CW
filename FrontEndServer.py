import Pyro4
import asyncio

Interface = Pyro4.Proxy("PYRONAME:main.interface")  # use name server object lookup uri shortcut
print(Interface.getrestruants())
