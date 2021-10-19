
#api interaction
#Functions used to interact with the Google Maps API
#Everything that interacts directly with the API is stored here;
#API calls in the main script happen using functions from this one

#generates a request for a Google Maps API geolocation service
#this has to be a POST request and as such a simple URL will not suffice
#returns the generated request without sending it
def generateGeolocationRequest():
    from urllib.request import Request
    from key_management import getApiKey
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
def executeGeolocationRequest(request = None):
    from urllib.request import urlopen
    from json import loads as parseJsonString
    from json.decoder import JSONDecodeError
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
    from key_management import getApiKey

    apikey = getApiKey()

    urlBase = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    locationParam = f"location={latitude}%2C{longitude}"

    queryParam = f"query={encodeForUrl(searchText)}"

    radiusParam = f"radius={range}"

    keyParam = f"key={apikey}"

    requestText = f"{urlBase}{locationParam}&{queryParam}&{radiusParam}&{keyParam}"

    return requestText


#gets the users location and uses it as the basis of a restaurant search
#return results as a dict
def executePlaceSearchRequest(searchRequestText = None, locationData = None):
    from urllib.request import urlopen
    from json import loads as parseJsonString
    from json.decoder import JSONDecodeError

    if searchRequestText == None and locationData == None:
        locationData = executeGeolocationRequest()

    if searchRequestText == None:
        latitude = locationData['location']['lat']
        longitude = locationData['location']['lng']
        searchRequestText = generatePlaceSearchRequest(latitude, longitude)

    searchResponse = urlopen(searchRequestText)
    searchResponseText = searchResponse.read().decode()

    try:
        parsedResponse = parseJsonString(searchResponseText)
        return parsedResponse
    except JSONDecodeError:
        print(f"Attempted to parse {searchResponseText} as JSON, but it was invalid")
        raise

#given a dict from executePlaceSearchRequest, attempts to return 
#the 'results' list. If a key error occurs (most likely due to unexpected
# API behavior), returns unmodified input
#if input is already a list, returns it unmodified
def getSearchResultsAsList(searchResults):

    #test if list
    if isinstance(searchResults, list):
        #if input is a list, return it immediately
        return searchResults

    #if not a list, attempt to get as a list
    try:
        resultList = searchResults['results']
    except KeyError:
        #if a key error occurs, return unmodified input
        resultList = searchResults

    return resultList