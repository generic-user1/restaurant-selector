
#interactive prompt
#the interactivePrompt function,
#and related helper functions

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
    from api_interaction import executeGeolocationRequest, getSearchResultsAsList
    from restaurant_selector import getNearbyRestaurants, getOpenRestaurants, pickRestaurantIndex
    from output_formatting import printInfoForUser, printPlaceLink

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
        promptText = f"Is {selectedRestaurant['name']} acceptable? (input 'y' for yes or 'n' for no): "
        userLikesChoice = promptYesNo(promptText)

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