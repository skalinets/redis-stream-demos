import redis

from chapter1 import (
    add_remove_groups,
    article_vote,
    get_articles,
    get_group_articles,
    post_article,
)
from icecream import ic


def test_redis():
    r = redis.Redis(host="localhost", port=6379, db=0)
    r.set("foo", "bar")
    print(r.get("foo"))


def test_some_scenario():
    db = redis.Redis(host="localhost", port=6379, db=0)
    # clean redis
    # db.flushall()
    #
    #
    #
    # for i in range(1, 100000):
    i = 100
    post_article(db, "user12", f"title{i}", f"link{i}")
    post_article(db, "user12", f"title{i}", f"link{i}")
    post_article(db, "user12", f"title{i}", f"link{i}")

    article_vote(db, "user1", "2")
    article_vote(db, "user4", "2")
    # article_vote(db, "user3", "article:2")
    # article_vote(db, "user1", "article:3")
    # article_vote(db, "user2", "article:3")
    # article_vote(db, "user1", "article:4")

    add_remove_groups(db, "2", ["good"])
    add_remove_groups(db, "9", ["good"])

    as2 = get_group_articles(db, "good", 1)
    ic(as2)
    # assert 1 == 2
    #
    #
    #
    as1 = get_articles(db, 100)[:4]
    # ic(as1)
    # assert as1 == []
    #

def test_srt():
    assert ""
