nyt-comments
******************************

The package includes three main functions to perform three distinct tasks involving the retrieval of comments' and articles' from New York Times as ready-to-use dataset for data science/machine learning projects:

1. The main function ``get_dataset`` returns two dataframes - one each for the articles and the comments on them. The retrieval can be customized based on a number of optional parameters such as a specific timeline for the articles, search keywords, filter queries based on a number of options such as the week of the day, the word count of the articles, source, etc., maximum limit on the number of comments or articles or both, sorting the articles chronologically based on either the newest or oldest articles, option to suppress or activate the output log for the process, option to save the data as two `csv` files, etc. The function returns only the articles that were open to comments along with the comments on them.   

2. The function ``get_articles`` can be used as an API wrapper for NYT article search API. It returns the cleaned up and preprocessed data for articles as a ready-to-use pandas dataframe (with an option to store it in ``csv`` files). The retrieval can be customized with the same options as above and unlike the above function, it returns all the articles that satisfy the search criteria.

3. The function ``get_comments`` retrieves the comments on NYT article(s) given their urls. It can be used as a substitute for the comments by url option in the NYT Community API that is now deprecated and only return comments that were picked as editor's selection on account of an `unresolved issue <https://github.com/NYTimes/public_api_specs/issues/29>`_. This function does not use NYT API for the retrieval unlike the above two.

Dependencies
------------
* Python 3.4+
* pandas 
* requests

Usage
-------
.. code:: python

  from nytcomments import get_dataset
  articles_df, comments_df = get_dataset(ARTICLE_API_KEY, page_lower=0, page_upper=2)

Please refer to the `tutorial here <https://github.com/AashitaK/nyt-comments/blob/master/Tutorial.ipynb>`_ for illustration of the three functions ``get_dataset``, ``get_comments`` and ``get_articles`` as well as detailed information about the function arguments. The functions ``get_dataset`` and ``get_articles`` requires the use of NYT API key that can be obtained by registering at the `NYT developers' site <http://developer.nytimes.com/signup>`_ whereas ``get_comments`` can be used without the API key. You must agree to the `Terms of Use <http://developer.nytimes.com/tou>`_ for the NYT article search API to use the key.

Note : The dataset of comments posted on NYT articles in the period Jan-April 2017 and Jan-April 2018 is availabl on `_featured on Kaggle<https://www.kaggle.com/aashita/nyt-comments>`_.

Acknowledgement
---------------
* The url used to retrieve comments from a given article in the function ``get_comments`` is taken from the `blog by Neal Caren <http://nealcaren.web.unc.edu/scraping-comments-from-the-new-york-times/>`_.
* NYT article search API is used for the article search.



