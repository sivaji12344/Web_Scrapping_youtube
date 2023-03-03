from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import logging
import pymongo
import time
import pprint

from selenium import webdriver   
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.chrome.options import Options  
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

logging.basicConfig(filename="YoutubeChannelDatascrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    logging.info('Successfully Landed on Home Page')
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def Youtube_scrape():
    if request.method == 'POST':
        try:
            url = request.form['content']
            df = selenium_method(url)
            return render_template('result.html', reviews=df[0:(len(df)-1)])
        except Exception as e:
            logging.info(f'Exception Occured {e}')
            return('Exception Occured :',e)
    else:
        return render_template('index.html')
def selenium_method(url):
            s = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=s)
            driver.get(url)
            driver.maximize_window()
            time.sleep(4)
            driver.execute_script("window.scrollTo(0, 200)")
            time.sleep(2)
            thumbnails = driver.find_elements(By.XPATH, '//a[@id="thumbnail"]/yt-image/img')
            views = driver.find_elements(By.XPATH,'//div[@id="metadata-line"]/span[1]')
            titles = driver.find_elements(By.ID, "video-title")
            links = driver.find_elements(By.ID, "video-title-link")
            videos = []
            for title, view, thumb, link in zip(titles, views, thumbnails, links):
                video_dict = {
                    'title': title.text,
                    'views': view.text,
                    'thumbnail': thumb.get_attribute('src'),
                    'link': link.get_attribute('href')
                    }
                if len(videos)<=4:
                    videos.append(video_dict)
            driver.quit()
            Scrape_data = pd.DataFrame(videos)
            Scrape_data.to_csv('YTdata.csv',index=False)
            client = pymongo.MongoClient("mongodb+srv://sivajisiva49:sivajisiva49@cluster0.6hyzjnn.mongodb.net/?retryWrites=true&w=majority")
            db = client['youtube_scrap']
            review_col = db['review_scrap_data']
            review_col.insert_many(videos)
            return videos
if __name__=="__main__":
    app.run(host = '0.0.0.0', port=8000, debug=True)
