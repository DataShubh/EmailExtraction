from flask import Flask, render_template, request
import re
import requests
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve the entered content from the form
        user_input = request.form.get('user_input')
        original_url = user_input 

        unscraped = deque([original_url])  

        scraped = set()  

        emails = set() 
        while len(unscraped):
            url = unscraped.popleft()  
            scraped.add(url)

            parts = urlsplit(url)
                
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            if '/' in parts.path:
                path = url[:url.rfind('/')+1]
            else:
                path = url
            try:
                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                continue
            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
            emails.update(new_emails) 

            soup = BeautifulSoup(response.text, 'lxml')
            
            for anchor in soup.find_all("a"):
                if "href" in anchor.attrs:
                    link = anchor.attrs["href"]
                else:
                    link = ''

                    if link.startswith('/'):
                        link = base_url + link
        
                    elif not link.startswith('http'):
                        link = path + link

                    if not link.endswith(".gz"):
                        if not link in unscraped and not link in scraped:
                            unscraped.append(link)

            my_dict={}
        
           for email in emails:    
                try:
                    emailObject= validate_email(email)
                    email = emailObject.email
                    my_dict[email] = "Email Address is Valild"
                except EmailNotValidError as e:
                    my_dict[email] = str(e)                
        return render_template('result.html', my_dict=my_dict)
                                
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
