# nyt-comments
The package scraps comments posted on New York Times articles and returns the data as pandas dataframes (with an option to store it in ready-to-use csv files) with features engineered to be used as a dataset for data science/machine learning projects. The retrieval of the comments can be customized for a specific timeline or a search query. The package can also be used as an API wrapper for NYT article_search API to perform article search and get the results processed as a ready-to-use pandas dataframe (with an option to store it in csv files). 

The package can be used without the API key for getting comments given the url of the specific article(s). Before using, you will need to get NYT article_search API key from here. Please review the terms and condition. There is no direct daily limits for comments, to the best of knowledge but the daily limit for article search is 1000. 

### Dependencies
Python 3.4+


### Python packages
pandas

