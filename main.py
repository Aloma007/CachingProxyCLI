import argparse
import sys
import requests
import uvicorn
from fastapi import FastAPI, Request, Response

app = FastAPI()

ORIGIN_URL = ""
cache_store = {} 

# A dedicated internal route to handle the clear-cache command
@app.post("/clear-internal-cache")
async def clear_internal_cache():
    cache_store.clear()
    return {"status": "success", "message": "In-memory cache wiped."}

@app.get("/{path:path}")
async def proxy_request(path: str, request: Request):
    global ORIGIN_URL
    
    target_url = f"{ORIGIN_URL}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"
        
    if target_url in cache_store:
        print(f"Cache HIT: {target_url}")
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
        origin_headers = dict(origin_response.headers)
        
        cache_store[target_url] = {
            "content": origin_response.content,
            "status_code": origin_response.status_code,
            "headers": origin_headers
        }
        
        response_headers = origin_headers.copy()
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

    # The updated cache clearing logic
    if args.clear_cache:
        print("Sending clear cache command to the running server...")
        try:
            # We fire a POST request to the hidden endpoint on the local server
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
    print(f"Forwarding requests to origin: {ORIGIN_URL}")
    
    uvicorn.run(app, host="127.0.0.1", port=args.port)

if __name__ == "__main__":
    main()