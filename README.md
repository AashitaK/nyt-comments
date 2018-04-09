# nyt-comments
The package scraps comments posted on New York Times articles and converts the data into `pandas` dataframes (with an option to directly store it in csv files). The main function `get_dataset` returns two dataframes - one each for the articles and the comments that are cleaned up and preprocessed to be used as a dataset for data science/machine learning projects. The retrieval of the comments can be customized based on a number of parameters such as a specific timeline, a search query, etc. The function `get_articles` that returns only articles can be used as an API wrapper for NYT article search API to get the results processed as a ready-to-use pandas dataframe (with an option to store it in csv files). The above two functions `get_dataset` and `get_articles` uses NYT article search API inside and require the use of API key that can be found here. The third function `get_comments` retrieves the comments on an article given its url without the use of an API key.


### Dependencies
Python 3.4+


### Python package required
pandas

### Usage
```python
from nytcomments import get_dataset
articles_df, comments_df = get_dataset(ARTICLE_API_KEY, page_lower=0, page_upper=2)
```
Please refer to the [tutorial here](https://github.com/AashitaK/nyt-comments/blob/master/Tutorial.ipynb) for illustration of the three functions `get_dataset`, `get_comments` and `get_articles` as well as detailed information about the function arguments. You must agree to the [Terms of Use](http://developer.nytimes.com/tou) for the NYT API to use the functions `get_dataset` and `get_articles`.

## Acknowledgement:
* A part of code used in the function `get_comments` is inspired from the code written by [Neal Caren](http://nealcaren.web.unc.edu/scraping-comments-from-the-new-york-times/) with some modification.
* NYT article search API is used for the article search.



