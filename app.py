from flask import Flask, redirect, render_template, request,jsonify, url_for
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import os
import csv

app = Flask(__name__)
cors = CORS(app)


@app.route('/')
def index():

    return render_template('index.html')

@app.route('/product_reviews', methods=['POST'])
def product_reviews():
        #get input from the user
        userinput = request.form.get('user_input')


    

        response = requests.get(f"https://www.flipkart.com/search?q={userinput}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off")
        soup = BeautifulSoup(response.content,"html.parser")
        #producturlfind = soup.find('a', class_='_1fQZEK')
        try:
                producturl= "https://www.flipkart.com" + soup.find('a', class_='_1fQZEK')['href']
        except:
               return render_template('Errorpage.html')
        productrequest = requests.get(producturl)

        productmainpage = BeautifulSoup(productrequest.content,"html.parser")
       
        try:
                productreviewurl = "https://www.flipkart.com" + productmainpage.find('div', class_='col JOpGWq').a['href']
        except:
                return render_template('Errorpage.html')
        reviewpage = requests.get(productreviewurl)
        reviewpagecontent = BeautifulSoup(reviewpage.content,"html.parser")
      
        # the url for getting the overall reviews
        OverallReviewUrl = "https://www.flipkart.com" + reviewpagecontent.find('div', class_='_33iqLu').find('div').find('a')['href']
        

        overallreviews = requests.get(OverallReviewUrl)
        overallreviewscontent = BeautifulSoup(overallreviews.content,"html.parser")
        productname = overallreviewscontent.find('div', class_='_2s4DIt _1CDdy2').text 
        
        # get the reviews.
        elements = overallreviewscontent.select('div[class^="col _2wzgFH K0kLPL"]')
        
        #empty list to save the dictionary containing the reviews data
        reviews_data = [] 
       
        for element in elements:
        # Extracting the reviewer name
                PersonName = element.find('p', class_=lambda c: c and c.startswith('_2sc7ZR')).text
        # getting the rating provided
                rating = int(element.find('div', class_=lambda c: c and c.startswith('_3LWZlK')).text)
        # getting the review title
                title = element.find('p', class_=lambda c: c and c.startswith('_2-N8zT')).text.rstrip('READ MORE')
        # getting the review text
                review = element.find('div', class_=lambda c: c and c.startswith('t-ZTKy')).div.text.rstrip('READ MORE')

                review_data = {
                        "PersonName": PersonName,
                        "Rating": rating,
                        "Title": title,
                        "Review": review
                }
        
                reviews_data.append(review_data)
        #save the data to csv file
        print_to_csv(productname,reviews_data)

        return render_template('table_template.html', data=reviews_data, title=productname)

def print_to_csv(productname,reviews_data):
               #folder in which the csv file will be stored        
        data_folder = os.path.join(os.getcwd(), 'Reviews')    
        
        #columns of the csv file        
        columns = ["PersonName", "Rating", "Title", "Review"]

        file_path = os.path.join(data_folder, productname + ".csv")

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()
                for review_data in reviews_data:
                        writer.writerow(review_data)
 
if __name__ == '__main__':
    app.run(debug=True)
