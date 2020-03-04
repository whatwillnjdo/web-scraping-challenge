from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    all_content = {}
    
    #Scrape the latest news
    news_url = "https://mars.nasa.gov/news"
    
    #Beauftiful soup config
    browser.visit(news_url)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    
    #Add the news title and synopsys to all_content dictionary
    all_content["news_title"] = soup.find('div', class_="content_title").text
    all_content["news_synopsis"] = soup.find('div', class_='rollover_description_inner').text
    
    #Scrape the featured image
    pic_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    
    #Beauftiful soup config
    browser.visit(pic_url)
    html = browser.html
    pic_soup = BeautifulSoup(html, 'html.parser')

    #Get the component we need from the scrape
    picture = pic_soup.find('article').find('a').get('data-fancybox-href')
    
    modified_url = pic_url.split('?')[0]
    modified_picture = picture.split('/')[2]+"/"+picture.split('/')[3]+"/"+picture.split('/')[4]
    new_url = modified_url + modified_picture
    
    #Add the featured image to all_content dictionary
    all_content["featured_image"] = new_url
    
    #Scrape the weather on mars
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    response = requests.get(twitter_url)
    time.sleep(1)
    twitter_soup = BeautifulSoup(response.text, 'html.parser')
    timeline = twitter_soup.select('#timeline li.stream-item')
    
    all_tweets = []
    for tweet in timeline:
        #tweet_id = timeline['data-item-id']
        tweet_text = tweet.select('p.tweet-text')[0].get_text()
        all_tweets.append({"text": tweet_text})

    mars_weather = all_tweets[0]
    all_content["weather"] = mars_weather
    
    #Mars facts scrape
    fact_url = 'https://space-facts.com/mars/'
    facts_tables = pd.read_html(fact_url)
    facts_df = facts_tables[0]
    facts_df.columns = ['Description', 'Value']
    facts_df.set_index('Description', inplace=True)
    
    facts_data = facts_df.to_html()
    facts_data = facts_data.replace('\n', '')
    
    all_content["facts"] = facts_data
    
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    hemisphere_html = browser.html
    hemisphere_soup = BeautifulSoup(hemisphere_html, 'html.parser')    
    
    hemisphere_image_urls = []
    items = hemisphere_soup.find_all('div', class_='item')

    hemispheres_main_url = 'https://astrogeology.usgs.gov' 

    # Loop through the items previously stored
    for i in items: 
        
        title = i.find('h3').text
        partial_img_url = i.find('a', class_='itemLink product-item')['href']
        
        # Visit the link that contains the full image website 
        browser.visit(hemispheres_main_url + partial_img_url)
        
        # HTML Object of individual hemisphere information website 
        partial_img_html = browser.html
        
        # Parse HTML with Beautiful Soup for every individual hemisphere information  
        soup = BeautifulSoup( partial_img_html, 'html.parser')
            
        # Retrieve full image source 
        img_url = hemispheres_main_url + soup.find('img', class_='wide-image')['src']
            
        # Append the retreived information into a list of dictionaries 
        hemisphere_image_urls.append({"title":title,"img_url":img_url})
    
    all_content['hemisphere_image_urls'] = hemisphere_image_urls
    
    return all_content

    browser.quit()
