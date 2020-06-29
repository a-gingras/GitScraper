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

props_list = [
'allowsExternalPlayback',
'audioOnly',
'automaticallyWaitsToMinimizeStalling',
'bufferConfig',
'controls',
'currentPlaybackTime',
'disableFocus',
'filter',
'filterEnabled',
'fullscreen',
'fullscreenAutorotate',
'fullscreenOrientation',
'headers',
'hideShutterView',
'id',
'ignoreSilentSwitch',
'maxBitRate',
'minLoadRetryCount',
'mixWithOthers',
'muted',
'paused',
'pictureInPicture',
'playInBackground',
'playWhenInactive',
'poster',
'posterResizeMode',
'preferredForwardBufferDuration',
'progressUpdateInterval',
'rate',
'repeat',
'reportBandwidth',
'resizeMode',
'selectedAudioTrack',
'selectedTextTrack',
'selectedVideoTrack',
'source',
'stereoPan',
'textTracks',
'trackId',
'useTextureView',
'volume',
'onAudioBecomingNoisy',
'onBandwidthUpdate',
'onEnd',
'onExternalPlaybackChange',
'onFullscreenPlayerWillPresent',
'onFullscreenPlayerDidPresent',
'onFullscreenPlayerWillDismiss',
'onFullscreenPlayerDidDismiss',
'onLoad',
'onLoadStart',
'onReadyForDisplay',
'onPictureInPictureStatusChanged',
'onPlaybackRateChange',
'onProgress',
'onSeek',
'onRestoreUserInterfaceForPictureInPictureStop',
'onTimedMetadata'
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

def parse_js_code(code):
    start = code.find('<Video')
    end = code.find('/>', start)
    video_code = code[start:end] # get code in between '<Video' and '/>'
    for prop in props:
        if prop in video_code:
            print("  PROP:", prop)
            props[prop] = props[prop] + 1


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
    get_files(base_url + url + '/search?q=video')
    for file_name in file_urls:
        print('JS/TSX FILE:', file_name)
        time.sleep(1)
        page_response = requests.get(base_url + file_name , timeout=5)
        page_content = BeautifulSoup(page_response.content, "html.parser")
        code_body = page_content.find_all('table')
        if code_body and '<Video' in code_body[0].text:
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
