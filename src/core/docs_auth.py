from fastapi import Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from .config import settings
from starlette.middleware.base import BaseHTTPMiddleware

security = HTTPBasic()


def verify_docs_credentials(credentials: HTTPBasicCredentials) -> bool:
    """Verify documentation credentials"""
    is_username_correct = secrets.compare_digest(
        credentials.username, settings.docs_username
    )
    is_password_correct = secrets.compare_digest(
        credentials.password, settings.docs_password
    )
    return is_username_correct and is_password_correct


class DocsAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to protect documentation endpoints"""
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in ["/docs", "/redoc", "/openapi.json"]:
            auth_header = request.headers.get("authorization")
            
            if not auth_header or not auth_header.startswith("Basic "):
                return HTMLResponse(
                    content="""
                    <html>
                        <head>
                            <title>Authentication Required</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 40px; }
                                .container { max-width: 400px; margin: 0 auto; }
                                .form { background: #f5f5f5; padding: 20px; border-radius: 5px; }
                                input { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 3px; }
                                button { background: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 3px; cursor: pointer; }
                                button:hover { background: #0056b3; }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h2>Authentication Required</h2>
                                <p>Please enter your credentials to access the documentation:</p>
                                <div class="form">
                                    <form id="authForm">
                                        <label for="username">Username:</label><br>
                                        <input type="text" id="username" name="username" required><br>
                                        <label for="password">Password:</label><br>
                                        <input type="password" id="password" name="password" required><br><br>
                                        <button type="submit">Login</button>
                                    </form>
                                </div>
                            </div>
                            <script>
                                document.getElementById('authForm').addEventListener('submit', function(e) {
                                    e.preventDefault();
                                    const username = document.getElementById('username').value;
                                    const password = document.getElementById('password').value;
                                    const credentials = btoa(username + ':' + password);
                                    
                                    // Retry the request with credentials
                                    fetch(window.location.href, {
                                        headers: {
                                            'Authorization': 'Basic ' + credentials
                                        }
                                    }).then(response => {
                                        if (response.ok) {
                                            window.location.reload();
                                        } else {
                                            alert('Invalid credentials');
                                        }
                                    });
                                });
                            </script>
                        </body>
                    </html>
                    """,
                    status_code=401,
                    headers={"WWW-Authenticate": "Basic realm=Documentation"}
                )
            
            try:
                import base64
                credentials_str = auth_header.split(" ")[1]
                decoded_credentials = base64.b64decode(credentials_str).decode("utf-8")
                username, password = decoded_credentials.split(":", 1)
                
                if not verify_docs_credentials(HTTPBasicCredentials(username=username, password=password)):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Basic realm=Documentation"}
                    )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Basic realm=Documentation"}
                )
        
        response = await call_next(request)
        return response 