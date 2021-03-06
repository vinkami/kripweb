# Kripweb
Kripweb is asynchronous webside framework module for Python 3.

This is like Flask, Django and other popular webside frameworks, which can help you write your website without the need to handle annoying http requests.


# Installation
**Python 3.10+ is required**  
This bad developer didn't think of old-version compatibility and used match-case right away.

### The Module Itself
`python -m pip install kripweb`

### Necessary Packages
 - Jinja2 >= 3.0.1

### Optional Packages
 - Any other ASGI-supported modules for server deployment. For example:
    - Uvicorn >= 0.14.0
    - Hypercorn >= 0.11.2
    
# Quick Example
### main.py

```python
from kripweb.handler import Handler
from kripweb.response import TextResponse, StaticResponse, HTMLResponse, Redirect, errorize
import uvicorn

from other_scripts import handler as other_handler

ALLOWED_HOST = "www.vinkami.tech"

handler = Handler()
handler.setting.allow_host(ALLOWED_HOST)
handler.ingest_subhandler(other_handler)


@handler.page("", name="home")
async def home():
    return HTMLResponse.render("index.html")


@handler.page("query", take_request=True)
async def a(request):
    return TextResponse(request.query_string)


@handler.page("favicon.ico")
async def favicon():
    return StaticResponse("logo.png")


@handler.page("user/<name>", name="hi", take_request=True)
async def hi(request):
    return TextResponse(f"Hi, {request.kwargs['name']}!")


@handler.page("go-there")
async def go():
    return Redirect.to_view("here", "other")


@handler.error_page("bad_host")
async def bad_host():
    return Redirect(f"https://{ALLOWED_HOST}")


@handler.error_page("404")
async def error404():
    return errorize(TextResponse(f"Nope, this path is not valid"), 404)


if __name__ == '__main__':
    uvicorn.run(handler.get_application(), host="127.0.0.1", port=8000)
```

### other_scripts.py

```python
from kripweb.handler import PagesHandler
from kripweb.response import TextResponse, Redirect, HTMLResponse

handler = PagesHandler(name="other", url="somewhere")


@handler.page("back")
async def go_back_to_home_page():
    return Redirect.to_view("home")


@handler.page("here")
async def here():
    return TextResponse("Hi you're here!")


@handler.page("name")
async def name():
    return HTMLResponse("""
    <html>
        <head>[Skipped]</head>
        <body>
            <form>
                <input type="text" name="name">
                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    """)


@handler.page("name", method="POST", take_request=True)
async def name_post(request):
    return TextResponse(f"Hi, {request.form.get('name')}!")
```