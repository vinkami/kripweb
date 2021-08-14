# Quickstart

## Minimal Example:
This is a basic kripweb application looks like:
```python
from kripweb.handler import Handler
from kripweb.response import TextResponse

import uvicorn

handler = Handler()

@handler.page("")
async def home():
    return TextResponse("Welcome to Kripaars' world!")


if __name__ == "__main__":
    uvicorn.run(handler.get_application(), host="localhost", port=80)
```
This is what we did in the example,  
>1. Firstly, we imported the kripweb's handler. When we are using this module, we would register all the route
        to the handler.<br> The handler will analyze and process the request according to the registered methods.
2. Then, we imported a `TextResponse()`. This is used for returning a response in text form. 
3. Next, we imported uvicorn as our ASGI server implementation. Uvicorn will load in all the request and push them to the handler to process our request.
4. We opened a handler instance.
5. Then, we created a new page. Register the 'home' page by using the decorator `@handler.page()`
6. We return the "Welcome to Kripaars' world!" string in text form by calling `TextResponse()`.
7. Call the `uvicorn.run()` method to make the server start.
---

## Routing
Web applications uses a good URL to help user to remember this page and vists the page directly.
Use decorator `handler.page()` to bind a URL to function.

```python
@handler.page("")
async def index():
    return TextResponse("Krip Web!")


@handler.page("ping")
async def ping():
    return TextResponse("Pong!")
```
---

## URL Variables
Adding variable sector by marking sections with `<section_name>`. 
Your function can the naccess the above-marked name with the request.
```python
@handler.page("user/<username>", take_request=True)
async def user(request):
    return TextResponse(f"User {request.kwargs.get('username')}")
```
---

## Responses
There are different response in kripweb. Each of them correspond to a return form.<br>
Use the `return` keyword to return the response in the function.


- `TextResponse` \- Return in text form  
- `ImageResponse` \-  Return an image  
- `FileResponse` \- Return a file  
- `StaticResponse` \- Return static file (e.g, js files, css files)  
- `HTMLResponse` \- Return html code to render.
- `Redirect` \- Redirect the user to another page according to the url provided in parameter.
---

## Request
You can pass in `True` in the parameter `take_request` in the decorator `handler.page`<br>
Now, you can access `request` in your function context as the following example.
```python
@handler.page("get_host", take_request=True)
async def get_host(request):
    return TextResponse(request.host)
```
---

## Method
HTTP Methods represents different meanings, for example,<br>
GET method requests a representation of the specified resource.<br><br>
Add parameter `method` as the following example to permit which method allowed in a request<br>
The `method` parameter is, by default, the `GET` method. 
```python
@handler.page("ping", method="POST")
async def ping():
    return TextResponse("Pong!")
```
---

## Ingestion
This is a special feature in kripweb which allows one handler absorbs the other handler's routes into its own route map.  
For Example, `AHandler` have 2 routes and when the `BHandler.ingest_handler(AHandler)` is called,  
`BHandler` will have all routes from `AHandler` along with its binded functions.
`name` in `PagesHandler` provide a name for url resolving when the `Redirect` response is used,   
`url` is an indicator for the main handler to know where to find pages in the corresponding `PagesHandler` instead of itself, when using the `get_page` method.
```python
AHandler = PagesHandler(name="a", url="a")
BHandler = Handler()

@AHandler.page("secret_method_that_handler_b_dont_have")
async def special_secret_method():
    return TextResponse("Handler B is stupid.")


BHandler.ingest_handler(AHandler) # Now Handler B knows all the route in AHandler including its secret.
```

## Error Handling
Things might not always happen as everything thought, thus all errors need to be handled.  
By default, there are a few error responses preset in case you did not specifically write them in your scripts.  
However, it is recommended to overwrite the preset pages with `@handler.error_page()`.  
In those error view functions, you should also return the responses wrapped with `errorize()` so that the status codes are correct.  
If you do not want to use `errorize()`, you can instead set `response.status_code` and `response.status` yourself.
```python
from kripweb.response import errorize, TextResponse


@handler.error_page(404, take_request=True)
async def error404(request):
    return errorize(TextResponse(f"Nope, {request._scope['path']} is not a valid path for content."), 404)
```