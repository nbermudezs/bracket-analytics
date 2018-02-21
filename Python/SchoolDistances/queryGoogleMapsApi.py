#!/usr/bin/env python
import json
import requests
import sys
from lxml import html
from subprocess import call

def getLatitudeLongitude(address):
	apiKey = 'AIzaSyC5MrI_dBEFEDyzmTjxxNHJE4L0BkMDFAM'
	googleMapsBaseUrl = 'https://maps.googleapis.com/maps/api/geocode/json'

	address = address.replace(' ', '+')
	queryString = '{0}?address={1}&key={2}'.format(googleMapsBaseUrl, address, apiKey)

	# call('curl {0}'.format(queryString), shell=True)
	jsonResponse = requests.get(queryString).text
	# print jsonResponse

	responseDict = json.loads(jsonResponse)
	firstResult = responseDict['results'][0]

	location = firstResult['geometry']['location']
	latitude = location['lat']
	longitude = location['lng']

	return [latitude, longitude]


def searchGoogleForAddress(schoolName):
	cleanedSchoolName = schoolName.replace(' ', '+')
	searchUrl = 'https://www.google.com/search?q={0}'.format(cleanedSchoolName)
	page = requests.get(searchUrl)
	tree = html.fromstring(page.content)

	text = page.text
	index = text.find('Address:')
	nextSpanIndex = text.find('<span', index)

	startAddressIndex = text.find('>', nextSpanIndex) + 1
	endAddressIndex = text.find('<', startAddressIndex)

	address = text[startAddressIndex:endAddressIndex]
	return address

	# print page.text


# This script searches Google to get the address
# of the given school, then calls the Google Maps API
# to get the school's latitude and longitude.

schoolName = str(sys.argv[1])
schoolAddress = searchGoogleForAddress(schoolName)
schoolLatLon = getLatitudeLongitude(schoolAddress)

print '{0}\n\tAddress:\t{1}\n\tLatitude:\t{2}\n\tLongitude:\t{3}\n'.format(schoolName, schoolAddress, schoolLatLon[0], schoolLatLon[1])
