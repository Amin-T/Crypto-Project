# Import libraries
import pandas as pd
import numpy as np
import datetime
import time
import requests
import json
import re


class RedditAPI:

    def __init__(self, Client_ID, Secret_Token, Username, Password, User_Agent):
        """
        Reddit reauires OAuth to authenticate use on applications. for more info please refer to:
        https://github.com/reddit-archive/reddit/wiki/OAuth2

        Client_ID: personal use script
        Secret_Token: secret authentication tocken
        Username: personal reddit username
        Password: reddit account password
        User_Agent: app name and version
        """

        self.CLIENT_ID = Client_ID
        self.SECRET_TOKEN = Secret_Token
        self.username = Username
        self.User_Agent = User_Agent
        self.password = Password

    def connect(self):
        """
        Acquire Authorization token to make requests to reddit's API.
        """

        auth = requests.auth.HTTPBasicAuth(self.CLIENT_ID, self.SECRET_TOKEN)

        # Here the login method is passed
        data = {'grant_type': 'password',
                'username': self.username,
                'password': self.password}

        # Setup header info
        headers = {'User-Agent': self.User_Agent}

        # Send request for an OAuth token
        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=headers)
        self.GetResponse = res

        if res.status_code == 200:
            try:
                TOKEN = res.json()['access_token']
            except:
                print('An error occured:\n')
                print(f"Error: {res.json().get('error')}, Message: {res.json().get('message')}")

            # Add authorization tocken to our headers dictionary
            self.headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

            print('Connection successful.')

        else:
            print('An error occured:\n')
            print(f"Error: {res.json().get('error')}, Message: {res.json().get('message')}")


    def make_request(self, url, headers=None, params=None, max_retries = 3):
        def fire_away(url, headers, params):
            response = requests.get(url, headers=headers, params=params)
            assert response.status_code == 200
            return json.loads(response.content)
        current_tries = 1
        while current_tries < max_retries:
            try:
                time.sleep(1)
                response = fire_away(url, headers, params)
                return response
            except:
                time.sleep(1)
                current_tries += 1
        return fire_away(url, headers, params)

    def search(self, query, limit=100):
        """
        Search and return subreddits containing the 'query'.
        """
        get_url = 'https://oauth.reddit.com/subreddits/search'
        params = {'q': str(query), 'limit': 100}
        subreddits_df = pd.DataFrame()
        retrieved_cnt = 0

        while retrieved_cnt < limit:
            try:
                subreddits = self.make_request(url=get_url, headers=self.headers, params=params)
                temp_df = pd.DataFrame([x['data'] for x in subreddits['data']['children']])
                subreddits_df = pd.concat([subreddits_df, temp_df])
                params['after'] = subreddits['data']['after']
                retrieved_cnt = subreddits_df.shape[0]

                if params['after'] is None:
                    break
            except:
                break

        def timestamp_date(timestamp):    
            output = datetime.datetime.fromtimestamp(timestamp)
            return output

        subreddits_df['created_utc'] = subreddits_df['created_utc'].apply(timestamp_date)
        subreddits_df.reset_index(drop=True, inplace=True)

        return subreddits_df

    def GetSubmissions(self, subreddit, size=100, start=None, end=None):
        """
        Rretrieve the most recent threads (submissions) for a subreddit
        """
        get_url = f'https://oauth.reddit.com/r/{subreddit}/new'
        params = {'limit': 100}
        submissions_df = pd.DataFrame()
        retrieved_cnt = 0

        while retrieved_cnt < size:
            try:
                submissions = self.make_request(get_url, headers=self.headers, params=params)
                temp_df = pd.DataFrame([x['data'] for x in submissions['data']['children']])
                submissions_df = pd.concat([submissions_df, temp_df])
                params['after'] = submissions['data']['after']
                retrieved_cnt = submissions_df.shape[0]

                if params['after'] is None:
                    break

            except:
                break

        timestamp_date =  lambda ts: datetime.datetime.fromtimestamp(ts)

        submissions_df['created_utc'] = submissions_df['created_utc'].apply(timestamp_date)
        submissions_df.reset_index(drop=True, inplace=True)
        return submissions_df