# Kripweb
This is a new web framework made by **vinkami** from the **krippars**

# Notes
Basically it's just a web framework like everyone expects.  
Currently, it's more like _flask_ than another separate framework cuz _flask_ is just objectively nice and easy to use and easy to get similar of, except this is more suitable to be used in asgi, like _quart_.  
Therefore, if you know how to write in _flask_, you're 90% gonna know how to write in _kripweb_.

# How to use
Here is a basic script you may write and let it run correctly.  
```python
from kripweb.handler import Handler
from kripweb.response import TextResponse, StaticResponse, HTMLResponse
from uvicorn import run

handler = Handler()


@handler.page("")
async def home():
    return HTMLResponse.render("main.html")


@handler.page("a", take_request=True)
async def a(request):
    return TextResponse(request.query_string)


@handler.page("favicon.ico")
async def favicon():
    return StaticResponse("logo.png")


@handler.error_page(404, take_request=True)
async def error404(request):
    return TextResponse(f"Nope, {request.scope['path']}")


run(handler.application)
```

I think you can get it by its look, but I'll explain.  
The `handler` is the core of the module and everything will run with it.  
`handler.page()` is a decorator function that tells the `handler` (or precisely, `handler.application`) what to look for when getting a HTTP request of a page.  
In addition, the functions' name actually doesn't matter, but you can use it tp do redirections.  
`handler.error_page()` allows you to set the pages to load if it gets any errors, like 404 not found in this example.  
Finally, this handler is not able to run itself currently, so _uvicorn_ is used here to start the server (TODO: add an in-module server so that it does not depend on something else)
