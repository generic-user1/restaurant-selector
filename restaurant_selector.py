
#restaurant selector
#functions related to selecting a restaurant near the user


#returns the results of a Maps request for use with the interactivePrompt
def getNearbyRestaurants(userLocation=None, searchRange = 10000, searchText = "restaurant"):
    from api_interaction import executeGeolocationRequest, generatePlaceSearchRequest, executePlaceSearchRequest    


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

#given a list of restaurants, returns only those 
#which are open currently 
def getOpenRestaurants(restaurantList):
    from api_interaction import getSearchResultsAsList

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
def pickRestaurantIndex(searchResults):
    from random import randrange
    from api_interaction import getSearchResultsAsList
    
    #get search results as list, if it wasn't one already
    searchResultsList = getSearchResultsAsList(searchResults)
    
    #pick a random place's index
    return randrange(0, len(searchResultsList))


#uses pickRestaurantIndex to select a random
#restaurant, then return the details of the restaurant
#see pickRestaurantIndex definition for more details
def pickRestaurant(searchResults):
    from api_interaction import getSearchResultsAsList

    searchResultsList = getSearchResultsAsList(searchResults)
    restaurantIndex = pickRestaurantIndex(searchResultsList)
    return searchResultsList[restaurantIndex]


