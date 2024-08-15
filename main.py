from fasthtml.common import (
    RedirectResponse,
    fast_app,
    serve,
    Div,
    P,
    Form,
    Group,
    # mk_input,
    Button,
    Card,
    Ul,
    Titled,
    Input,
    Main,
    H1,
    A,
)
from fasthtml import FastHTML

from chapter1 import get_articles, post_article
from redis import Redis
from icecream import ic

app = FastHTML()
# messages = ["This is a message, which will get rendered as a paragraph"]


def _show_article(article):
    # ic(article[b"title"])
    return Card(
        Titled(article["title"], article["poster"]),
        P(article["votes"]),
        P(article["time"]),
    )

conn = Redis("localhost", 6379, decode_responses=True)

@app.get("/") # pyright: ignore[]
def home():
    messages = get_articles(conn, 1)
    ic(messages)
    return Main(
        H1("Messages"),
        Form(
            Input(type="text", name="title", placeholder="title"),
            Input(type="text", name="user", placeholder="user"),
            Button("Submit"),
            action="/",
            method="post",
        ),
        *[_show_article(msg) for msg in messages],
        # A("Link to Page 2 (to add messages)", href="/page2"),
    )


@app.get("/page2") # pyright: ignore[]
def page2():
    return Main(
        P("Add a message with the form below:"),
        Form(
            Input(type="text", name="title", placeholder="title"),
            Input(type="text", name="user", placeholder="user"),
            Button("Submit"),
            action="/",
            method="post",
        ),
    )


@app.post("/") # # pyright: ignore[]
def add_message(title: str, user: str):
    post_article(conn, user, title, "")
    return home()


serve()
