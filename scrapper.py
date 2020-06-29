# Imports
from bs4 import BeautifulSoup
import requests
import re
import time
import json
import operator

# Global for all found repo urls
repo_urls = []
# Github base url
base_url = 'https://github.com'

COMPONENT_NAME = 'ScrollView'

props_list = [
'alwaysBounceHorizontal',
'alwaysBounceVertical',
'automaticallyAdjustContentInsets',
'bounces',
'bouncesZoom',
'canCancelContentTouches',
'centerContent',
'contentContainerStyle',
'contentInset',
'contentInsetAdjustmentBehavior',
'contentOffset',
'decelerationRate',
'directionalLockEnabled',
'disableIntervalMomentum',
'disableScrollViewPanResponder',
'endFillColor',
'horizontal',
'indicatorStyle',
'invertStickyHeaders',
'keyboardDismissMode',
'keyboardShouldPersistTaps',
'maintainVisibleContentPosition',
'maximumZoomScale',
'minimumZoomScale',
'nestedScrollEnabled',
'onContentSizeChange',
'onMomentumScrollBegin',
'onMomentumScrollEnd',
'onScroll',
'onScrollBeginDrag',
'onScrollEndDrag',
'onScrollToTop',
'overScrollMode',
'pagingEnabled',
'persistentScrollbar',
'pinchGestureEnabled',
'refreshControl',
'removeClippedSubviews',
'scrollBarThumbImage',
'scrollEnabled',
'scrollEventThrottle',
'scrollIndicatorInsets',
'scrollPerfTag',
'scrollToOverflowEnabled',
'scrollsToTop',
'showsHorizontalScrollIndicator',
'showsVerticalScrollIndicator',
'snapToAlignment',
'snapToEnd',
'snapToInterval',
'snapToOffsets',
'snapToStart',
'stickyHeaderIndices',
'zoomScale'
]

def get_repos(link):
    page_response = requests.get(link, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")

    for link in page_content.find_all('a', attrs={'data-hovercard-type': 'repository'}):
        if link.get('href') not in old_repos:
            repo_urls.append(link.get('href'))
            print(link.get('href'))

    next_button = page_content.find('a', string='Next')
    if next_button and len(repo_urls) < 100: # keep going until 100 new repos are found
        time.sleep(1)
        get_repos(next_button.get('href'))

def get_files(url):
    time.sleep(2)
    page_response = requests.get(url, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    for file_name in page_content.find_all('a', string=re.compile('.*\.(tsx)|.*\.(js)$')):
        file_urls.append(file_name.get('href'))
    next_button = page_content.find('a', string='Next')
    if next_button:
        get_files(base_url + next_button.get('href'))   

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

# get all substring props
substring_props = []
for p in props_list:
    for pp in props_list:
        if p in pp and p != pp:
            substring_props.append(p)  
print(substring_props)    

# make new props object
# props = {}
# for p in props_list:
#     props[p] = 0

# get previously stored data
with open('data.json') as json_file:
    props = json.load(json_file)

# get list of repos that have already been looked at
with open('repos.txt', 'r') as f:
    old_repos = f.readlines()
    old_repos = [r[:-1] for r in old_repos]

page_link = 'https://github.com/react-native-community/react-native-video/network/dependents?package_id=UGFja2FnZS0xNDgwNzUwNw%3D%3D'
get_repos(page_link) 

for url in repo_urls:
    file_urls = []
    print('\nREPO: ', url)
    # search repo for files containing 'video'
    get_files(base_url + url + '/search?q=' + COMPONENT_NAME)
    for file_name in file_urls:
        print('JS/TSX FILE:', file_name)
        time.sleep(1)
        page_response = requests.get(base_url + file_name , timeout=5)
        page_content = BeautifulSoup(page_response.content, "html.parser")
        code_body = page_content.find_all('table')
        if code_body and ('<' + COMPONENT_NAME) in code_body[0].text:
            parse_js_code(code_body[0].text)
            a_file = open("data.json", "w")
            json.dump(props, a_file)
            a_file.close()
    with open("repos.txt", "a") as myfile:
        myfile.write(url + "\n")

# sort data and print
sorted_props = sorted(props.items(), key=operator.itemgetter(1), reverse=True)
props = dict(sorted_props)
print(props)
