
from json.decoder import JSONDecodeError
import re
from key_management import getApiKey

#generates a request for a Google Maps API geolocation service
#this has to be a POST request and as such a simple URL will not suffice
#returns the generated request without sending it
def generateGeolocationRequest():
    from urllib.request import Request
    apikey = getApiKey()

    baseUrl = "https://www.googleapis.com/geolocation/v1/geolocate?"

    keyParam = f"key={apikey}"

    urlText = f"{baseUrl}{keyParam}"

    postData = """{
        'considerIp': true
}
"""
    return Request(urlText, data = str.encode(postData))


#sends a reqest to get user's location and returns the response as a dictionary
def getLocation(request = None):
    from urllib.request import urlopen
    from json import loads as parseJsonString
    if request == None:
        request = generateGeolocationRequest()

    response = urlopen(request)

    #attempt to decode the response
    #and return results, if valid
    responseText = response.read().decode()

    try:
        parsedResponse = parseJsonString(responseText)
        return parsedResponse
    except JSONDecodeError:
        print(f"Attempted to parse {responseText} as JSON, but it was invalid")
        raise
        
#generates a url for a Google Maps API (text search) request
#returns the generated url WITHOUT actually sending the request
#there is a library to do this, but I need to learn 
#how to manually use web services for a work project 
def generatePlaceSearchRequest(latitude, longitude, searchText = "restaurant", range = 10000):
    from urllib.parse import quote as encodeForUrl

    apikey = getApiKey()

    urlBase = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    locationParam = f"location={latitude}%2C{longitude}"

    queryParam = f"query={encodeForUrl(searchText)}"

    keyParam = f"key={apikey}"

    requestText = f"{urlBase}{locationParam}&{queryParam}&{keyParam}"

    return requestText


#gets the users location and uses it as the basis of a restaurant search
#return results as a dict
def executePlaceSearch(locationData = None):
    from urllib.request import urlopen
    from json import loads as parseJsonString

    if locationData == None:
        locationData = getLocation()

    latitude = locationData['location']['lat']
    longitude = locationData['location']['lng']

    searchRequest = generatePlaceSearchRequest(latitude, longitude)

    searchResponse = urlopen(searchRequest)
    searchResponseText = searchResponse.read().decode()

    try:
        parsedResponse = parseJsonString(searchResponseText)
        return parsedResponse
    except JSONDecodeError:
        print(f"Attempted to parse {searchResponseText} as JSON, but it was invalid")
        raise
    


#define a testing method
def restaurant_selector_test():
    restaurants = executePlaceSearch()

    print(restaurants)

#test this module if run as a script
if __name__ == "__main__":
    restaurant_selector_test()
