from apify_client import ApifyClient

def scrape_instagram_profile(username):
    #Initialize the ApifyClient with your API token
    client = ApifyClient("apify_api_RD5dC9E6UUmLh7zsNb7p0xmCEKBvHP1NnBZP")
    
    #Use a specific actor for scraping (e.g , Instagram scraper)
    actor_id = "apify/instagram-scraper"
    
    
    #Run the actor with the required input
    run = client.actor(actor_id).call (
        run_input = {
            "usrname": username,
            "resultsLimit": 10,
        }
    )
    
    #Fetch the results
    return run ["defaultDatasetId"]