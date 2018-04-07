from urllib.parse import urlencode
from urllib.request import urlopen
import json

from datetime import datetime
from time import sleep

import numpy as np
import pandas as pd

NYT_ARTICLE_API_URL = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'

def get_replies(df):
    if 'replyCount' in df.columns:
        selected_df = df.loc[df.replyCount>0]
        if selected_df.shape[0] > 0:
            df_list = []
            for idx, row in selected_df.iterrows():
                replies_df = pd.DataFrame(row.replies)
                replies_df['inReplyTo'] = row.commentID
                df_list.append(replies_df)
            all_replies_df = pd.concat([replies_df for replies_df in df_list])
            all_replies_df = get_replies(all_replies_df)
            df = pd.concat([df, all_replies_df])
    return df

def preprocess_comments_dataframe(df): 
    df.reset_index(inplace=True, drop=True)
    df.drop(['replies'], inplace=True, axis=1)
    # Specify dtypes:
    df.approveDate = df.approveDate.astype('int64')
    df.articleID = df.articleID.astype('category')
    df.commentID = df.commentID.astype('category')
    df.commentTitle = df.commentTitle.astype('category')
    df.commentType = df.commentType.astype('category')
    df.createDate = df.createDate.astype('int64')
    df.inReplyTo = df.inReplyTo.fillna(0).astype('int32')
    df.newDesk = df.newDesk.astype('category')
    df.parentID = df.parentID.fillna(0).astype('category')
    df.parentUserDisplayName = df.parentUserDisplayName.astype('category')
    df.permID = df.permID.astype('category')
    df.picURL = df.picURL.astype('category')
    df.printPage = df.printPage.astype('int32')
    df.recommendations = df.recommendations.astype('int64')
    df.recommendedFlag  = df.recommendedFlag.astype('category')
    df.replyCount = df.replyCount.astype('int32')
    df.reportAbuseFlag = df.reportAbuseFlag.astype('category')
    df.sectionName = df.sectionName.astype('category')
    df.sharing = df.sharing.astype('category').cat.codes
    df.status = df.status.astype('category')
    df.timespeople = df.timespeople.astype('category').cat.codes
    df.trusted = df.trusted.astype('category').cat.codes
    df.updateDate = df.updateDate.astype('int64')
    df.userDisplayName = df.userDisplayName.astype('category')
    df.userID = df.userID.astype('category')#.cat.codes
    df.userLocation = df.userLocation.astype('category')
    df.userTitle = df.userTitle.astype('category')
    df.userURL = df.userURL.astype('category')
    return df

def preprocess_articles_dataframe(df): 
    df.reset_index(inplace=True, drop=True)
    df.drop(['blog', 'score', 'uri'], axis=1, inplace=True)
    df = df.rename(columns = {'_id': 'articleID', 'document_type': 'documentType', 
                'new_desk': 'newDesk', 'print_page': 'printPage', 'pub_date': 'pubDate', 
                'section_name': 'sectionName', 'type_of_material': 'typeOfMaterial', 
                'web_url': 'webURL', 'word_count': 'articleWordCount'}) 
    df.printPage.fillna(0, inplace=True)
    if 'sectionName' in df.columns:
        df.sectionName.fillna('Unknown', inplace=True)
    else: df['sectionName'] = 'Unknown'
    
    df.loc[~df.byline.isnull(), 'byline'] = df.loc[~df.byline.isnull(), 
                            'byline'].apply(lambda x: x['original']).fillna('By UNKNOWN')
    df.loc[df.byline.isnull(), 'byline'] = 'By UNKNOWN'   
    df.headline = df.headline.apply(lambda x: x['print_headline']).fillna('Unknown').replace('', 'Unknown')
    df.keywords = df.keywords.apply(lambda keywords: [keyword['value'] for keyword in keywords])
    df.multimedia = np.where(df.multimedia, 1, 0)
    df.pub_date = pd.to_datetime(df.pubDate, errors='coerce')
    
    # Specify dtypes:
    df.articleID = df.articleID.astype('category')
    df.byline = df.byline.astype('category')
    df.documentType = df.documentType.astype('category')
    df.newDesk = df.newDesk.astype('category')
    df.printPage = df.printPage.astype('int32')
    df.sectionName = df.sectionName.astype('category')
    df.source = df.source.astype('category')
    df.typeOfMaterial = df.typeOfMaterial.astype('category')
    df.webURL = df.webURL.astype('category')
    return df
    
def get_comments(article_url):
    '''Given the url of an articles from NYT, returns the list of comments in that article'''
    
    article_url = article_url.replace(':','%253A') #convert the : to an HTML entity
    article_url = article_url.replace('/','%252F')
    
    offset = 0 #Start off at the very beginning
    total_comments = 0 # Initialize the count of comments in the article 
    df_list = []
    comments_df = pd.DataFrame() # Set up a list to store the comments' data 

    while True:
        sleep(1) 
        url='http://www.nytimes.com/svc/community/V3/requestHandler?callback=NYTD.commentsInstance.drawComments&method=get&cmd=GetCommentsAll&url='+article_url+'&offset='+str(offset)+'&sort=newest' 
        file = urlopen(url).read().decode() # Get the comments data and read it into a string
        file=file.replace('NYTD.commentsInstance.drawComments(','')
        file=file.replace('      /**/ ','')  
        file=file[:-2] 
        js = json.loads(file) # Load the file as json
        if js['status'] == 'OK':
            results = js['results']
            total_comments_returned = results['totalCommentsReturned']
            if total_comments_returned:
                comments = results['comments']
                df = pd.DataFrame(comments)
                df_list.append(df)
                if offset == 0:
                    total_comments = results['totalCommentsFound'] # Store the total number of comments
                    print('Found ' + str(total_comments) + ' comments')
            else:
                break
        offset = offset + 25 # Increment the counter since 25 comments are scraped each time
    if total_comments:    
        comments_df = pd.concat([df for df in df_list])
        comments_df.drop_duplicates(subset=['commentID'], inplace=True)
        comments_df['inReplyTo'] = np.nan 
        comments_df = get_replies(comments_df)
    return comments_df


def run_rounds(ARTICLE_API_KEY, page_lower=0, page_upper=10, begin_date=None, end_date=None, sort='newest', query=None, save=False):
    '''Collects the comments on the articles of NYT by first scraping the 
    articles using NYT articles search API and then calling on the customized function
    get_comments(url) on each article'''
    
    params = {'api-key': ARTICLE_API_KEY}
    
    if begin_date: # Check begin_date is not None
        params['begin_date'] = begin_date 
    elif end_date: # Check end_date is not None
        params['sort'] = 'newest'
    elif sort == 'newest':
        params['end_date'] = datetime.today().strftime('%Y%m%d')
    elif sort == 'oldest':
        params['begin_date'] = '20081030'
        
    if end_date: # Check end_date is not None
        params['end_date'] = end_date 
    elif begin_date: # Check begin_date is not None
        params['sort'] = 'oldest'
    
    if query:
        params['q'] = query
        
    params['sort'] = sort
    articles_list = []
    comments_df_list = []
    
    articles_df = pd.DataFrame()
    comments_df = pd.DataFrame()
    
    for page in range(page_lower, page_upper):
        params['page'] = page # Every page has 10 articles
        if not save:
            print("Page: ", page)
        # Using NYT API to scrap articles
        search_url = NYT_ARTICLE_API_URL + '?' + urlencode(params)
        file = urlopen(search_url).read() # Get the articles search data and read it into a string
        js = json.loads(file) # Load the articles search data as json

        if js['status'] == 'OK':
            docs = js['response']['docs']
            for i in range(10):
                if docs[i]['document_type'] != 'multimedia': # Ignore multimedia articles
                    article_url = docs[i]['web_url'] # Get the url for the article
                    comments = get_comments(article_url) # Use the article url to get comments 
                    if not comments.empty: # Check if the article has comments
                        if not save:
                            print(article_url)
                        article_id = docs[i]['_id']
                        article = docs[i]
                        articles_list.append(article)
                        comments['articleID'] = article_id
                        comments['sectionName'] = article.get('section_name', 'Unknown')
                        comments['newDesk'] = article.get('new_desk', 'Unknown')
                        comments['articleWordCount'] = article.get('word_count', 0)
                        comments['printPage'] = article.get('print_page', 0)
                        comments['typeOfMaterial'] = article.get('type_of_material', 'Unknown')
                        comments = preprocess_comments_dataframe(comments)
                        comments_df_list.append(comments)
    if comments_df_list: # Check that the list is not empty
        comments_df = pd.concat([df for df in comments_df_list])
        articles_df = pd.DataFrame(articles_list)
        articles_df = preprocess_articles_dataframe(articles_df)
    if save:
        articles_df.to_csv('Articles.csv')
        comments_df.to_csv('Comments.csv')
    else:
        print("Total articles stored: ", articles_df.shape[0])
        return articles_df, comments_df
