from time import time
from redis.asyncio.client import Redis
# from icecream import ic


ONE_WEEK_IN_SECONDS = 7 * 86400  # A
VOTE_SCORE = 432  # A


async def article_vote(conn: Redis, user, article_id):
    cutoff = time() - ONE_WEEK_IN_SECONDS      #B
    article = "article:" + article_id  # D
    # ic(article)
    # return
    if await conn.zscore('time:', article) < cutoff:      #C
        return

    # article_id = article.partition(":")[-1]  # D
    if await conn.sadd("voted:" + article_id, user):  # E
        await conn.zincrby("score:", VOTE_SCORE, article)  # E
        await conn.hincrby(article, "votes", 1)  # E


async def post_article(conn: Redis, user, title, link):
    article_id = str(await conn.incr("article:"))  # A

    voted = "voted:" + article_id
    await conn.sadd(voted, user)  # B
    await conn.expire(voted, ONE_WEEK_IN_SECONDS)  # B

    now = time()  # C
    article = "article:" + article_id
    await conn.hset(
        article,
        mapping={  # C
            "title": title,  # C
            # "link": link,  # C
            "poster": user,  # C
            "time": now,  # C
            "votes": 1,  # C
        },
    )  # C

    await conn.zadd("score:", {article: now + VOTE_SCORE})  # D
    await conn.zadd("time:", {article: now})  # D

    return article_id

ARTICLES_PER_PAGE = 10

async def get_articles(conn: Redis, page, order='score:'):
    start = (page-1) * ARTICLES_PER_PAGE            #A
    end = start + ARTICLES_PER_PAGE - 1             #A

    ids = await conn.zrevrange(order, start, end)         #B
    articles = []
    for id in ids:                                  #C
        article_data = await conn.hgetall(id)             #C
        if article_data:
            article_data['id'] = id.split(":")[-1]                     #C
            articles.append(article_data)               #C

    return articles

async def add_remove_groups(conn, article_id, to_add=[], to_remove=[]):
    article = 'article:' + article_id           #A
    for group in to_add:
        await conn.sadd('group:' + group, article)    #B
    for group in to_remove:
        await conn.srem('group:' + group, article)    #C

async def get_group_articles(conn, group, page, order='score:'):
    key = order + group                                     #A
    if not await conn.exists(key):                                #B
        await conn.zinterstore(key,                               #C
            ['group:' + group, order],                      #C
            aggregate='max',                                #C
        )
        await conn.expire(key, 60)                                #D
    return await get_articles(conn, page, key)         
