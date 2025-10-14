git stash
git fetch
git reset --hard $1
docker compose stop FelArgailo
docker compose rm -f FelArgailo
docker compose build --no-cache
docker image prune -f
docker buildx prune -f
docker compose up -d FelArgailo