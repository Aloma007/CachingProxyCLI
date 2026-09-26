# Caching Proxy CLI

A lightweight command-line tool that starts a caching proxy server. It intercepts client requests, forwards them to an origin server, and caches the responses locally. Subsequent identical requests are served directly from the cache, significantly reducing latency and the load on the origin server.

This project was built as an intermediate backend challenge from [roadmap.sh] https://roadmap.sh/projects/caching-server

## Features

* **Command-Line Interface:** Easily start the proxy server using a custom `caching-proxy` command.
* **Transparent Caching:** Intercepts dynamic paths and query parameters, caching the raw content, status codes, and HTTP headers.
* **Cache Status Headers:** Injects custom `X-Cache: HIT` and `X-Cache: MISS` headers into the response to easily identify data sources.
* **Inter-Process Cache Clearing:** Includes a `--clear-cache` flag that communicates directly with the running server to wipe the in-memory cache without requiring a server restart.

## 🛠️ Tech Stack

* **Python 3**
* **FastAPI** (Server routing and HTTP handling)
* **Uvicorn** (ASGI server)
* **Requests** (HTTP client for fetching origin data)
* **Argparse** (Built-in Python library for CLI parsing)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/caching-proxy.git
   cd caching-proxy
   ```

2. **Create and activate a virtual environment:**
   * **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the CLI tool:**
   Run the following command to install the package dependencies and map the custom terminal command:
   ```bash
   pip install -e .
   ```

## 💻 Usage

### Starting the Proxy Server

Start the proxy by specifying the port you want it to run on and the origin URL you want to mirror.

```bash
caching-proxy --port 3000 --origin http://dummyjson.com
```
*   `--port`: The port on which the proxy server will listen (defaults to 3000).
*   `--origin`: The base URL of the actual server to which requests will be forwarded.

### Testing the Cache

Once the server is running, open your browser or an API testing tool and make a request to your local proxy:

1. **First Request (Cache MISS):**
   Navigate to `http://127.0.0.1:3000/products`. The proxy fetches the data from the origin, saves it, and returns it with the header:
   `X-Cache: MISS`

2. **Second Request (Cache HIT):**
   Refresh the page. The proxy retrieves the data instantly from its local memory and returns it with the header:
   `X-Cache: HIT`

### Clearing the Cache

To clear the stored cache while the server is running, open a **new terminal window** (ensure your virtual environment is active) and run:

```bash
caching-proxy --port 3000 --clear-cache
```
*Note: Make sure to pass the same port number your server is currently running on so the CLI knows where to send the clear command.*

## 📂 Project Structure

```text
caching-proxy/
├── main.py        # Core application logic, routing, and CLI setup
├── setup.py       # Package configuration to create the native command
├── .gitignore     # Git ignore rules
└── README.md      # Project documentation
```

## License

Distributed under the GPL-3.0 License. See LICENSE for more information.
