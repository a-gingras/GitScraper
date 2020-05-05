# Imports
from bs4 import BeautifulSoup
import requests

# Hardcoded URL for now.
# Query for react native repose that were most recenty updated.
page_link = 'https://github.com/search?o=desc&q=react+native&s=updated&type=Repositories'

# Fetch the content from the url
page_response = requests.get(page_link, timeout=5)

# Parse content
page_content = BeautifulSoup(page_response.content, "html.parser")

for link in page_content.find_all('a'):
        print(link.get('href'))
