

#checks an API key to see if it's valid (format wise)
#returns True if it's valid, False otherwise
def apiKeyIsValid(apiKey):
    from re import match

    API_KEY_PATTERN = "AIza[0-9A-Za-z-_]{35}"

    return bool(match(API_KEY_PATTERN, apiKey))


#reads a file that contains the API key
#there is most likely a better way to do this (possibly with environment variables),
#but this works and *I think* it's secure enough
#if nothing else, this is better than just pasting the key into the code
def getApiKey(keyFilePath = "./apikey.txt"):

    with open(keyFilePath, 'r') as keyFile:
        
        apiKey = keyFile.read()
    
    if apiKeyIsValid(apiKey):
        return apiKey
    else:
        raise ValueError(f"API key found in {keyFilePath} is invalid!")


#define a testing function
def key_management_test():

    apiKey = getApiKey()

    print("api key retrieved :", apiKey)


#if this module is run as a script, run the testing function
if __name__ == "__main__":
    key_management_test()