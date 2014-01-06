import android
from kol.Session import Session
from kol.request.CharpaneRequest import CharpaneRequest
from kol.request.InventoryRequest import InventoryRequest
from kol.Error import Error
import os
droid = android.Android()

login = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android" android:id="@+id/background" android:orientation="vertical" android:layout_width="match_parent" android:layout_height="match_parent" android:background="#ff000000">
	<TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="Login" android:id="@+id/textView1" android:textAppearance="?android:attr/textAppearanceLarge" android:gravity="center_vertical|center_horizontal|center"></TextView>
	<EditText android:layout_width="match_parent" android:layout_height="wrap_content" android:id="@+id/editText1" android:tag="First stuff" android:inputType="text">
		<requestFocus></requestFocus>
	</EditText>
	<EditText android:layout_width="match_parent" android:layout_height="wrap_content" android:id="@+id/editText2" android:tag="Stuff" android:inputType="textPassword"></EditText>
	<CheckBox android:layout_height="wrap_content" android:id="@+id/checkBox1" android:layout_width="234dp" android:text="Remember me" android:checked="false"></CheckBox>
	<LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:id="@+id/linearLayout1">
		<Button android:id="@+id/button2" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Ok"></Button>
		<Button android:id="@+id/button3" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Cancel"></Button>
	</LinearLayout>
</LinearLayout>
"""
main = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android" android:id="@+id/background" android:orientation="vertical" android:layout_width="match_parent" android:layout_height="match_parent" android:background="#ff000000">
	<TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="Main menu" android:id="@+id/textView" android:textAppearance="?android:attr/textAppearanceLarge" android:gravity="center_vertical|center_horizontal|center"></TextView>
	<Button android:id="@+id/charData" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Character Data"></Button>
	<Button android:id="@+id/inventory" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Get Inventory"></Button>
	<Button android:id="@+id/findinventory" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Find in inventory"></Button>
	<Button android:id="@+id/quit" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Quit"></Button>
</LinearLayout>
"""

s = Session()
def eventloop():
	global s
	while True:
		event = droid.eventWait().result
		if event["name"] == "key" and event["data"]["key"] == "4":
			return
		if event["name"] == "click":
			id = event["data"]["id"]
			if id == "button3":
				return
			elif id == "button2":
				try:
					title = "Logging in..."
					message = 'KoL for Android is logging you in...'
					droid.dialogCreateSpinnerProgress(title, message)
					droid.dialogShow()
					try:
						s.login(droid.fullQueryDetail("editText1").result["text"], droid.fullQueryDetail("editText2").result["text"])
						if droid.fullQueryDetail("checkBox1").result["checked"]:
							droid.prefPutValue("user", droid.fullQueryDetail("editText1").result["text"], "kolsettings")
							droid.prefPutValue("pass", droid.fullQueryDetail("editText2").result["text"], "kolsettings")
	 	 	 	 	 	return
					except Error as e:
						droid.dialogDismiss()
						droid.makeToast(e.msg)
					except:
						if droid.wifiGetConnectionInfo().result["network_id"] == -1:
							droid.dialogDismiss()
							droid.makeToast("WiFi not connected!")
					finally:
						droid.dialogDismiss()
				except:
					droid.dialogDismiss()
		elif event["name"]=="screen":
			if event["data"]=="destroy":
				return
def mainloop():
	global s
	while True:
		event = droid.eventWait().result
		if event["name"] == "key" and event["data"]["key"] == "4":
			return
		if event["name"] == "click":
			id = event["data"]["id"]
			if id == "charData":
				droid.dialogCreateSpinnerProgress("Loading", "Loading...")
				droid.dialogShow()
				c = CharpaneRequest(s)
				response = c.doRequest()
				title = "Character data"
				message = ""
				for key in response.keys():
					message += "%s: %s\n" % (key, response[key])
				droid.dialogDismiss()
				droid.dialogCreateAlert(title, message)
				droid.dialogSetPositiveButtonText("OK")
				droid.dialogShow()
	 	 	elif id == "inventory":
				droid.dialogCreateSpinnerProgress("Loading", "Loading...")
				droid.dialogShow()
	 	 	 	i = InventoryRequest(s)
	 	 	 	response = i.doRequest()
	 	 	 	title = "Inventory"
	 	 	 	message = ""
	 	 	 	for key in response["items"]:
	 	 	 	 	message += "%s: %s\n" % (key["name"], key["quantity"])
				droid.dialogDismiss()
	 	 	 	droid.dialogCreateAlert(title, message)
	 	 	 	droid.dialogSetPositiveButtonText("OK")
	 	 	 	droid.dialogShow()
			elif id == "findinventory":
				droid.dialogCreateInput("Item to find:", "Enter the name (or partial name) of the item to find")
				droid.dialogSetPositiveButtonText("OK")
				droid.dialogSetNegativeButtonText("Cancel")
				droid.dialogShow()
				response = droid.dialogGetResponse().result
				if response.has_key("which") and response["which"] == "positive" and response.has_key("value") and response["value"] != "":
					droid.dialogCreateSpinnerProgress("Searching...", "Finding items...")
					droid.dialogShow()
					i = InventoryRequest(s)
					inventory = i.doRequest()
					title = "Search results"
					message = ""
					for item in inventory["items"]:
						if item.has_key("name") and response["value"] in item["name"]:
							message += "%s: %s\n" % (item["name"], item["quantity"])
					if message == "":
						message = "No item matching %s was found" % response["value"]
					droid.dialogDismiss()
					droid.dialogCreateAlert(title, message)
					droid.dialogSetPositiveButtonText("OK")
					droid.dialogShow()
				pass
			elif id == "quit":
				return
print "Started"

droid.fullShow(login, "Login")
droid.dialogCreateAlert("KoL for Android", "Welcome to KoL for Android v0.1. This script is in alpha, and will not work as expected.")
droid.dialogSetPositiveButtonText('Continue')
droid.dialogShow()
eventloop()
droid.fullDismiss()
if s.isConnected:
	droid.fullShow(main)
	mainloop()
droid.fullDismiss()