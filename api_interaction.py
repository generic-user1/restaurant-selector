
#api interaction
#Functions used to interact with the Google Maps API
#Everything that interacts directly with the API is stored here;
#API calls in the main script happen using functions from this one

#generates a request for a Google Maps API geolocation service
#this has to be a POST request and as such a simple URL will not suffice
#returns the generated request without sending it
from urllib import request


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


#given a pagetoken for the next page of results, generate a Maps API request
#and return the generated url as text
def generateNextPageRequest(nextPageToken):
    from key_management import getApiKey
    apikey = getApiKey()

    urlBase = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    pagetokenParam = f"pagetoken={nextPageToken}"

    keyParam = f"key={apikey}"

    requestText = f"{urlBase}{pagetokenParam}&{keyParam}"

    return requestText


#given a pagetoken for the next page of results, execute a Maps API request
#to request the next page and return the result
def executeNextPageRequest(nextPageToken):
    from urllib.request import urlopen
    from json import loads as parseJsonString
    from json.decoder import JSONDecodeError
   
    requestText = generateNextPageRequest(nextPageToken)

    searchResponse = urlopen(requestText)
    searchResponseText = searchResponse.read().decode()

    try:
        parsedResponse = parseJsonString(searchResponseText)
        return parsedResponse
    except JSONDecodeError:
        print(f"Attempted to parse {searchResponseText} as JSON, but it was invalid")
        raise


#given the result of a Place search request,
#returns a generator object that will return
#each 20-place 'page' of search results
def getSearchResultPages(searchRequestResults):

    #loop until there are no more search result pages to
    #display. this check happens AFTER the first page is yielded,
    #so it is always returned
    hasNextPage = True
    while hasNextPage:
        yield searchRequestResults['results']

        hasNextPage = "next_page_token" in searchRequestResults.keys()
        
        if hasNextPage:
            #if there is a next page, execute another search request 
            #to retrieve the next page and set searchRequestResults
            searchRequestResults = executeNextPageRequest(searchRequestResults['next_page_token'])

        #if there is no next page, break the loop and end
        else:
            break