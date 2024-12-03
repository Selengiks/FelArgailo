git stash
git fetch
git reset --hard $1
docker compose stop fel_argailo
docker compose rm -f fel_argailo
docker compose build --no-cache
docker image prune -f
docker buildx prune -f
docker compose up -d fel_argailo