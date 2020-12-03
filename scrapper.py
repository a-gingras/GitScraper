# Imports
from bs4 import BeautifulSoup
import requests
import re
import time
import json
import operator
import sys
from github import Github

COMPONENT_NAME = sys.argv[1]

token_idx = 0
with open("tokens.json") as json_file:
    tokens = json.load(json_file)["tokens"]

g = Github(tokens[token_idx])
repo_urls = []
props_list = []

base_url = 'https://github.com'
data_filename = "output/" + COMPONENT_NAME + ".json"
repos_filename = "output/stuff/" + COMPONENT_NAME + "Repos.txt"


def get_props_list():
    props = []
    docs_url = "https://reactnative.dev/docs/0.60/" + COMPONENT_NAME.lower()
    docs_page_response = requests.get(docs_url, timeout=5)
    docs_page_content = BeautifulSoup(docs_page_response.content, "html.parser")

    props_a =  docs_page_content.find('a', text="Props")
    for child in props_a.next_sibling:
        prop_a = child.find('a')
        if "DEPRECATED" not in prop_a.text:
            props.append(prop_a.text)
            print(prop_a.text)
    return props

def get_repos(link):
    page_response = requests.get(link, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")

    for link in page_content.find_all('a', attrs={'data-hovercard-type': 'repository'}):
        if link.get('href') not in old_repos:
            repo_urls.append(link.get('href'))
            print(link.get('href'))

    next_button = page_content.find('a', string='Next')
    if next_button and len(repo_urls) < 100: # keep going until 100 new repos are found
        get_repos(next_button.get('href'))

def get_files(repo_name): 
    files = []
    query_js = "repo:" + repo_name[1:] + " " + COMPONENT_NAME + " extension:js"
    results_js = g.search_code(query_js, order='desc')
    query_tsx = "repo:" + repo_name[1:] + " " + COMPONENT_NAME + " extension:tsx"
    results_tsx = g.search_code(query_tsx, order='desc')
    for result in results_js:
        files.append(result)
    for result in results_tsx:
        files.append(result)
    return files

def find_closing_bracket(start, code):
    current = start + 1
    counter = 0
    while True:
        next_ = min(code.find('<', current), code.find('>', current))
        if next_ == -1 or next_ == current:
            return len(code)
        if code[next_] == '<':
            counter = counter + 1
        elif code[next_] == '>':
            if code[next_ - 1] == '=': # ignore '=>'
                pass
            elif counter == 0:
                return next_
            else:
                counter = counter - 1   
        current = next_ + 1      

def parse_js_code(code):
    code = str(code)
    current = 0
    while code.find('<' + COMPONENT_NAME, current) != -1:
        start = code.find('<' + COMPONENT_NAME, current)
        end = find_closing_bracket(start, code)
        video_code = code[start:end] # get code in between '<COMPONENT_NAME' and '/>'
        for prop in props_list:
            props_is_there = False
            if prop in substring_props:
                if (prop + '=') in video_code:
                    props_is_there = True
            else:
                if prop in video_code:
                    props_is_there = True
            if props_is_there:
                print("  PROP:", prop)
                props[prop] = props[prop] + 1
        current = end        


props_list = get_props_list()
# get all substring props
substring_props = []
for p in props_list:
    for pp in props_list:
        if p in pp and p != pp:
            substring_props.append(p)  
print("substring props: ", substring_props)   

if len(sys.argv) > 2 and sys.argv[2] == "new":
    # make new props object
    props = {}
    for p in props_list:
        props[p] = 0
    # clear repos    
    open(repos_filename, 'w').close()
    old_repos = []    
else:
    # get previously stored data
    with open(data_filename) as json_file:
        props = json.load(json_file)

    # get list of repos that have already been looked at
    with open(repos_filename, 'r') as f:
        old_repos = f.readlines()
        old_repos = [r[:-1] for r in old_repos]    

# get list of repos that depend on react-native-video
page_link = 'https://github.com/react-native-community/react-native-video/network/dependents?package_id=UGFja2FnZS0xNDgwNzUwNw%3D%3D'
get_repos(page_link) 

for url in repo_urls:
    # check the rate limit and wait if the limit has been passed
    rate_limit = g.get_rate_limit()
    while rate_limit.search.remaining <= 5 or rate_limit.core.remaining < 400:
        token_idx = (token_idx + 1) % len(tokens)
        print("Rate limit remaining:", rate_limit.search.remaining, rate_limit.core.remaining, "token_idx:", token_idx)
        g = Github(tokens[token_idx])
        print("\nWaiting for rate limit to reset...")
        time.sleep(2)
        rate_limit = g.get_rate_limit()    

    print('\nREPO: ', url)
    # get all js/tsx files that have the component name in them
    files = get_files(url)   
    for file_ in files:
        print("File:", file_.name)
        # parse the file for props
        parse_js_code(file_.decoded_content)

    # update data.json and repos list
    a_file = open(data_filename, "w")
    json.dump(props, a_file)
    a_file.close()
    with open(repos_filename, "a") as myfile:
        myfile.write(url + "\n")


