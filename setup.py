from setuptools import setup

def readme():
    with open('README.rst') as file:
        return file.read()

setup(name='nytcomments',
      version='0.1',
      description='Package to retrieve comments from the New York Time articles that also serves as API Wrapper for NYT article search and performs the function of the now deprecated NYT Community API',
      long_description=readme(),
      url='https://github.com/AashitaK/nyt-comments',
      keywords=['Scraper for comments from the New York Time articles', 'API Wrapper for NYT API'],
      author='Aashita Kesarwani',
      author_email='kesar01@gmail.com',
      license='MIT',
      packages=['nytcomments'],
      install_requires=[
          'requests',
          'pandas',
      ],
      zip_safe=False)
