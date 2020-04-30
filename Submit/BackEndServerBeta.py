import Pyro4
import Pyro4.errors
import asyncio

UPDATE_ATTEMPTS = 3  # How many times to try and update another backend server before giving up


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


class User:
    def __init__(self, name):
        self.name = name
        self.orders = []
        self.address = None


class DataState:

    def __init__(self):
        self.users = {}
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
        menu = [MenuItem("Cursed Ambrosia", 1209, ["Gluten-Free", "Cursed"]),
                MenuItem("Shallot d'Morte", 3.99, ["Starter"]),
                MenuItem("The Essence of Eternity Itself", 7.99, []),
                MenuItem("Ham Sandwich", 19.99, []),
                MenuItem("Chaos Incarnate", 430.10, []),
                MenuItem("Giant's Toe Burrito", 4.50, ["Gluten-Free"]),
                MenuItem("Blood of the Forsaken", 19.20, ["Drink", "Cursed"]),
                MenuItem("Liquified Hellfire", 666, ["Drink"])]
        addr = "Keswick CA12 4TP"
        self.restruants["Cthulu's Hearth"] = Restruant("Cthulu's Hearth", menu, addr)

    def serialiseusers(self):
        userlist = []
        for user in self.users.values():
            userlist.append((user.name, user.orders, user.address))
        return userlist


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

    def makeorder(self, name, address, basket, total, time):
        try:
            if not name in currData.users:
                currData.users[name] = User(name)
            Pyro4.Future(tryupdate)("updateusers", currData.serialiseusers())
            currData.users[name].orders.append((name, address, basket, total, time))
            return True
        except:
            return False

    def ping(self):
        return True

    def getuserorders(self, name):
        if name not in currData.users:
            currData.users[name] = User(name)
            Pyro4.Future(tryupdate)("updateusers", currData.serialiseusers())
        return currData.users[name].orders

    @Pyro4.oneway
    def initialisebackupinterfaces(self):
        initbackups()


@Pyro4.expose
class UpdateInterface:

    def updateusers(self, newusers):
        print("Users being updated")
        currData.users = {}
        for user in newusers:
            currData.users[user[0]] = User(user[0])
            currData.users[user[0]].orders = user[1]
            currData.users[user[0]].address = user[2]


def initbackups():
    print("Initialising/Reinitialising backups")
    for backup in backupnames:
        try:
            interface = Pyro4.Proxy(backup)
            interface._pyroBind()
            workingbackups.append(interface)
        except Pyro4.errors.CommunicationError as err:
            print(f"Backup Interface: {backup} is not working, error: {err}")
        except Pyro4.errors.NamingError:
            print(f"Backup Interface: {backup} is not recognised by the nameserver, likely is not running")
    print(f"Backup initialisation complete, {len(workingbackups)} backups avaliable")


def tryupdate(methname, args):
    print("Updating backups...")
    global workingbackups
    updatebackups = False
    for backup in workingbackups:
        for i in range(UPDATE_ATTEMPTS):
            try:
                getattr(backup, methname)(*args)
                break
            except Pyro4.errors.CommunicationError as err:
                print("Error updating backup, attempting reconnect")
                try:
                    backup._pyroReconnect(2)
                except Pyro4.errors.PyroError:
                    print(f"Backup '{backup}' is not working, will reinitialise backups")
                    updatebackups = True
    if updatebackups:
        initbackups()

backupnames = ["PYRONAME:back.updateinterface.alpha", "PYRONAME:back.updateinterface.gamma"]
workingbackups = []

currData = DataState()

daemon = Pyro4.Daemon()  # make a Pyro daemon
ns = Pyro4.locateNS()  # find the name server
uri = daemon.register(Interface)  # register the greeting maker as a Pyro object
ns.register("back.interface.beta", uri)  # register the object with a name in the name server
uri = daemon.register(UpdateInterface)
ns.register("back.updateinterface.beta", uri)

print("Backend Beta Ready.")
daemon.requestLoop()  # start the event loop of the server to wait for calls
