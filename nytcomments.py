from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError
import sys
import json

from time import sleep
from datetime import datetime

import pandas as pd
        
NYT_ARTICLE_API_URL = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
COMMENTS_URL = 'http://www.nytimes.com/svc/community/V3/requestHandler?callback=NYTD.commentsInstance.drawComments&method=&cmd=GetCommentsAll&url='


def get_dataset(ARTICLE_API_KEY, page_lower=0, page_upper=30, begin_date=None, end_date=None, 
                 max_comments=50000, sort='newest', query=None, save=False, printout=True):
    '''Collects the comments on the articles of NYT by first scraping the 
    articles using NYT articles search API, calling on the customized function
    get_comments(url) to get comments on each article, processing the comments' 
    and articles' data and returning two pandas dataframes - one each for articles 
    and comments.'''
    
    params = {'api-key': ARTICLE_API_KEY}
    
    if page_lower<0:
        page_lower = 0
        print('Out of range value passed for page_lower. The page_lower parameter is set to 0')
        print()
    
    if page_upper>200:
        page_upper = 200
        print('Out of range value passed for page_upper. The page_upper parameter is set to 199.')
        print()
        
    if (sort!='newest') & (sort!='oldest'):
        print('Invalid value passed for sort. The sort parameter is set to newest.')
        print()
    
    if sort=='oldest':
        if begin_date is None:
            begin_date = '20081031'   
    elif end_date is None:
        end_date = datetime.today().strftime('%Y%m%d')
        
    if begin_date: # Check begin_date is not None
        try:
            begin_date = pd.to_datetime(begin_date, errors='coerce').strftime('%Y%m%d')
        except:
            print("Error: Please try again with begin_date entered in the format %Y%m%d.")
        params['begin_date'] = begin_date 

    if end_date: # Check end_date is not None
        try:
            end_date = pd.to_datetime(end_date, errors='coerce').strftime('%Y%m%d')
        except:
            print("Error: Please try again with end_date entered in the format %Y%m%d.")
        params['end_date'] = end_date

    if query:
        params['q'] = query

    params['sort'] = sort
    
    articles_list = []
    comments_df_list = []

    articles_df = pd.DataFrame()
    comments_df = pd.DataFrame()
    
    total_comments = 0
    
    HTTPErrorCount = 0
    
    for page in range(page_lower, page_upper):
        if total_comments < max_comments:
            params['page'] = page # Every page has 10 articles
            if printout:
                print("Page: ", page)
            try:
                # Using NYT API to scrap articles
                search_url = NYT_ARTICLE_API_URL + '?' + urlencode(params)
                file = urlopen(search_url).read() # Get the articles search data and read it into a string
                js = json.loads(file) # Load the articles search data as json

                if js['status'] == 'OK':
                    docs = js['response']['docs']
                    docs_length = len(docs)
                    if docs_length==0:
                        if printout:
                            print("No aricles found on page", page)
                        break
                    for i in range(docs_length):
                        if docs[i]['document_type'] != 'multimedia': # Ignore multimedia articles
                            article_url = docs[i]['web_url'] # Get the url for the article
                            # Use the article url to get comments 
                            comments, number_comments, error = get_comments(article_url, returnError=True) 
                            total_comments += number_comments
                            if not comments.empty: # Check if the article has comments
                                if printout:
                                    print("Article url:", article_url)
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
                            if error:
                                break
                    if error:
                        break
            except KeyboardInterrupt:
                if printout:
                    print('KeyboardInterrupt: Retrieval interrupted.')
                break
            except ConnectionError:
                if printout:
                    print('ConnectionError: Retrieval interrupted.')
                break
            except SystemExit:
                if printout:
                    print('SystemExit: Retrieval interrupted.')
                break
            except HTTPError:
                HTTPErrorCount += 1
                if HTTPErrorCount < 5:
                    if printout:
                        print(sys.exc_info()[1], "Page {} is skipped. Retrival is continued from the next page.".format(page))
                        print()
                    pass
                else:
                    if printout:
                        print(sys.exc_info()[1], "Retrival is terminated due to repeated HTTP errors.")
                        print()
                    break
            except:
                if printout:
                    print("Unexpected error:", sys.exc_info()[1])
                    print("Page {} is skipped. Retrival is continued from the next page.".format(page))
                    print()
                pass
                            
    if comments_df_list: # Check that the list is not empty
        comments_df = pd.concat([df for df in comments_df_list])
        articles_df = pd.DataFrame(articles_list)
        articles_df = preprocess_articles_dataframe(articles_df)
        
    if printout:
        if page_lower > page_upper:
            print("page_lower value is greater than the page_upper. No articles returned.")
        elif (begin_date is not None) & (end_date is not None):
            if begin_date>end_date:
                print("begin_date is bigger than the end_date. No articles returned.")
            else:
                print()
                print("Total articles stored: ", articles_df.shape[0])
                print("Total comments retrieved: ", comments_df.shape[0])
        else:
            print()
            print("Total articles stored: ", articles_df.shape[0])
            print("Total comments retrieved: ", comments_df.shape[0])
    if save:
        articles_df.to_csv('Articles.csv', index=False)
        comments_df.to_csv('Comments.csv', index=False)
    return articles_df, comments_df
 
    
def get_comments(article_url, save=False, printout=True, returnError=False):
    '''Given the url of an articles from NYT, returns a dataframe of comments in that article'''
    
    url = article_url.replace(':','%253A') #convert the : to an HTML entity
    url = url.replace('/','%252F')
    
    offset = 0 #Start off at the very beginning
    total_comments = 0 # Initialize the count of comments in the article 
    df_list = []
    comments_df = pd.DataFrame() # Set up a list to store the comments' data 
    error = None
    while True:
        try:
            sleep(1) 
            url = COMMENTS_URL + url + '&offset=' + str(offset) + '&sort=newest' 
            file = urlopen(url).read().decode() # Get the comments data and read it into a string
            file = file.replace('NYTD.commentsInstance.drawComments(','')
            file = file.replace('      /**/ ','')  
            file = file[:-2] 
            js = json.loads(file) # Load the file as json
            if js['status'] == 'OK':
                results = js['results']
                total_comments_returned = results['totalCommentsReturned']
                total_comments += total_comments_returned # Store the total number of comments
                if total_comments_returned:
                    comments = results['comments']
                    df = pd.DataFrame(comments)
                    df_list.append(df)
                else:
                    break # Break when no comments are returned
            offset = offset + 25 # Increment the counter since 25 comments are scraped each time
        except KeyboardInterrupt:
            if returnError:
                error = True
            if printout:
                print('KeyboardInterrupt: Retrieval interrupted.')
            break
        except ConnectionError:
            if returnError:
                error = True
            if printout:
                print('ConnectionError: Retrieval interrupted.')
            break
        except SystemExit:
            if returnError:
                error = True
            if printout:
                print('SystemExit: Retrieval interrupted.')
            break
        except HTTPError:
            if printout:
                print(sys.exc_info()[1], "Article with the URL {} is skipped. Retrival is continued from the next article.".format(article_url))
                print()
            break    
        except:
            if printout:
                print("Unexpected error:", sys.exc_info()[1])
                if returnError:
                    print("Article with the URL {} is skipped. Retrival is continued from the next article.".format(article_url))
                    print()
            break
        
    if total_comments:
        if printout:
            print('Retrieved ' + str(total_comments) + ' comments')
        comments_df = pd.concat([df for df in df_list])
        comments_df.drop_duplicates(subset=['commentID'], inplace=True)
        comments_df['inReplyTo'] = None 
        comments_df = get_replies(comments_df)
    if save:
        comments_df.to_csv('Comments.csv', index=False)
    if returnError:
        return comments_df, total_comments, error
    else:
        return comments_df, total_comments

def get_articles(ARTICLE_API_KEY, page_lower=0, page_upper=50, begin_date=None, end_date=None, 
                 max_articles=100000, sort='newest', query=None, save=False, printout=True):
    '''Collects the data on the articles of NYT using NYT articles search API, processes the 
    articles' data and returns a pandas dataframe for articles.'''
    
    params = {'api-key': ARTICLE_API_KEY}
    
    if page_lower<0:
        page_lower = 0
    
    if page_upper>=200:
        page_upper = 199
    
    if sort=='oldest':
        if begin_date is None:
            begin_date = '20081030'   
    elif end_date is None:
        end_date = datetime.today().strftime('%Y%m%d')
        
    if begin_date: # Check begin_date is not None
        try:
            begin_date = pd.to_datetime(begin_date, errors='coerce').strftime('%Y%m%d')
        except:
            print("Error: Please try again with begin_date entered in the format %Y%m%d.")
        params['begin_date'] = begin_date 

    if end_date: # Check end_date is not None
        try:
            end_date = pd.to_datetime(end_date, errors='coerce').strftime('%Y%m%d')
        except:
            print("Error: Please try again with end_date entered in the format %Y%m%d.")
        params['end_date'] = end_date

    if query:
        params['q'] = query

    params['sort'] = sort
    
    articles_list = []
    articles_df = pd.DataFrame()
    
    total_articles = 0
    
    for page in range(page_lower, page_upper):
        if total_articles < max_articles:
            try: 
                sleep(1)

                params['page'] = page # Every page has 10 articles
                if printout:
                    print("Page: ", page)

                # Using NYT API to scrap articles
                search_url = NYT_ARTICLE_API_URL + '?' + urlencode(params)
                file = urlopen(search_url).read() # Get the articles search data and read it into a string
                js = json.loads(file) # Load the articles search data as json

                if js['status'] == 'OK':
                    docs = js['response']['docs']
                    docs_length = len(docs)
                    if docs_length==0:
                        if printout:
                            print("No articles found on page", page)
                        break
                    for i in range(docs_length):
                        article = docs[i]
                        articles_list.append(article)
                        if printout:
                            article_url = article['web_url'] # Get the url for the article
                            print("Article url:", article_url)
            except KeyboardInterrupt:
                if printout:
                    print('KeyboardInterrupt: Retrieval interrupted.')
                break
            
            except ConnectionError:
                if printout:
                    print('ConnectionError: Retrieval interrupted.')
                break
            except SystemExit:
                if printout:
                    print('SystemExit: Retrieval interrupted.')
                break
            except:
                if printout:
                    print("Unexpected error:", sys.exc_info()[0])
                    print("Page {} is skipped. Retrival is continued from the next page.".format(page))
                    print()
                pass
                           
    articles_df = pd.DataFrame(articles_list)
    articles_df = preprocess_articles_dataframe(articles_df)
        
    if printout:
        if page_lower > page_upper:
            print("page_lower value is greater than the page_upper. No articles returned.")
        elif (begin_date is not None) & (end_date is not None):
            if begin_date>end_date:
                print("begin_date is bigger than the end_date. No articles returned.")
            else:
                print()
                print("Total articles stored: ", articles_df.shape[0])
        else:
            print()
            print("Total articles stored: ", articles_df.shape[0])
    if save:
        articles_df.to_csv('Articles.csv', index=False)
    return articles_df


def get_replies(df):
    '''Extracts the replies to the comments and returns the dataframe
    including the replies as comments'''
    
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
    '''Preprocesses the comments' dataframe'''
    
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
    '''Preprocesses the articles' dataframe'''
    df.reset_index(inplace=True, drop=True)
    df.drop(['blog', 'score', 'uri'], axis=1, inplace=True)
    df = df.rename(columns = {'_id': 'articleID', 'document_type': 'documentType', 
                'new_desk': 'newDesk', 'print_page': 'printPage', 'pub_date': 'pubDate', 
                'section_name': 'sectionName', 'type_of_material': 'typeOfMaterial', 
                'web_url': 'webURL', 'word_count': 'articleWordCount'}) 
    
    if 'printPage' in df.columns:
        df.printPage.fillna(0, inplace=True)
    else: 
        df['printPage'] = 0
        
    if 'sectionName' in df.columns:
        df.sectionName.fillna('Unknown', inplace=True)
    else: 
        df['sectionName'] = 'Unknown'
        
    if 'newDesk' in df.columns:
        df.newDesk.fillna('Unknown', inplace=True)
    else: 
        df['newDesk'] = 'Unknown'
        
    if 'typeOfMaterial' in df.columns:
        df.typeOfMaterial.fillna('Unknown', inplace=True)
    else: 
        df['typeOfMaterial'] = 'Unknown'
    
    if 'byline' in df.columns:
        df.loc[~df.byline.isnull(), 'byline'] = df.loc[~df.byline.isnull(), 
                                'byline'].apply(lambda x: x['original']).fillna('By UNKNOWN')
        df.loc[df.byline.isnull(), 'byline'] = 'By UNKNOWN'  
    else:
        df['byline'] = 'By UNKNOWN'  
    
    if 'headline' in df.columns:
        df.headline = df.headline.apply(lambda x: x['print_headline']).fillna('Unknown').replace('', 'Unknown')
    else:
        df['headline'] = 'Unknown'
        
    df.keywords = df.keywords.apply(lambda keywords: [keyword['value'] for keyword in keywords])
    
    if 'multimedia' in df.columns:
        df.multimedia = df.multimedia.apply(lambda x: len(x))
    else:
        df['multimedia'] = 0
        
    if 'pubDate' in df.columns:
        df.pubDate = pd.to_datetime(df.pubDate, errors='coerce')
    
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
    



