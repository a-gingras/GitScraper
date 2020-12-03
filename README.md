# GitScrapper

This is a script that looks through various React Native projects on Github to see which props are the most used. 

## Installation
Install the following python libraries:
- BeautifulSoup
- PyGithub

Make a file called `tokens.json` in the following format with your Github tokens:
```json
{
    "tokens": [
        "token1",
        "token2"
        ...
    ]
}
```
It's highly recommended to get multiple tokens because Github's rate limit is very low and this will run very slowly and error out often with only one token. 

~~To get more tokens you can ask your friends for theirs :).~~

## Run

Run the following where <COMPONENT> is the name of the component you want to look at:
```bash
python3 scrapper.py <COMPONENT> new
```
Running the script will go through up to 100 repos. Run without "new" to continue where it left off and look are more repos. 

## Troubleshooting
If the script stops with an `"API rate limit exceeded for user ID ___."` error just wait a minute and run again without "new" to continue.

## Getting Results
Go to `output/` to get a json file with the results.
