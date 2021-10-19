#generates a request for a Google Maps API geolocation service
#this has to be a POST request and as such a simple URL will not suffice
#returns the generated request without sending it
from os import close
from types import resolve_bases


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

#given a list of restaurants, returns only those 
#which are open currently 
def getOpenRestaurants(restaurantList):

    #ensure input is a list
    restaurantList = getSearchResultsAsList(restaurantList)

    openRestaurantList = []

    #iterate through list of places to find ones that are open
    for placeData in restaurantList:

        if placeData['opening_hours']['open_now']:
            
            openRestaurantList.append(placeData)
            

    return openRestaurantList


#given the results of a search request,
#picks out one location and returns its index in the search results
#Does NOT return the actual item; if you want to return the item
#instead of an index, use the pickRestaurant function instead (defined below)
#if excludeIds is set to a list of placeIds, places with those ids won't be chosen
def pickRestaurantIndex(searchResults, excludeKeys=None):
    from random import randrange
    
    #get search results as list, if it wasn't one already
    searchResultsList = getSearchResultsAsList(searchResults)
    
    #pick a random place's index
    return randrange(0, len(searchResultsList))


#uses pickRestaurantIndex to select a random
#restaurant, then return the details of the restaurant
#see pickRestaurantIndex definition for more details
def pickRestaurant(searchResults):

    searchResultsList = getSearchResultsAsList(searchResults)
    restaurantIndex = pickRestaurantIndex(searchResultsList)
    return searchResultsList[restaurantIndex]


#given a place id (from the Maps API),
#return a URL that points to that location
#on the Google Maps website.
#note that this DOES NOT require an API call; 
#this is simply creating a URL that the user
#can put into their browser
def getPlaceLink(placeId):
    
    placeLink = f"https://www.google.com/maps/place/?q=place_id:{placeId}"
    return placeLink

#generates and prints a Google Maps link to a place, given a place id
#surrounds it with space using newlines so it's easier to copy+paste
def printPlaceLink(placeId):
    
    placeLink = getPlaceLink(placeId)
    print(f"\n\n{placeLink}\n\n")


#given a Place object (as returned by the pickRestaurant function),
#print Place information that is relevant to the user to the console
#(this includes the name, full address, rating, price level, and Google Maps URL)
def printInfoForUser(selectedPlace):
    
    #print the place name
    print(f"***  {selectedPlace['name']}  ***")

    #print the place address
    print(f"{selectedPlace['formatted_address']}")

    #print the place's price level, if it exists
    try:
        print(f"Price level: {selectedPlace['price_level']} out of 3")
    except KeyError:
        print("Price level unknown")

    try:
        #print the place's rating along with the number of reviews
        print(f"Rated {selectedPlace['rating']} out of 5 stars (from {selectedPlace['user_ratings_total']} reviews)")
    except KeyError:
        print("Rating unknown")

    #indicate that this place is closed if appropriate
    if not selectedPlace['opening_hours']['open_now']:
        print ('### Currently Closed ###')
    
    #print an empty line to signify the end of info
    print()


#asks the user for a yes or no
#uses a loop to repeat the question if input is invalid
#returns a boolean true/false representing the user's choice
def promptYesNo(promptText):
    
    #input validation loop
    #when valid input is recieved, the function
    #returns, exiting this loop
    while True:
        #prompt user for input
        #this is done inside a loop so that the prompt can be repeated 
        userInput = input(promptText)
        
        #store user input in lowercase
        #all checks against the value of the userInput
        #are done against this, meaning the actual case of the letters
        #the user typed doesn't matter 
        lowercaseUserInput = userInput.lower()

        #'parse' user input into a boolean 
        if lowercaseUserInput in ('y', 'yes'):
            return True
        elif lowercaseUserInput in ('n', 'no'):
            return False
        else:
            #print message and continue loop if input invalid
            print(f"Invalid input: {userInput}")


#ask the user if the specified location is acceptable
#prompt for a (y)es or (n)o
#handles invalid input by repeating the prompt
def askIfAcceptable(restaurantName = None):

    #set restaurantName to something generic if no name was specified
    if restaurantName == None:
        restaurantName = "this restaurant"

    promptText = f"Is {restaurantName} acceptable? (input 'y' for yes or 'n' for no): "

    return promptYesNo(promptText)


#returns the results of a Maps request for use with the interactivePrompt
def getNearbyRestaurants(userLocation=None, searchRange = 10000, searchText = "restaurant"):
    
    if userLocation == None:
        #get the user's location if it wasn't provided
        userLocation = executeGeolocationRequest()['location']
    else:
        #attempt to extract location data from a geolocation response
        try:
            userLocation = userLocation['location']
        except KeyError:
            #if a key error is raised, it's possible the location data
            #is already in the correct format.
            #if the proper keys are in this dict,
            #the KeyError is suppressed
            locationKeys = userLocation.keys()
            if 'lat' in locationKeys and 'lng' in locationKeys:
                pass
            else:
                #if either key is missing, the event is not suppressed
                raise

    #generate a search request
    #this is done outside of executePlaceSearchRequest so that adding more options
    #(such as range limiting or different search text) is easier
    searchRequest = generatePlaceSearchRequest(
        userLocation['lat'], userLocation['lng'], 
        searchText, searchRange)

    restaurants = executePlaceSearchRequest(searchRequest)

    return restaurants


#an interactive prompt to select a restaurant
#- userLocation param, if set, is used as the user's location data
#  if not set, the result of executeGeolocationRequest is used instead
#
#- includeClosed param is a boolean representing whether or not to include
#  closed locations in the output
#  note: if the user rejects every open location, they will be prompted to 
#  change this option during runtime. This does NOT call any APIs again
#
#- searchRange param is the range to search for in meters
#  
def interactivePrompt(userLocation = None,  includeClosed = False, searchRange = 10000):

    #execute relevant requests if list of restaurants is not provided
    if userLocation == None:
        userLocation = executeGeolocationRequest()
    
    restaurants = getNearbyRestaurants(userLocation, searchRange)

    #convert restaurants to list, if it wasn't one already
    restaurants = getSearchResultsAsList(restaurants)

    #return -1 if no restaurants found at this stage
    if len(restaurants) == 0:
        print("No restaurants found within this range!")
        return -1

    if not includeClosed:
        #narrow down restaurants to only those which are currently open
        relevantRestaurants = getOpenRestaurants(restaurants)
        
        #get a list of closed restaurants (to expand search with, if needed)
        closedRestaurants = []
        for restaurant in restaurants:
            if restaurant not in relevantRestaurants:
                closedRestaurants.append(restaurant)

        #if no restaurants are relevant, that means all restaurants were closed
        #however, because of the length check before excluding closed locations,
        #the fact that this is being executed means there are some restaurants to display
        #therefore, auto-set includeClosed to true
        if len(relevantRestaurants) == 0:
            print("All restaurants are closed! Showing closed locations")
            includeClosed = True
            relevantRestaurants = restaurants
        
    else:
        #if includeClosed is true, all restaurants are relevant
        #closedRestaurants is not set in this case as it would never be used
        relevantRestaurants = restaurants    

    print("You should eat at:")

    #loop until user likes what was selected
    userLikesChoice = False
    while not userLikesChoice:

        #pick a restaurant index at random
        selectedRestaurantIndex = pickRestaurantIndex(relevantRestaurants)
        #pop that restaurant from the list so that it isn't repeated
        selectedRestaurant = relevantRestaurants.pop(selectedRestaurantIndex)

        #print info on the restaurant that 
        #would be relevant to the user
        printInfoForUser(selectedRestaurant)

        #prompt the user if the selected restaurant is acceptable
        userLikesChoice = askIfAcceptable(selectedRestaurant['name'])

        #if the user accepts the restaurant, print a Google Maps link
        #to the location, then return the selected restaurant
        if userLikesChoice:
            print("Fortunate! Here is a link:")
            printPlaceLink(selectedRestaurant['place_id'])
            return selectedRestaurant
        else:
            #continue if there are more restaurants in the list
            if len(relevantRestaurants) > 0:
                print("\nUnfortunate! How about:") 
                continue  
            else:
                #if restaurant list is empty, ask to change options to include more restaurants
                print("Super Unfortunate! You have exhausted the restaurants in your area.")

                #prompt user to expand search to closed locations,
                #if they weren't already included
                if not includeClosed:
                    if promptYesNo("Include closed locations in results? (y/n): "):
                        #set includeClosed so this prompt is not shown again
                        includeClosed = True
                        #set the relevantRestaurants list
                        #to the closed restaurants that were not shown earlier
                        relevantRestaurants = closedRestaurants
                        #continue loop to iterate through closedRestaurants
                        print("How about:")
                        continue
                
                        
                #return None if no restaurant was selected and 
                #all options to expand have been exhausted
                print("Sorry I couldn't help :(")
                return None



#if this module is called as a script, run the
#interactive prompt
if __name__ == "__main__":
    interactivePrompt()
