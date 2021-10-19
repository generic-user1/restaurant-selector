
#output formatting
#functions to print information in defined, 
#human readable formats


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



