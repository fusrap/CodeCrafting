# Byg og Kør Docker-Container

1. **Byg Docker-imagen**:

```cmd
	docker build --no-cache -t myapp:latest .
```
2. **Kør Docker-containeren**:

```cmd
	docker run -p 8000:8000 myapp:latest
```

3. Swagger-dokumentation:
```http
	http://localhost:8000/apidocs
```
