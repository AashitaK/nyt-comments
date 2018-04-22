import pandas as pd

def get_replies(df):
    '''Extracts the replies to the comments as well as the nested 
    replies to those replies, adds all of them to the orginal dataframe
    and returns the dataframe.'''
    
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
    '''Preprocesses the comments' dataframe.'''
    
    df.reset_index(inplace=True, drop=True)
    if 'replies' in df.columns:
        df.drop(['replies'], inplace=True, axis=1)
    
    # Specify dtypes:
    df.approveDate = df.approveDate.astype('int64')
    
    if 'articleID' in df.columns:
        df.articleID = df.articleID.astype('category')
        
    if 'articleWordCount' in df.columns:
        df.articleWordCount = df.articleWordCount.fillna(0)
        
    df.commentID = df.commentID.astype('int32')
    df.commentTitle = df.commentTitle.astype('category')
    df.commentType = df.commentType.astype('category')
    df.createDate = df.createDate.astype('int64')
    df.inReplyTo = df.inReplyTo.fillna(0).astype('int32')
    
    if 'newDesk' in df.columns:
        df.newDesk = df.newDesk.fillna('Unknown').astype('category')
        
    df.parentID = df.parentID.fillna(0).astype('category')
    df.parentUserDisplayName = df.parentUserDisplayName.astype('category')
    df.permID = df.permID.astype('category')
    df.picURL = df.picURL.astype('category')
    
    if 'printPage' in df.columns:
        df.printPage = df.printPage.fillna(0).astype('int32')
        
    df.recommendations = df.recommendations.astype('int16')
    df.recommendedFlag  = df.recommendedFlag.astype('category')
    df.replyCount = df.replyCount.astype('int8')
    df.reportAbuseFlag = df.reportAbuseFlag.astype('category')
    
    if 'sectionName' in df.columns:
        df.sectionName = df.sectionName.fillna('Unknown').astype('category')
        
    df.sharing = df.sharing.astype('category').cat.codes
    df.status = df.status.astype('category')
    df.timespeople = df.timespeople.astype('category').cat.codes
    df.trusted = df.trusted.astype('category').cat.codes
    
    if 'type_of_material' in df.columns:
        df.type_of_material = df.type_of_material.fillna('Unknown').astype('category')
        
    df.updateDate = df.updateDate.astype('int64')
    df.userDisplayName = df.userDisplayName.astype('category')
    df.userID = df.userID.astype('category')#.cat.codes
    df.userLocation = df.userLocation.astype('category')
    df.userTitle = df.userTitle.astype('category')
    df.userURL = df.userURL.astype('category')
    return df


def preprocess_articles_dataframe(df): 
    '''Preprocesses the articles' dataframe.'''
    
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
