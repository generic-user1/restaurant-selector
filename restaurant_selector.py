

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

    keyParam = f"key={apikey}"

    requestText = f"{urlBase}{locationParam}&{queryParam}&{keyParam}"

    return requestText


#gets the users location and uses it as the basis of a restaurant search
#return results as a dict
def executePlaceSearchRequest(locationData = None):
    from urllib.request import urlopen
    from json import loads as parseJsonString
    from json.decoder import JSONDecodeError

    if locationData == None:
        locationData = executeGeolocationRequest()

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
    

#given the results of a search request,
#picks out one location that is currently open
#and returns all details on it
#if onlyOpen is false, skips checking for open status
def pickRestaurant(searchResults, onlyOpen = True):
    from random import choice
    
    relevantPlaces = []

    if not onlyOpen:
        #if onlyOpen is false, all places are relevant
        relevantPlaces = searchResults['results']
    else:
        #iterate through list of places to find ones that are open
        for placeData in searchResults['results']:

            if placeData['opening_hours']['open_now']:
                relevantPlaces.append(placeData)

    #pick a random place out of the list of relevant ones
    return choice(relevantPlaces)

#given a place id (from the Maps API),
#return a URL that points to that location
#on the Google Maps website.
#note that this DOES NOT require an API call; 
#this is simply creating a URL that the user
#can put into their browser
def getPlaceLink(placeId):
    
    placeLink = f"https://www.google.com/maps/place/?q=place_id:{placeId}"
    return placeLink

#given a Place object (as returned by the pickRestaurant function),
#print Place information that is relevant to the user to the console
#(this includes the name, full address, rating, price level, and Google Maps URL)
def printInfoForUser(selectedPlace):
    
    #print the place name
    print(f"***  {selectedPlace['name']}  ***")

    #print the place address
    print(f"{selectedPlace['formatted_address']}")

    #print the place's rating along with the number of reviews
    print(f"Rated {selectedPlace['rating']} out of 5 stars (from {selectedPlace['user_ratings_total']} reviews)")

    #print the link to the place on Google Maps
    placeLink = getPlaceLink(selectedPlace['place_id'])
    print(f"\n\n{placeLink}\n\n")

#define a testing method
def restaurant_selector_test():
    restaurants = executePlaceSearchRequest()

    selectedRestaurant = pickRestaurant(restaurants)

    printInfoForUser(selectedRestaurant)

#test this module if run as a script
if __name__ == "__main__":
    restaurant_selector_test()
