import argparse
import sys
import requests
import uvicorn
import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

ORIGIN_URL = ""
cache_store = {} 
# New dictionary to track our analytics
analytics = {"hits": 0, "misses": 0}

@app.post("/clear-internal-cache")
async def clear_internal_cache():
    cache_store.clear()
    analytics["hits"] = 0
    analytics["misses"] = 0
    return {"status": "success", "message": "In-memory cache wiped."}

# Endpoint to serve the raw JSON data for our dashboard
@app.get("/api/dashboard-stats")
async def get_dashboard_stats():
    return {
        "hits": analytics["hits"],
        "misses": analytics["misses"],
        "cached_urls": list(cache_store.keys()),
        "origin": ORIGIN_URL
    }

# Endpoint to serve the HTML webpage
@app.get("/dashboard")
async def serve_dashboard():
    try:
        with open("dashboard.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return Response(content="dashboard.html not found.", status_code=404)

# The catch-all proxy route MUST remain at the bottom
@app.get("/{path:path}")
async def proxy_request(path: str, request: Request):
    global ORIGIN_URL
    
    target_url = f"{ORIGIN_URL}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"
        
    if target_url in cache_store:
        print(f"Cache HIT: {target_url}")
        analytics["hits"] += 1  # Increment hit counter
        
        cached_data = cache_store[target_url]
        headers = cached_data["headers"].copy()
        headers["X-Cache"] = "HIT"
        
        return Response(
            content=cached_data["content"],
            status_code=cached_data["status_code"],
            headers=headers
        )

    print(f"Cache MISS: {target_url}")
    try:
        origin_response = requests.get(target_url)
        
        # Clean the headers by removing compression and chunking headers
        clean_headers = {}
        for key, value in origin_response.headers.items():
            if key.lower() not in ['content-encoding', 'transfer-encoding', 'connection']:
                clean_headers[key] = value
                
        # Save the fresh data and the CLEANED headers into our dictionary
        cache_store[target_url] = {
            "content": origin_response.content,
            "status_code": origin_response.status_code,
            "headers": clean_headers
        }
        
        analytics["misses"] += 1
        
        # Inject the X-Cache header
        response_headers = clean_headers.copy()
        response_headers["X-Cache"] = "MISS"
        
        return Response(
            content=origin_response.content,
            status_code=origin_response.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.RequestException as e:
        return Response(content=f"Bad Gateway: {str(e)}", status_code=502)


def main():
    global ORIGIN_URL
    
    parser = argparse.ArgumentParser(description="A caching proxy server")
    parser.add_argument("--port", type=int, default=3000, help="Port on which the server will run")
    parser.add_argument("--origin", type=str, help="URL of the server to which requests are forwarded")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the stored cache and exit")
    
    args = parser.parse_args()

    if args.clear_cache:
        print("Sending clear cache command to the running server...")
        try:
            response = requests.post(f"http://127.0.0.1:{args.port}/clear-internal-cache")
            if response.status_code == 200:
                print("Cache cleared successfully.")
            else:
                print(f"Failed to clear cache. Server returned status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to proxy on port {args.port}. Is the server running?")
        sys.exit(0)

    if not args.origin:
        parser.error("--origin is required unless you are clearing the cache with --clear-cache")

    ORIGIN_URL = args.origin.rstrip("/")
    
    print(f"Starting proxy server on port {args.port}...")
    print(f"Dashboard available at: http://127.0.0.1:{args.port}/dashboard")
    print(f"Forwarding requests to origin: {ORIGIN_URL}")
    
    uvicorn.run(app, host="127.0.0.1", port=args.port)

if __name__ == "__main__":
    main()