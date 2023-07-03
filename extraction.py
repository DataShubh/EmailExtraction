import re
import requests
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd
from email_validator import validate_email, EmailNotValidError
original_url = input("Enter the website url: ") 

unscraped = deque([original_url])  

scraped = set()  

emails = set()  

print(unscraped)
while len(unscraped):
    url = unscraped.popleft()  
    scraped.add(url)

    parts = urlsplit(url)
        
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    if '/' in parts.path:
      path = url[:url.rfind('/')+1]
    else:
      path = url

    print("Crawling URL %s" % url)
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


print(emails)
#Checking whether email address exists or not
for email in emails:    
    try:
      emailObject= validate_email(email)
      email = emailObject.email
      print(email, "Email is Valid")
    except EmailNotValidError as e:
      print(email, "is:" ,str(e))

#df = pd.DataFrame(emails, columns=["Email"])
#df.to_csv('email.csv', index=False)

#files.download("email.csv")
