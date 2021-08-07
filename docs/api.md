# API Reference

## Handler
<pre><i>class</i> handler.<b>Handler</b>(setting=None)</pre>
> This is the central object of the whole web server,responsible for storing, adding, and finding back the views/pages of the website, and storing the settings of how the responses should be made, etc.  
> You can simply write these lines at the top of your main script to set up a proper handler:
```python
from kripweb.handler import Handler
handler = Handler()
```
> <pre><i>function</i> <b>page</b>(url="", method="GET", take_request=False, name="")</pre>
> The decorator to add a view to your website. If there's no such page(`Node`), the function will automatically create one for convenience.  
> Arguments:
> 
> - url: the url path that will lead to this view
> - method: the HTTP request method that this view will handle, usually "GET" or "POST"
> - take_request: to select whether a `Request` object about the HTTP request should be called with. Select this to **True** and put a `request` parameter in the view function to use it.
> - name: a name to identify the current `Node` (or simply, the GET view of the page), used for `Redirect.to_view()`.

> <pre><i>function</i> <b>error_page</b>(err_code="404", take_request=False)</pre>
> The decorator to add an error page view to your website.  
> Arguments:
> 
> - err_code: the type of error that this view will handle, represented as an error code. The current error codes are:
>   - "404": The typical 404 Not Found error. Called when a client tried to access a page that does not exist.
>   - "bad_host": Called when a client tries to access any webpage without using an allowed hostname. Ignored if no allowed hostnames are set. It's recommended to simply `Redirect` the client to an allowed host.
> - take_request: same as `handler.page`.

> <pre><i>function</i> <b>get_application</b>()</pre>  
> Returns an `ASGIApplication` instance which set up an interface for other ASGI-supported modules to work with.  
> Currently, this `kripweb` module cannot work by itself as the server management part is not implemented yet. That's why in all examples, `uvicorn` is playing a role to manage the server.

> <pre><i>function</i> <b>get_page</b>(url)</pre>  
> Pathfind the matching `Node` object with the url.  
> Arguments:
> 
> - url: the url path of the `Node` required.
> 
> Returns:
> 
> - `Node` that includes the views and pages information corresponding to the url given  
> or
> - `DNENode` if the required url page cannot be found. 

> <pre><i>function</i> <b>ingest_handler</b>(subhandler)</pre>
> A way to include the views from other scripts, as a so-called "subpages".
> Argument:
> 
> - subhandler: A subhandler for handling other pages. `PagesHandler` is the only subhandler for now.

> <pre><i>function</i> <b>name_to_url</b>(page_name, from_subpages="")</pre>
> Convert an internal name to the url path of the view. Usually used by `Redirect.to_view()`.
> Arguments:
> 
> - page_name: The internal name of the `Node`, the same one as when `handler.page()` is called.
> - from_subpages: The subpages' name that the `Node` is from, the same one as when `PagesHandler()` is called in any other scripts. An empty string indicates that the view is in the main script.
> 
> Return: The url path of the wanted view.

> <pre><i>function</i> <b>static_url_for</b>(filename)</pre>
> Convert a filename(filepath) to a static url path of the website. Usually used by `StaticResponse()` and sometimes by you in Jinja2 HTML files with `{{ static() }}` method.
> Arguments:
> 
> - filename: the filename to locate the static file. The static path will be added thus there's no need to manually add it.
> 
> Return: The static url path.

## Setting
<pre><i>class</i> setting.<b>Setting</b>()</pre>

WIP