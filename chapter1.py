from time import time
from redis import Redis


ONE_WEEK_IN_SECONDS = 7 * 86400  # A
VOTE_SCORE = 432  # A


def article_vote(conn: Redis, user, article):
    cutoff = time() - ONE_WEEK_IN_SECONDS      #B
    if conn.zscore('time:', article) < cutoff:      #C
        return

    article_id = article.partition(":")[-1]  # D
    if conn.sadd("voted:" + article_id, user):  # E
        conn.zincrby("score:", VOTE_SCORE, article)  # E
        conn.hincrby(article, "votes", 1)  # E


def post_article(conn: Redis, user, title, link):
    article_id = str(conn.incr("article:"))  # A

    voted = "voted:" + article_id
    conn.sadd(voted, user)  # B
    conn.expire(voted, ONE_WEEK_IN_SECONDS)  # B

    now = time()  # C
    article = "article:" + article_id
    conn.hset(
        article,
        mapping={  # C
            "title": title,  # C
            # "link": link,  # C
            "poster": user,  # C
            "time": now,  # C
            "votes": 1,  # C
        },
    )  # C

    conn.zadd("score:", {article: now + VOTE_SCORE})  # D
    conn.zadd("time:", {article: now})  # D

    return article_id

ARTICLES_PER_PAGE = 2

def get_articles(conn: Redis, page, order='score:'):
    start = (page-1) * ARTICLES_PER_PAGE            #A
    end = start + ARTICLES_PER_PAGE - 1             #A

    ids = conn.zrevrange(order, start, end)         #B
    articles = []
    for id in ids:                                  #C
        article_data = conn.hgetall(id)             #C
        article_data['id'] = id                     #C
        articles.append(article_data)               #C

    return articles

def add_remove_groups(conn, article_id, to_add=[], to_remove=[]):
    article = 'article:' + article_id           #A
    for group in to_add:
        conn.sadd('group:' + group, article)    #B
    for group in to_remove:
        conn.srem('group:' + group, article)    #C

def get_group_articles(conn, group, page, order='score:'):
    key = order + group                                     #A
    if not conn.exists(key):                                #B
        conn.zinterstore(key,                               #C
            ['group:' + group, order],                      #C
            aggregate='max',                                #C
        )
        conn.expire(key, 60)                                #D
    return get_articles(conn, page, key)         
