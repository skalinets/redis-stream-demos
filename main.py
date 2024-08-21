import fasthtml.common as fh

from chapter1 import article_vote, get_articles, post_article
from redis import Redis
from icecream import ic
from faker import Faker

app, rt = fh.fast_app(live=True)


def _show_article(article):
    # ic(article[b"title"])
    ic(article["id"])
    return fh.Card(
        fh.P(article["title"], article["poster"]),
        fh.P(article["votes"]),
        fh.Form(
            fh.Hidden(name="article_id", value=article["id"]),
            fh.Button("Vote"),
            hx_post="/vote",
            hx_target="#messages",
        ),
    )


conn = Redis("localhost", 6379, decode_responses=True)


def _show_all_articles():
    messages = get_articles(conn, 1)
    # ic(messages)
    return fh.Div(*[_show_article(m) for m in messages])


@rt("/")  # pyright: ignore[]
def get():
    return fh.Main(
        fh.H1("Messages FOO"),
        fh.Form(
            fh.Input(type="text", name="title", placeholder="title"),
            fh.Input(type="text", name="user", placeholder="user"),
            fh.Button("Submit"),
            hx_post="/add",
            hx_target="#messages",
        ),
        fh.Div(
            id="messages",
            *_show_all_articles(),
        ),
    )


@rt("/add")  # # pyright: ignore[]
def post1(title: str, user: str):  # # pyright: ignore[]
    post_article(conn, user, title, "")
    return _show_all_articles()


@rt("/vote")  # # pyright: ignore[]
def post(article_id: str):  # # pyright: ignore[]
    ic(article_id)
    faker = Faker()
    user_name = faker.profile().get("username")
    article_vote(conn, user_name, article_id)
    return _show_all_articles()


fh.serve()
