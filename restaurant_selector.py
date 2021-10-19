
#restaurant selector
#helps to select a restaurant by listing locations
#in the user's area in a random order

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


#given a list of restaurants, returns 2 lists:
#the first is the standard list of open restaurants, the second
#is all of the closed restaurants
def splitRestaurantsByOpenStatus(restaurantList):

    openRestaurantList = []
    
    closedRestaurantList = []

    #iterate through list of places to find ones that are open
    for placeData in restaurantList:

        #if the place is open now, append it to the open list
        if placeData['opening_hours']['open_now']:
            openRestaurantList.append(placeData)
        
        else:
            closedRestaurantList.append(placeData)

    
    return (openRestaurantList, closedRestaurantList)


#returns the paged results of a Maps request for use with the interactivePrompt
#this is in the form of an iterable, with each page of the results being a member
#there may be anywhere from 1 to 3 pages
def getNearbyRestaurants(userLocation=None, searchRange = 10000, searchText = "restaurant"):
    from api_interaction import executeGeolocationRequest, generatePlaceSearchRequest
    from api_interaction import executePlaceSearchRequest, getSearchResultPages   


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

    restaurantSearchResults = executePlaceSearchRequest(searchRequest)

    #get a page generator from the search results
    searchResultPages = getSearchResultPages(restaurantSearchResults)

    return searchResultPages



#given a list of restaurants (preferably a shuffled one),
#prompts the user to accept each one in succession
#returns the data of the restaurant that was accepted,
#or None if the list was exhausted before a place was accepted
def promptRestaurants(restaurantList):
    from output_formatting import printInfoForUser, printPlaceLink

    for restaurant in restaurantList:

        print("You should eat at:")

        #print info on the restaurant that 
        #would be relevant to the user
        printInfoForUser(restaurant)

        #prompt the user if the selected restaurant is acceptable
        promptText = f"Is {restaurant['name']} acceptable? (input 'y' for yes or 'n' for no): "
        if promptYesNo(promptText):
            #if the user accepts the restaurant, print a Google Maps link
            #to the location, then return the selected restaurant
            print("Fortunate! Here is a link:")
            printPlaceLink(restaurant['place_id'])
            return restaurant
        
        #if the user doesn't like the restaurant,
        #print a message and continue the loop
        else:
            print("Unfortunate!\n")

    #if the end of the loop is reached, None is returned
    #this indicates that none of the restaurants in the list 
    #were selected
        

#an interactive prompt to select a restaurant
#- userLocation param, if set, is used as the user's location data
#  if not set, the result of executeGeolocationRequest is used instead
#
#- searchRange param is the range to search for in meters
#  
def interactivePrompt(userLocation = None, searchRange = 10000):
    from api_interaction import executeGeolocationRequest
    from restaurant_selector import getNearbyRestaurants, splitRestaurantsByOpenStatus
    from random import shuffle

    #get user location if it isn't provided
    if userLocation == None:
        userLocation = executeGeolocationRequest()
    
    #get a list of pages, where each page is a list of up to 20 restaurants
    restaurantPages = getNearbyRestaurants(userLocation, searchRange)

    for restaurantPage in restaurantPages:

        #return None if no restaurants found at this stage
        if len(restaurantPage) == 0:
            print("No restaurants found within this range!")
            return None

        #shuffle the list of restaurants so they appear in a random order
        shuffle(restaurantPage)

        #split the restaurant list into open and closed restaurants
        openRestaurants, closedRestaurants = splitRestaurantsByOpenStatus(restaurantPage)

        #check the number of open restaurants
        if len(openRestaurants) > 0:
            #if at least one restaurant is open, show open restaurants first
            selectedRestaurant = promptRestaurants(openRestaurants)
            #if selectedRestaurant is not none,
            #return it
            if selectedRestaurant != None:
                return selectedRestaurant
            #if selected restaurant is none, print a message
            #indicating no more open restaurants
            print("No more open restaurants within range!")
        else:
            print("No open restaurants within range!")


        #if there are only closed restaurants, 
        #prompt for them immediately
        #this same code is executed if no open restaurants are selected
        if promptYesNo("Show closed restaurants? (y/n): "):
            selectedRestaurant = promptRestaurants(closedRestaurants)

            if selectedRestaurant != None:
                return selectedRestaurant

        #if all restaurants on this page are exhausted,
        #prompt user to go to the next page
        if promptYesNo("All restaurants within range have been rejected! Expand range? (y/n): "):
            continue
        else:
            break

    #if this point is reached, all results have been exhausted
    #print a message and return none
    print("No more restaurants in range. Sorry we couldn't help!")
        


#if this module is called as a script, run the
#interactive prompt
if __name__ == "__main__":
    interactivePrompt()