
from newspaper import Article
import pandas as pd
import sys, time, json, requests, uuid

def get_articles_newsapi(config): 

    def build_query(config, page=1):
        query = "http://newsapi.org/v2/everything?"
        for k,v in config.items():
            if v is None or v == "":
                continue
            query += f"{k}={v}&"
        query += f"page={page}"
        return query

    page = 1
    all_articles = []
    while True:
        url = build_query(config, page)
        print(f"Getting page {page}...")
        response = requests.get(url).json()
        articles = response.get("articles")
        if response["status"] == "error":
            break
        if not articles:
            break
        if page > config["pageSize"]: 
            break

        all_articles.extend(articles)
        
        page += 1
    
    return(all_articles)

def parse_article_text(url, content):
    try:
        article = Article(url, )
        article.download()
        article.parse()
        article_text = article.text
    except: 
        article_text = content
        print("Article `download()` failed")
    return(article_text)


def get_news_pages(NEWS_API_KEY, query, from_date, to_date, sort_by, searchIn, page_size):

    config = {}
    config["q"] = query
    config["from"] = from_date
    config["to"] = to_date
    config["sortBy"] = sort_by
    config["searchIn"] = searchIn
    config["pageSize"] = page_size
    config["apiKey"] = NEWS_API_KEY

    articles = get_articles_newsapi(config) 
    df = pd.DataFrame(articles)
    df['media'] = df['source'].apply(lambda x: x['name'])
    df["text"] = df.apply(lambda x: parse_article_text(x.url, x.content), axis=1)
    df['text'] = df['text'].str.replace('\n\n','\n')
    df['words'] = df['text'].apply(lambda x: len(x.split()))
    df['source'] = "news"
    df = df[["source", "title", "author", "description", "media", "url", "publishedAt", "text", "words"]]
    print("Number of articles:", len(df))

    return(df)



    

