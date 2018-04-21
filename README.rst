nyt-comments
******************************

The package includes three main functions to perform three distinct tasks involving the retrieval of comments' and articles' from New York Times as ready-to-use dataset for data science/machine learning projects:

1. The main function ``get_dataset`` returns two dataframes - one each for the articles and the comments. The retrieval can be customized based on a number of parameters such as a specific timeline, search queries, etc for the articles.   

2. The function ``get_articles`` can be used as an API wrapper for NYT article search API. It returns the cleaned up and preprocessed data for articles as a ready-to-use pandas dataframe (with an option to store it in ``csv`` files). 

3. The function ``get_comments`` retrieves the comments on an article given its url. It can be used as a substitute for the comments by url option in the NYT Community API that is now deprecated and only return comments that were picked as editor's selection on account of an `unresolved issue <https://github.com/NYTimes/public_api_specs/issues/29>`_.

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

Acknowledgement
---------------
* The url used to retrieve comments from a given article in the function ``get_comments`` is taken from the `blog by Neal Caren <http://nealcaren.web.unc.edu/scraping-comments-from-the-new-york-times/>`_.
* NYT article search API is used for the article search.



