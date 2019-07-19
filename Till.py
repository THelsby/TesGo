import datetime

from bson import Decimal128
from pymongo import MongoClient
from pymongo import ReturnDocument


class Till:
    running = True

    def __init__(self, _id, userId, userPassword):
        self.id = _id
        self.userId = userId
        self.userPassword = userPassword
        self.functionality = {
            "lookUpAllItems": self.readAllItems,
            "lookUpByName": self.readItemByName,
            "addItem": self.addItem,
            "modifyStock": self.updateStock,
            "addSale": self.updateSale,
            "removeItem": self.removeItemByName,
            "addStaff": self.addStaffMember,
            "removeStaff": self.deleteStaffMember,
            "updateStaff": self.updateStaffMember,
            "lookUpAllStaff": self.readAllStaff,
            "shutDown": self.shutDown
        }

    def startup(self):
        print("---------Available operations---------")
        for function in self.functionality:
            print(function)
        while self.running:
            startInput = input("Enter function you would like to use\n")
            try:
                self.functionality[startInput]()
            except KeyError:
                print("Did not recognise command")

    @staticmethod
    def connectToDatabase():
        HOST = "localhost"
        PORT = 27017
        client = MongoClient(host=HOST, port=PORT)
        myDb = client.tesGodb
        client.close()
        return myDb

    def getStockCollection(self):
        myDb = self.connectToDatabase()
        return myDb.stock

    def getCounterId(self):
        myDb = self.connectToDatabase()
        counter_collection = myDb.counters
        counter = counter_collection.find_one_and_update({'_id': 'productid'}, {'$inc': {'sequence_value': 1}},
                                                         return_document=ReturnDocument.BEFORE)
        return counter["sequence_value"]

    def readAllItems(self):
        stockData = self.getStockCollection().find()
        for stock in stockData:
            print("ID - {} | {} - Price {}".format(stock["_id"], stock["itemName"], stock["price"]))
        self.logAction("lookupAll", {})

    def readItemByName(self):
        item = input("Enter item you want to search for\n").lower()
        readItemQuery = {"itemName": item}
        itemData = self.getStockCollection().find_one(readItemQuery)
        if not itemData:
            print("Cannot find item requested\n")
        else:
            print(
                "ID - {} | Item Name - {} | Price - {} | Stock Amount - {}".format(itemData["_id"],
                                                                                   itemData["itemName"],
                                                                                   itemData["price"],
                                                                                   itemData['stock']))
        self.logAction("lookUpById", readItemQuery)
        return itemData

    def addItem(self):
        print("All values must be entered to insert an item\n")
        name = input("Enter product name\n").lower()
        price = Decimal128(input("Enter product price\n"))
        stock = int(input("Enter amount of stock\n"))
        inSale = int(input("Product in sale? 0 = No | 1 = Yes\n"))
        saleAmount = int(input("Enter sale amount\n"))
        stockCollection = self.getStockCollection()
        addItemQuery = {"_id": self.getCounterId(), "itemName": name, "price": price, "stock": stock, "inSale": inSale,
                        "saleAmount": saleAmount}
        stockCollection.insert_one(addItemQuery)
        self.logAction("addItem", addItemQuery)

    def updateStock(self):
        itemData = self.readItemByName()
        stockCollection = self.getStockCollection()
        stockIncrement = int(input("Enter how much you would like to modify the stock by\n"))
        updateStockQuery = {"_id": itemData["_id"]}, {"$inc": {"stock": stockIncrement}}
        updatedStock = stockCollection.find_one_and_update(updateStockQuery, return_document=ReturnDocument.AFTER)
        print("------------Updated-Stock------------")
        print(
            "ID - {} | Item Name - {} | Price - {} | Stock Amount - {}".format(updatedStock["_id"],
                                                                               updatedStock["itemName"],
                                                                               updatedStock["price"],
                                                                               updatedStock['stock']))
        self.logAction("modifyStock", updateStockQuery)

    def updateSale(self):
        itemData = self.readItemByName()
        stockCollection = self.getStockCollection()
        saleOption = int(input("1: Add sale\n"
                               "2: Remove sale\n"))

        saleAmount = int(input("Enter the sale amount\n"))
        updateSaleQuery = {"_id": itemData["_id"]}, {"$set": {"inSale": saleOption, "saleAmount": saleAmount}}
        updatedStock = stockCollection.find_one_and_update(*updateSaleQuery, return_document=ReturnDocument.AFTER)
        salePrice = float(updatedStock["price"]) / 100 * updatedStock["saleAmount"]
        print("ID - {} | Item Name - {} | *New Price* - {} | Sale Amount - {} ".format(updatedStock["_id"],
                                                                                       updatedStock["itemName"],
                                                                                       salePrice,
                                                                                       updatedStock['saleAmount']))
        self.logAction("updateSale", updateSaleQuery)

    def removeItemByName(self):
        itemData = self.readItemByName()
        stockCollection = self.getStockCollection()
        removeOption = int(input("Are you sure you want to remove this item? 1 : Yes | 2: No\n"))
        if removeOption == 1:
            stockCollection.delete_one(itemData)
            self.logAction("RemoveItemByName", itemData)
        else:
            pass

    def logAction(self, actionTaken, collection):
        myDb = self.connectToDatabase()
        actionLogCollection = myDb.actionLog
        actionLogCollection.insert_one(
            {"userId": self.userId, actionTaken: collection,
             "TimeAndDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    def addStaffMember(self):
        # TODO 1) show that the account has been created with the user id generated
        myDb = self.connectToDatabase()
        employeesCollection = myDb.employees
        fName = input("Enter employees first name\n")
        sName = input("Enter employees second name\n")
        password = input("Enter employees password\n")
        role = input("Enter employees role\n")
        addStaffQuery = {"fName": fName, "sName": sName, "userId": self.getCounterId(), "password": password,
                         "role": role}
        employeesCollection.insert_one(addStaffQuery)
        self.logAction("addStaffMember", addStaffQuery)

    def deleteStaffMember(self):
        myDb = self.connectToDatabase()
        employeesCollection = myDb.employees
        idToDelete = int(input("Enter the id of the user you wish you remove\n"))
        deleteStaffQuery = {"userId": idToDelete}
        employeesCollection.delete_one(deleteStaffQuery)
        self.logAction("deleteStaffMember", deleteStaffQuery)

    def updateStaffMember(self):
        myDb = self.connectToDatabase()
        employeeCollection = myDb.employees
        userToModify = int(input("Enter your user id\n"))
        sName = input("Enter your updated second name\n")
        updateUserQuery = {"userId": userToModify}, {"$set": {"sName": sName}}
        updatedEmployee = employeeCollection.find_one_and_update(*updateUserQuery, return_document=ReturnDocument.AFTER)
        print("userID - {} | Name - {} {}".format(updatedEmployee["userId"], updatedEmployee["fName"],
                                                  updatedEmployee["sName"]))

    def readAllStaff(self):
        myDb = self.connectToDatabase()
        employeeCollection = myDb.employees
        employees = employeeCollection.find()
        for employee in employees:
            print("ID - {} | Name - {} {} | Role - {}".format(employee["userId"], employee["fName"], employee["sName"],
                                                              employee["role"]))
        self.logAction("lookupAll", {})

    def shutDown(self):
        self.running = False


newTill = Till(1, 101, 111)
newTill.startup()
