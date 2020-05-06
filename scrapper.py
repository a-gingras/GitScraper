# Imports
from bs4 import BeautifulSoup
import requests
import re

# Global for all found repo urls
repo_urls = []

# Pagination starts at 2 for the query
page = 2

# First half of query url
first_half_url = 'https://github.com/search?o=desc&p='

# Second half of query url
second_half_url = '&q=react+native&s=updated&type=Repositories'


# Hardcoded URL for now.
# Query for react native repose that were most recenty updated.
page_link = 'https://github.com/react-native-community/react-native-video/network/dependents?package_id=UGFja2FnZS0xNDgwNzUwNw%3D%3D'

# Fetch the content from the url
page_response = requests.get(page_link, timeout=5)

# Parse content
page_content = BeautifulSoup(page_response.content, "html.parser")

for link in page_content.find_all('a'):
    reg = '^/\w+(?:-\w+)+/\w+(?:-\w+)+$'
    result = re.match(reg, link.get('href'))
    if(result):
       repo_urls.append(link.get('href'))

for link in page_content.find_all('a'):
    reg = '^/(?!topics)(?!features)\w+/\w+$'
    result = re.match(reg, link.get('href'))
    if(result):
        repo_urls.append(link.get('href'))

for link in page_content.find_all('a'):
    reg = '^/(?!topics)\w+/\w+(?:-\w+)+$'
    result = re.match(reg, link.get('href'))
    if(result):
        repo_urls.append(link.get('href'))


print(repo_urls)

# Github base url
base_url = 'https://github.com'

page_response = requests.get('https://github.com/karan-singh-07/Netflix-clone-react-native', timeout=5)
page_content = BeautifulSoup(page_response.content, "html.parser")
for code_page in page_content.find_all('a'):
    reg = '.*\.(tsx)|.*\.(js)$' # Regex for all Typescript files
    result = re.match(reg, code_page.get('href'))
    if(result):
        print(code_page.get('href'))
