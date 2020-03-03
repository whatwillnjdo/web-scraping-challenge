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

    news_url = "https://mars.nasa.gov/news"
    
    browser.visit(news_url)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    all_content["news_title"] = soup.find('div', class_="content_title").text
    all_content["news_synopsis"] = soup.find('div', class_='rollover_description_inner').text
    
    
    pic_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(pic_url)
    html = browser.html
    pic_soup = BeautifulSoup(html, 'html.parser')

    picture = pic_soup.find('article').find('a').get('data-fancybox-href')
    
    modified_url = pic_url.split('?')[0]
    modified_picture = picture.split('/')[2]+"/"+picture.split('/')[3]+"/"+picture.split('/')[4]
    new_url = modified_url + modified_picture
    all_content["featured_image"] = new_url
    
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

    mars_weather = all_tweets[1]
    all_content["weather"] = mars_weather
    
    #Mars facts scrape
    fact_url = 'https://space-facts.com/mars/'
    facts_tables = pd.read_html(fact_url)
    facts_df = facts_tables[0]
    facts_df.columns = ['Description', 'Value']
    facts_df.set_index('Description', inplace=True)
    
    facts_data = facts_df.to_html()
    
    all_content["facts"] = facts_df
    
    hemisphere_title_clean = []
    url_component = []
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    hemisphere_html = browser.html
    hemisphere_soup = BeautifulSoup(hemisphere_html, 'html.parser')
    all_hemispheres = hemisphere_soup.find_all('a', class_='itemLink product-item')
    hemisphere_title = hemisphere_soup.find_all('h3')
    for title in hemisphere_title:
        hemisphere_title_clean.append(title.text.strip())
    for hemisphere in all_hemispheres:
        url_component.append(hemisphere['href'])
    url_component = list( dict.fromkeys(url_component))
    
    hemisphere = hemisphere_url.split('/')[2]
    image_urls = []
    for url in url_component:
        hemisphere_url ='https://astropedia.'+hemisphere+'/download/'+url.split('/')[3]+'/'+url.split('/')[4]+'/'+url.split('/')[5]+'.tif/full.jpg'
        image_urls.append(hemisphere_url)  
            
    hemisphere_image_urls = dict(zip(hemisphere_title_clean,image_urls))        
    
    all_content['hemisphere_image_urls'] = hemisphere_image_urls
    
    return all_content
