###################################################################################################
# Introduction:	This program sends a HTTP GET request to Bungie's servers and reads Xurs inventory
# 				It will then take the encrypted itemHash and send another request for the items full details. 
# 				This code has been updated to add email functionality.
# 				For details on how to use this code, visit:
#				http://allynh.com/blog/creating-a-python-app-for-destiny-part-2-emailing-xurs-inventory/
#				Important note: This code will only work from 10am Friday morning to 10am Sunday morning (GMT time)!
#
# Usage:		python Get_Xur_inventory_email.py
# Created by:	Allyn Hunt - www.AllynH.com
###################################################################################################

import requests
import json
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Uncomment this line to print JSON output to a file:
#f = open('output.txt', 'w')

HEADERS = {"X-API-Key":'YOUR-X-API-Key'}

# Mail parameters:
fromaddr = "TO_ADDRESS"
toaddr = "FROM_ADDRESS"
password = "GMAIL_PASSWORD"

# Set required URLs:
base_url = "https://www.bungie.net/platform/Destiny/"
xur_url = "https://www.bungie.net/Platform/Destiny/Advisors/Xur/"
hashType = "6"

# Open our HTML template file:
template_file = open('template.html', "r")
my_html = template_file.read()
template_file.close()

# Send the request and store the result in res:
print "\n\n\nConnecting to Bungie: " + xur_url + "\n"
print "Fetching data for: Xur's Inventory!"
res = requests.get(xur_url, headers=HEADERS)

# Print the error status:
error_stat = res.json()['ErrorStatus']
print "Error status: " + error_stat + "\n"

# Quit if Xur is not here:
if error_stat != "Success":
	print "Xur is not here - quitting!"
	quit()

# Uncomment this line to print JSON output to a file:
#f.write(json.dumps(res.json(), indent=4))

print "##################################################"
print "## Printing Xur's inventory:"
print "##################################################"

for saleItem in res.json()['Response']['data']['saleItemCategories']:
	mysaleItems = saleItem['saleItems']
	for myItem in mysaleItems:
		hashID = str(myItem['item']['itemHash'])
		hashReqString = base_url + "Manifest/" + hashType + "/" + hashID
		res = requests.get(hashReqString, headers=HEADERS)
		item_name = res.json()['Response']['data']['inventoryItem']['itemName']
		item_type = res.json()['Response']['data']['inventoryItem']['itemTypeName']
		item_tier = res.json()['Response']['data']['inventoryItem']['tierTypeName']
		item_description = res.json()['Response']['data']['inventoryItem']['itemDescription'].encode('utf-8')
		item_url = "http://www.bungie.net/" + res.json()['Response']['data']['inventoryItem']['icon']
		# Uncomment this line to print JSON output to a file:
		#f.write(json.dumps(res.json(), indent=4))
		print "Item is: " + item_name
		print "Item type is: " + item_tier + " " + item_type + "\n"
		print "Item description: " + item_description + "\n"
		my_html = my_html + "\t\t<div class=\"col-md-4\">\n"
		my_html = my_html + "\t\t\t<div class=\"thumbnail\">\n"
		my_html = my_html + "\t\t\t\t<a href=\"" + item_url + "\">\n"
		my_html = my_html + "\t\t\t\t<img src=\"" + item_url + "\">\n"
		my_html = my_html + "\t\t\t\t</a>\n"
		my_html = my_html + "\t\t\t\t<h3>" + item_name + "</h3>\n"
		my_html = my_html + "\t\t\t\t<p>" + item_type + "</p>\n"
		my_html = my_html + "\t\t\t\t<p>" + item_description.decode('utf-8') + "</p>\n"
		my_html = my_html + "\t\t\t</div>\n"
		my_html = my_html + "\t\t</div>\n"

# Close the HTML file:
my_html = my_html + "\t</div> <!-- row -->"
my_html = my_html + "\t</div> <!-- container -->"
my_html = my_html + "</div> <!-- inventory-container -->"
my_html = my_html + "</body>"
my_html = my_html + "</html>"

# Compose mail:
msgRoot = MIMEMultipart('related')
msgRoot['From'] = fromaddr
msgRoot['To'] = toaddr
msgRoot['Subject'] = "Emailing Xurs Inventory!"

msgAlternative = MIMEMultipart('testing')
msgRoot.attach(msgAlternative)
msgText = MIMEText(my_html.encode('utf-8'), 'html')
msgAlternative.attach(msgText)

# Login to Gmail port 587:
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.login(fromaddr, password)
# Send mail and quit:
server.sendmail(fromaddr, toaddr, msgRoot.as_string())
server.quit()