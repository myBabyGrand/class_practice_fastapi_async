# class_practice_fastapi_async
실전! fastAPI 비동기 (인프런)

### Install Package (python 3.11+)
> pip install -r src/requirements.txt

### Docker desktop 실행

### Docker Compose
```docker
#run db & redis
docker compose up -d
docker compose down

#with servers
docker compose -f docker-compose.server.yml up -d
docker compose down --remove-orphans
``` 

### Table Creation 및 DB Migration
 - in **src** directory
> alembic upgrade head
