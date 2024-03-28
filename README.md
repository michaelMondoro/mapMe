# mapMe
Let’s unpack the `app.py` script, which is the brains behind a Flask app dealing with web content and APIs for network traffic data shenanigans. Here's the summary:

### Imports and Initial Setup
- It starts off by pulling in the big guns: Flask, pandas, geopandas, and SQLite for all the heavy lifting.
- Kicks off the Flask app and gets it all dressed up with environmental variables like hostname, host IP, and that all-important API token.

### Helper Function
- **check_mitm_header(request)**: Sniffs around to see if there's a `MITM-HOST` header in the incoming request, a dead giveaway it’s been snagged by mitmproxy. It logs and hands back the client's ID, snagged from the `MITM-HOST` header or the request's remote address.

### Routes
- **@app.route("/")**: The welcome mat of the app, serving up `index.html` with the client’s address and hostname on a silver platter.
- **@app.route("/update")**: Goes fishing in the SQLite database for the freshest client data, jazzes it up into a GeoDataFrame for some map magic, and tosses it back as JSON. This spot’s the go-to for the latest network traffic scoop.
- **@app.route("/clear_session", methods=["POST"])**: Hits the reset button on the current client’s session data in the SQLite database, wiping the slate clean.

### Main Block
- Takes a crack at linking up with MongoDB when the show starts and then revs up the Flask app on the chosen host and port.

Then there’s the `start_proxy.sh` script, a Bash maestro that gets the mitmproxy show on the road with `map_addon.py` as its wingman. It tweaks the `block_global` setting to false to let the proxy snag global traffic.

In a nutshell, `app.py` is the backstage tech wizard for a web app that keeps tabs on network traffic data, playing nice with MongoDB and SQLite, and slicing and dicing geospatial data to chat with the front end through HTTP APIs. And `start_proxy.sh`? It’s the backstage pass to get the mitmproxy up and running, all set for some serious network traffic detective work. Yeehaw to tech prowess!

**The documentation for the functioning of db.py, map_addon.py, and mitm.py is located in the README.md file within the src folder. Similarly, the workings of main.js and map.js are documented in the README.md file situated in the js directory under the static folder of your project. This setup ensures that documentation is organized and easily accessible, aligning with the structure of the project's codebase.**