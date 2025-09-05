# sonolus-server-web-fastapi
Quick FastAPI application designed to serve a compiled /dist/ from https://github.com/Sonolus/sonolus-server-web

# Setup
1. Install python
2. Make a venv (recommended, optional)
3. `pip install -r requirements.txt`
4. Move the compiled `/dist` folder to the project root
5. `python main.py` to serve (you can pair this with something like pm2!)
    - Alternatively, you can serve the app.py file directly.

### Serving - NGINX
This is a quick configuration to serve this on NGINX! You can use whatever you want.

```conf
server {
    listen 80;
    # your server name
    server_name subdomain.domain.tld;

    # use the port you specified in config
    location /server {
        proxy_pass http://127.0.0.1:39040;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # or serve your own webapp on the base url by deleting this redirect
    location = / {
        return 302 /server;
    }
}
```