import android, sys, json
from kol.Session import Session
from kol.request.CharpaneRequest import CharpaneRequest
from kol.request.InventoryRequest import InventoryRequest
from kol.Error import Error
from kol.manager.ChatManager import ChatManager


droid = android.Android()
s = Session()
charMgr = None
def eventloop():
	global s
	global chatMgr
	while True:
		event = droid.eventWait().result
		if event["name"] == "key" and event["data"]["key"] == "4":
			return
		if event["name"] == "login":
			try:
				title = "Logging in..."
				message = 'KoL for Android is logging you in...'
				droid.dialogCreateSpinnerProgress(title, message)
				droid.dialogShow()
				try:
					loginData = json.loads(event["data"])
					s.login(loginData["user"], loginData["pass"])
					if s.isConnected:
						droid.eventPost("loginResult", "success")
						chatMgr = ChatManager(s)
						return
				except Error as e:
					droid.dialogDismiss()
					droid.eventPost("login", "fail")
					droid.makeToast(e.msg)
				except:
					if droid.wifiGetConnectionInfo().result["network_id"] == -1:
						droid.dialogDismiss()
						droid.makeToast("WiFi not connected!")
					droid.eventPost("login", "fail")
				finally:
					droid.dialogDismiss()
			except:
				droid.dialogDismiss()
		elif event["name"] == "requestLoginInfo":
			objectPost("loginInfo", {"user": droid.prefGetValue("user"), "pass": droid.prefGetValue("pass")})
		elif event["name"] == "exit":
			sys.exit()
			return

def objectPost(name, obj):
	droid.eventPost(name, json.dumps(obj))

def alertNotLoggedIn(exit):
	if exit:
		droid.dialogCreateAlert("Not logged in", "You are no longer connected to the server. KoLDroid will now quit.")
		droid.dialogSetPositiveButtonText("Close")
		droid.dialogShow()
		response = droid.dialogGetResponse().result
		sys.exit()
		return
	else:
		droid.dialogCreateAlert("Not logged in", "You are no longer connected to the server.")
		droid.dialogSetPositiveButtonText("Close")
		droid.dialogShow()
		sys.exit()
		return
# TODO: rewrite mainloop() for use with webview
def mainloop():
	global s
	global chatMgr
	while True:
		event = droid.eventWait().result
		if event["name"] == "key" and event["data"]["key"] == "4":
			return
			
		id = event["name"]
		if id == "makeToast":
			droid.makeToast(event["data"])
		elif id == "charData":
			droid.dialogCreateSpinnerProgress("Loading", "Loading...")
			droid.dialogShow()
			c = CharpaneRequest(s)
			response = None
			try:
				response = c.doRequest()
			except Error as e:
				alertNotLoggedIn(True)
			message = ""
			title = "Character Data"
			for key in response.keys():
				if key != "effects":
					message += "%s: %s\n" % (key, response[key])
				else:
					message += "-------\nEFFECTS:\n"
					for effect in response["effects"]:
						message += " - " + effect["name"] + ": " + str(effect["turns"]) + "\n"
			droid.dialogDismiss()
			droid.dialogCreateAlert(title, message)
			droid.dialogSetPositiveButtonText("OK")
			droid.dialogShow()
			# objectPost("charDataInfo", response)
		elif id == "inventory":
			droid.dialogCreateSpinnerProgress("Loading", "Loading...")
			droid.dialogShow()
			i = InventoryRequest(s)
			response = None
			try:
				response = i.doRequest()
			except Error as e:
				alertNotLoggedIn(True)
			title = "Inventory"
			message = ""
			for key in response["items"]:
				message += "%s: %s\n" % (key["name"], key["quantity"])
			droid.dialogDismiss()
			droid.dialogCreateAlert(title, message)
			droid.dialogSetPositiveButtonText("OK")
			droid.dialogShow()
			# objectPost("inventoryInfo", response)
		elif id == "findInventory":
			droid.dialogCreateInput("Item to find:", "Enter the name (or partial name) of the item to find")
			droid.dialogSetPositiveButtonText("OK")
			droid.dialogSetNegativeButtonText("Cancel")
			droid.dialogShow()
			response = droid.dialogGetResponse().result
			if response.has_key("which") and response["which"] == "positive" and response.has_key("value") and response["value"] != "":
				droid.dialogCreateSpinnerProgress("Searching...", "Finding items...")
				droid.dialogShow()
				i = InventoryRequest(s)
				inventory = None
				try:
					inventory = i.doRequest()
				except Error as e:
					alertNotLoggedIn(True)
				title = "Search results"
				message = ""
				for item in inventory["items"]:
					if item.has_key("name") and response["value"].lower() in item["name"].lower():
						message += "%s: %s\n" % (item["name"], item["quantity"])
				if message == "":
					message = "No item matching %s was found" % response["value"]
				droid.dialogDismiss()
				droid.dialogCreateAlert(title, message)
				droid.dialogSetPositiveButtonText("OK")
				droid.dialogShow()
		elif id == "getNewChat":
			try:
				droid.eventPost("getNewChatResult", "|chatsplitter|".join(json.dumps(chat) for chat in chatMgr.getNewChatMessages()))
			except Error as e:
				alertNotLoggedIn(True)
		elif id == "sendChat":
			try:
				chatMgr.sendChatMessage(event["data"])
				droid.eventPost("sendChatResult", "success")
			except Error as e:
				droid.eventPost("sendChatResult", "fail")
		elif id == "exit":
			sys.exit()
			return

droid.webViewShow(sys.path[0] + "/webview.html")
droid.dialogCreateAlert("KoLMobile", "Welcome to KoLMobile v0.1. This script is in alpha, and will (probably) not work as expected.")
droid.dialogSetPositiveButtonText('Continue')
droid.dialogShow()
eventloop()
if s.isConnected:
	mainloop()