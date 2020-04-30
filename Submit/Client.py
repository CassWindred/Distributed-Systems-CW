import Pyro4
import Pyro4.errors
import sys
import math
import time

Pyro4.config.COMMTIMEOUT = 60 #Setting Timeout to 60 Seconds


def round_sig(x, sig=2):
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)


def rep_time(secs):
    mins = int(math.ceil(secs / 60) / 10) * 10
    hours = int(mins / 60)
    if hours >= 1:
        mins = mins % 60
        return f"{hours} hour{'s' if hours >= 2 else ''}{f' and {mins} minutes' if mins > 0 else ''}"
    else:
        return f'{mins} minutes'


def rep_money(amount):
    return format(float(amount), '0.2f')


def getRestruants():
    print("Please wait for a moment while we contact the server for you...")
    global restruants
    restruants = Interface.getrestruants(address, postcode)
    if not restruants:
        print("Error ")
    print("Thanks for waiting, avaliable restruants are listed below: ")
    for i in range(len(restruants)):
        print(f"{i + 1}: \'{restruants[i]}\'")
    print()


def displayRestruant(restruant):
    print(f"You have selected {restruant}!")
    print("Please wait a moment while we contact the server and find out more about your choice!")

    # Run the two functions concurrently to minimise the time it takes
    dist = Pyro4.Future(Interface.getdistance)(address, postcode, restruant)
    menu = Pyro4.Future(Interface.getmenuitems)(restruant)
    dist.wait()
    menu.wait()
    dist = dist.value
    menu = list(menu.value)
    if not menu:
        print(f"There was a server error while looking for the menu for {restruant}, please try again")
        return False
    else:
        print(f"Welcome to {restruant}!")
        if not dist[0]:
            print(
                f"There was an error finding how far away you are from {restruant}, make sure you are using a valid address.")
        else:
            print(
                f"{restruant} is located only {round_sig(int(dist[0]))} miles away by car, which should take our drivers about {rep_time(dist[1])} to traverse!")
        while True:
            print("This restruant has the following menu items avaliable: ")
            for i in range(len(menu)):
                item = menu[i]
                print(f"{i + 1}: {item[0]}, £{rep_money(item[1])} ({', '.join(item[2])})")
            print(
                "Please enter the number of an item you would like to add to your basket or \"BACK\" to return to main menu")
            inp = input("Input: ")
            if inp == "BACK":
                return False
            try:
                inp = int(inp)
                if inp > len(menu) or inp < 1:
                    print(f"{inp} is not a valid menu item, please enter a number between 1 and {len(restruants)}")
                else:
                    print(f"Adding {menu[inp - 1][0]} to your basket!")
                    global basket
                    basket.append(list(menu[inp - 1]) + [restruant])
                    print("Now returning to menu...")
                    print("         ---")
            except ValueError:
                print(f"{inp} is not a valid input, please try again...")


def displayCheckout(total):
    global basket
    while True:
        restruants = set(item[3] for item in basket)
        print(f"You are about to make an order to the following restruants: {', '.join(restruants)}.")
        print(f"Total Cost: £{rep_money(total)}")
        print(f"Delivery Address: {address}, {postcode}")
        print("Type \"CONFIRM\" to confirm your purchase or \"BACK\" To return to main menu")
        inp = input("Input: ")
        if inp == "CONFIRM":
            print("Great! Making order now...")
            timestr = time.asctime()
            if Interface.makeorder(name, f"{address}, {postcode}", basket, total, timestr):
                input("Order successfully made! Press enter to return to main menu.")
                orders.append((name, f"{address}, {postcode}", basket, total, timestr))
                return True
            else:
                print("Oh dear, the order failed! I swear this hasn't happened before! Uh, just, um, can we try again?")
        elif inp == "BACK":
            return False


def displayBasket():
    global basket
    if not basket:
        print("Your basket is empty! Come back when you have added some tasty food!")
        return False
    while True:
        print("Your basket contains the following items!")
        total = 0.0
        for i in range(len(basket)):
            print(f"{i + 1} - {basket[i][0]}, £{rep_money(basket[i][1])} (From {basket[i][3]})")
            total += basket[i][1]
        print(f"This comes to a total of £{rep_money(total)}")
        print()
        print(
            "Please enter a number to remove an item from your basket, type \"BACK\" to return to main menu, or type \"CHECKOUT\" to go to checkout with your current basket")
        inp = input("Input: ")
        try:
            inp = int(inp)
            if inp > len(restruants) or inp < 1:
                print(f"{inp} is not a valid item, please enter a number between 1 and {len(basket)}")
                break
            else:
                del basket[inp - 1]
        except ValueError:
            if inp == "BACK":
                return False
            elif inp == "CHECKOUT":
                displayCheckout(total)
                return False
            else:
                print(f"{inp} is not a valid input, please try again. This time, maybe do it right?")


def displayOrders():
    if not orders:
        print("You haven't made any orders yet :'( ")
        print("Come back once you have ordered some delicious food!")
        print()
    else:
        print(f"Here are your orders under the name \"{name}\": ")
        print("------------------------------------------------")
        for order in orders:
            print(f"---Order made on date: {order[4]}---")
            print(f"Sent to address: {order[1]}")
            print("Contained the following items:")
            for item in order[2]:
                print(f"-{item[0]}, £{rep_money(item[1])} (From {item[3]})")
            print(f"Totalling £{rep_money(order[3])}")
        print("------------------------------------------------")

    input("There are no further orders, please press enter to continue.")



Interface = Pyro4.Proxy("PYRONAME:front.interface")  # use name server object lookup uri shortcut

print("                                   Welcome to Just Hungry!")
print("-The premiere food delivery service for command line entheusiasts who love installing python modules!-")
print()
name = "Cass" #input("To start with, please input your name: ")
address = "35 The Moor Melbourn"  # input("Now please input your address, not including postcode: ")
postcode = "SG86ED"  # input("Now input your postcode: ")
print("Checking postcode...")
try:
    while not Interface.checkpostcode(postcode):
        postcode = input("Postcode invalid, please input a valid postcode: ")
except ConnectionError as err:
    if err == "Postcode Validation Failed":
        print("Postcode Validation Failed, proceeding without validation...")
except Pyro4.errors.CommunicationError as err:
    print("Error communicating with server, proceeding without validation...")
    print(err)
print("Postcode Accepted")

restruants = []
basket = []
orders = Interface.getuserorders(name)
try:
    getRestruants()
except Pyro4.errors.CommunicationError as err:
    if err is Pyro4.errors.TimeoutError:
        print("Connection with the server timed out, please ensure it is running...")
    else:
        print("Error communicating with server...")
    sys.exit()

while True:
    try:
        print("-- MAIN MENU --")
        print("The following options are now avaliable: ")
        print(
            f"Input a number between 1 and {len(restruants)} in order to select the restruant listed above and add items to your basket")
        print("Input \"RELIST\" to get the list of restruants from the server again")
        print("Input \"REENTER\" to re-enter your address information")
        print("INPUT \"BASKET\" to view your current basket or make an order")
        print("Input \"ORDERS\" to view existing orders")
        print("Input \"QUIT\" to quit Just Hungry")
        inp = input("Type Input Here: ")

        try:
            inp = int(inp)
            if inp > len(restruants) or inp < 1:
                print(f"{inp} is not a valid restruant, please enter a number between 1 and {len(restruants)}")
                break
            else:
                displayRestruant(restruants[inp - 1])
        except ValueError:
            if inp == "RELIST":
                getRestruants()
            elif inp == "REENTER":
                address = input("Please enter address, not including postcode: ")
                postcode = input("Please enter postcode: ")
                print("Great! Returning to main menu...")
                print()
            elif inp == "BASKET":
                displayBasket()
            elif inp == "ORDERS":
                displayOrders()
            elif inp == "QUIT":
                print("We hope you had a good time using Just Hungry, and we look forward to seeing you again!")
                print("Now exiting program...")
                sys.exit()
            else:
                print(
                    f"Uh oh! \"{inp}\" is not a valid option, returning you to main menu, next time, make better choices!")
    except Pyro4.errors.TimeoutError:
        print("Connection to server Timed Out, returning to main menu")
    except Pyro4.errors.ConnectionClosedError:
        print("The connection to the server unexpectedly closed, attempting to reconnect...")
        try:
            Interface._pyroReconnect(50)
            print("Reconnect Successful, returning you to main menu")
        except Pyro4.errors.PyroError:
            print("Reconnect Failed, this error is not recoverable, ending program...")
            sys.exit()