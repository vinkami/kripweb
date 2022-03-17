# API Reference

## Handler
<pre><i>class</i> handler.<b>Handler</b>(setting=None)</pre>
> This is the central object of the whole web server, responsible for storing, adding, and finding back the views/pages of the website, and storing the settings of how the responses should be made, etc.  
You can simply write these lines at the top of your main script to set up a proper handler:

```python
from kripweb.handler import Handler

handler = Handler()
```
> <pre><i>function</i> <b>page</b>(url="", method="GET", take_request=False, name="")</pre>
The decorator to add a view to your website. If there's no such page(`Node`), the function will automatically create one for convenience.

>Arguments:  
>> - url: the url path that will lead to this view
>> - method: the HTTP request method that this view will handle, usually "GET" or "POST"
>> - take_request: to select whether a `Request` object about the HTTP request should be called with. Select this to **True** and put a `request` parameter in the view function to use it.
>> - name: a name to identify the current `Node` (or simply, the GET view of the page), used for `Redirect.to_view()`.

> <pre><i>function</i> <b>error_page</b>(err_code="404", take_request=False)</pre>
The decorator to add an error page view to your website.  

>Arguments:
>> - err_code: the type of error that this view will handle, represented as an error code. The current error codes are:
>>> - "404": The typical 404 Not Found error. Called when a client tried to access a page that does not exist.
>>> - "bad_host": Called when a client tries to access any webpage without using an allowed hostname. Ignored if no allowed hostnames are set. It's recommended to simply `Redirect` the client to an allowed host.
>> - take_request: same as `handler.page`.

> <pre><i>function</i> <b>get_application</b>()</pre>  
Returns an `ASGIApplication` instance which set up an interface for other ASGI-supported modules to work with.  
Currently, this `kripweb` module cannot work by itself as the server management part is not implemented yet. That's why in all examples, `uvicorn` is playing a role to manage the server.

> <pre><i>function</i> <b>get_page</b>(url)</pre>  
Pathfind the matching `Node` object with the url.  

> Arguments:
>> - url: the url path of the `Node` required.

>Returns:
>> - `Node` that includes the views and pages information corresponding to the url given  
or
>> - `DNENode` if the required url page cannot be found. 

> <pre><i>function</i> <b>ingest_handler</b>(subhandler)</pre>
A way to include the views from other scripts, as a so-called "subpages".

> Argument:
>> - subhandler: A subhandler for handling other pages. `PagesHandler` is the only subhandler for now.

> <pre><i>function</i> <b>name_to_url</b>(page_name, from_subpages="")</pre>
Convert an internal name to the url path of the view. Usually used by `Redirect.to_view()`.

> Arguments:
>> - page_name: The internal name of the `Node`, the same one as when `handler.page()` is called.
>> - from_subpages: The subpages' name that the `Node` is from, the same one as when `PagesHandler()` is called in any other scripts. An empty string indicates that the view is in the main script.

> Return: The url path of the wanted view.

> <pre><i>function</i> <b>static_url_for</b>(filename)</pre>
Convert a filename(filepath) to a static url path of the website. Usually used by `StaticResponse()` and sometimes by you in Jinja2 HTML files with `{{ static() }}` method.

> Arguments:
>> - filename: the filename to locate the static file. The static path will be added thus there's no need to manually add it.

> Return: The static url path.

---

## Setting
<pre><i>class</i> setting.<b>Setting</b>()</pre>
> This is responsible for holding any freely-changable variables that affect how the handler should behave when finding things or working with codes.  
There are no functions other than the setters of the variables, so below is the list of the variables and their functions.  
You can change these settings anytime during the program (not quite recommended tho), and everything should follow the changes immediately without any restart.  
This also means that the variables can be set directly when you initiate the Setting class, or by calling the setters at anytime.

> <pre><b>template_path</b> :str = "template/"</pre>
> Change with `set_template_path()`  
> To locate the folder of the template files, relative to the main program

> <pre><b>static_path</b> :str = "static/"</pre>
> Change with `set_static_path()`
> To locate the folder of the static files, relative to the main program

> <pre><b>await_send_mode</b> :bool = False</pre>
> Toggle with `toggle_await_send_mode()`
> To show how your functions respond to web requests.
>> False: the functions return the Response object directly  
>> True: the functions take a `send` function as a parameter, and respond by calling `await send(resp)`

> <pre><b>hosts_allowed</b> :list = []</pre>
> Append with `allow_host()`
> To make a semi firewall the blocks requests that did not use the ips or hostnames to access the pages.   
> You can set how the program should behave after meeting this program with `@handler.error_page(err_code="bad_host")` or leave it as default.

> <pre><b>static_url</b> :str = "/static/"</pre>
> Change with `set_static_url()`
> To locate the url branch for static files' locations.  
> This does not affect where you put the static files, but only where you find them by directly putting in the url.  
> Although you should not be using /static/ as an url branch for normal webpages, you can change this variable if it collides with your code.

> <pre><b>print_connecton_information</b> :bool = True</pre>
> Toggle with `toggle_print_conn_info()`
> To toggle whether you want the information about visitors accessing your pages to be printed.  
> This is helpful if you want to debug your code by printing something else out and not have conn info mixed with your own debug messages.  
> You should leave it True most of the time because it helps identify unexpected traffics.

> <pre><b>app_logging_msg</b> :callable = constant.app_logging_message()</pre>
> Change with `set_app_logging_msg()`
> To customize the conn info printed.  
> As there are quite a lot of information that you may or may not want to see, you have the full access to the request and response objects to pull out whatever you need and arrange them however you want.  
> The parameter function should accept a `request` and a `response`, then return a string. The returning string is what you see after the <i>INFO:</i> keyword.
