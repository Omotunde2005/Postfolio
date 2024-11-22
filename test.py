# Testing using requests.

import requests
import functions
import jwt
import settings
from bs4 import BeautifulSoup
from datetime import timedelta, datetime, timezone, date
from pydantic import BaseModel
from schema import NewPostSchema


url = "http://localhost:8000/get/user/boards"
board_url = "http://localhost:8000/get/portfolio/670c4dc1b9a1c6bc0e953bca"
delete_url = "http://localhost:8000/delete/boards"
NEW_URL = "http://localhost:8000/"
login_url = "http://localhost:8000/login"


access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzBjNDczYTVmM2ZiMDFjZTI0NGMxY2YiLCJleHAiOjE3MzExMTE0MDN9.oLv46-2QFhD-ZSzq-jnwuKHccd5mpSihgyY7yZerHTI'
refresh_token = '' 

header = {
    "Authorization": f"Bearer {access_token}",
#    "token": f"{refresh_token}"
}

post_data = {
    "username": "emiloju_one",
    "email": "edunrilwan@gmail.com",
    "password": "123456789"
}

update_data = {
    "username": "dboy"
}

login_data = {
    "username": "edunrilwan@gmail.com",
    "password": "123456789"
}

BOARD_DATA = {
    "board_url": "emiloju",
    "title": "My 30 DAYS OF BUILDING ONLINE",
    "description": "Sharing my journey online",
    "social_app": "LinkedIn",
    "cta": "Hire me",
    "cta_url": "https://hireme/com"
}

UPDATE_BOARD_DATA = {
    "title": "30 DAYS"
}

response = requests.post(login_url, data=login_data)
print(response.json())


"""
{'message': 'Login successful', 
'token': {
    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzBjNDczYTVmM2ZiMDFjZTI0NGMxY2YiLCJleHAiOjE3MzExOTU0ODd9.orVNjIsWnZ6a4S6_7CmDFnEMiIooJZdB9sU1m3NAqcQ', 
    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzBjNDczYTVmM2ZiMDFjZTI0NGMxY2YiLCJleHAiOjE3MzE3OTcyODd9.u5rZ8nFM69kz3-clnljPsV9HKGHB2Z4n7O5Y8jqjUEA', 
    'token_type': 'Bearer'}}
"""

"""
{'message': 'Board created successfully', 
'board': '{
    "_id":"670c4dc1b9a1c6bc0e953bca",
    "user_Id":"670c473a5f3fb01ce244c1cf",
    "board_url":"emiloju",
    "title":"My 30 DAYS OF BUILDING ONLINE",
    "description":"Sharing my journey online",
    "social_app":"LinkedIn",
    "cta":"Hire me",
    "cta_url":"https://hireme/com",
    "is_published":false,
    "theme":{},
    "posts":[],
    "created_At":"2024-10-13T23:45:47.828000",
    "last_updated":null}'}
"""