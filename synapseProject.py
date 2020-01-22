import synapseclient
from synapseclient import Activity
from synapseclient import Entity, Project, Folder, File, Link
from synapseclient import Evaluation, Submission, SubmissionStatus
from synapseclient import Wiki
import calendar
import datetime
import requests


syn = synapseclient.Synapse()



class UserDef: 
    def __init__(self, email, password, phoneNumbers, legalNames):
        myMethods= CleoMethods()
        uri = "https://uat-api.synapsefi.com/v3.1/"
        userBody = {
          "logins": [
            {
              "email": email,
              "password": password
            }
          ],
          "phone_numbers": phoneNumbers,
          "legal_names": legalNames
        }
        self.user_id = syn.restPOST(uri,userBody,"users", **kwargs)
        form = syn.sendMessage (self.user_id, "fill form")
        self.bank_id = connectBankAccount(form[0], form[1], form[2], form[3])

    def connectBankAccount(accountType, encryptedUser, encryptedPW, bank):
        bankBody= {
            "type": accountType,
            "info": {
                "bank_id": encryptedUser,
                "bank_pw": encryptedPW,
                "bank_name": bank
            }
        }
        return( syn.restPOST(uri,bankBody,self.user_id + "/nodes"))
    
    def getTransactions(bills={}, income={}):
        now = datetime.datetime.now()
        month = now.month
        filterDict = {"month": month == month}
        body= { "page": 1,
                "per_page": 20,
                "filter": filterDict
            }
        transactions = syn.restGET(uri, body, self.user_id + "/trans")
        for t in transactions:
            if "note" in bills:
                myMethods.paidBill()
            if "note" in income:
                myMethods.recievedIncome()
        return transactions


    def makeTransactions(amount):
        path = self.user_id+"/nodes/"+self.bank_id+"/trans#"
        body = {"to": {
                    "type": "ACH-US",
                    "id": self.bank_id
                },
                "amount": {
                    "amount": amount,
                    "currency": "USD"
                }
            }
        syn.restPOST(uri, body,path)

bills= {"rent":("monthly", 1000), "electricity":("monthly", 40), "transportation": ("weekly", 33), "coffee": ("daily", 4) }

class CleoMethods:
    def __init__(self,user, income= {}, bills= {}, balance= 0, saving= False, percentSaving= None):
        self.user = UserDef
        self.income = income
        self.bills = bills
        self.saving = saving
        self.balance = balance
        now = datetime.datetime.now()
        daysInMonth=calendar.monthrange(now.year, now.month)[1]
        self.freq = {"monthly": 1, "weekly": 4, "daily": daysInMonth}
        self.monthlyexpenses = monthlyExpenses()
        self.monthlyIncome = monthlyIncome()
        self.budget = self.monthlyIncome - self.monthlyExpenses
        self.paidBill = []
        self.recievedIncome = []
        
        

    def addIncome(name, frequency, amount):
        self.income[name] = [frequency, amount]

    def addBill(name, frequency, amount):
        self.bills[name] = [frequency, amount]

    def monthlyExpenses():
        expenses = 0 
        for ex in self.bills:
            if ex[0] not in self.paidBill:
                expenses += (self.freq[ex[0]]*ex[1])
        if self.saving:
            expenses *= (1+ percentSaving)
        return expenses

    def monthlyIncome():
        monthlyincome = self,balance;
        for i in self.income:
            if i not in self.recievedIncome:
                monthlyincome += (self.freq[i[0]]* i[1])
        return monthlyincome

    def evaluateProgress():
        amountSpent = 0
        day = now.day
        purchases= slef.user.getTransactions(bills, income)
        for t in purchases:
            amountSpent += t.amount();
        percentOfMonth = day/daysInMonth
        budgetPortion = self.budget*percentOfMonth
        dailyBudget = self.budget/daysInMonth
        if (amountSpent < (budgetPortion + dailyBudget) and amountSpent > (budgetPortion - dailyBudget)):
            budgetStatus = "On track"
        elif amountSpent> (budgetPortion+ dailyBudget):
            budgetStatus = "Over"
            adjustBudget()
        else:
            budgetStatus = "Under"
            adjustBudget()

    def moveSavings(amount):
        self.user.makeTransaction(amount)
        adjustBudget()

    def adjustBudget():
        daysLeft= daysInMonth-now.day
        self.user.getTransaction(bills, income)
        monthlyExpenses()

    def paidBill(bill):
        self.paidBill+= bill

    def recievedIncome(check):
        self.recievedIncome += check
    
    
    
