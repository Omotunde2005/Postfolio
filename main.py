import uvicorn
import urllib
import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

