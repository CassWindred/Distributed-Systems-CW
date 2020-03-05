import Pyro4
import asyncio



# To Start NameServer: python -m Pyro4.naming

class MenuItem:
    def __init__(self, name, price, tags):
        self.name = name
        self.price = price
        self.tags = tags


class Restruant:
    def __init__(self, name, menuitems, address):
        self.name = name
        self.address = address
        self.menuitems = self.initmenuitems(menuitems)

    def initmenuitems(self, menuitems):
        menudict = {}
        for menuitem in menuitems:
            menudict[menuitem.name] = menuitem
        return menudict


class Order:
    def __init__(self, name, address, restruant):
        self.name = name
        self.address = address
        self.restruant = restruant


class DataState:

    def __init__(self):
        self.restruants = {}

        menu = [MenuItem("Cod Fillet", 9.99, ["Gluten-Free", "Pescatarian"]),
                MenuItem("Fish Burger and Chips", 12.99, ["Burger"]),
                MenuItem("Salmon", 6.50, ["Gluten-Free"]),
                MenuItem("Breaded Trout", 8.40, []),
                MenuItem("Coke", 1.50, ["Drink"])]
        addr = "Durham University, Lower Mountjoy, Stockton Rd, Durham DH1 3LE"
        self.restruants["Fil'o'Fish"] = Restruant("Fil'O'Fish", menu, addr)
        menu = [MenuItem("Beef Burger", 12.99, ["Burger"]),
                MenuItem("Fish Burger", 10.99, ["Burger"]),
                MenuItem("Side of Chips", 4.50, ["Gluten-Free"]),
                MenuItem("Sprite", 1.40, ["Drink"]),
                MenuItem("Beer", 3.50, ["Drink"])]
        addr = "21A Elvet Bridge, Durham DH1 3AA"
        self.restruants["BurgerTopia"] = Restruant("BurgerTopia", menu, addr)


currData = DataState()








@Pyro4.expose
class Interface:
    def getrestruants(self, address, postcode):
            return currData.restruants.keys()

    def getmenuitems(self, restruant: str):
        if restruant in currData.restruants:
            menu = currData.restruants[restruant].menuitems.values()
            return ((item.name, item.price, item.tags) for item in menu)
        else:
            print(f"getmenuitems() was called for nonexistent restruant {restruant}")
            return False

    def getaddress(self, restruant):
        return currData.restruants[restruant].address


daemon = Pyro4.Daemon()  # make a Pyro daemon
ns = Pyro4.locateNS()  # find the name server
uri = daemon.register(Interface)  # register the greeting maker as a Pyro object
ns.register("back.interface", uri)  # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()  # start the event loop of the server to wait for calls
