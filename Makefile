# Set the default goal if no targets were specified on the command line
.DEFAULT_GOAL = run
# Makes shell non-interactive and exit on any error
.SHELLFLAGS = -ec

PROJECT_NAME=vas3k_blog

run-dev:  ## Runs dev server locally
	poetry run python3 manage.py runserver 0.0.0.0:8000

docker-run-dev:  ## Runs dev server in docker
	poetry run python3 ./utils/wait_for_postgres.py
	poetry run python3 manage.py migrate
	poetry run python3 manage.py runserver 0.0.0.0:8000

docker-run-production:  ## Runs production server in docker
	poetry run python3 manage.py migrate
	poetry run gunicorn vas3k_blog.asgi:application -w 7 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8022 --capture-output --log-level debug --access-logfile - --error-logfile -

help:  ## Display this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | sort \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[0;32m%-30s\033[0m %s\n", $$1, $$2}'

migrate:  ## Migrate database to the latest version
	poetry run python3 manage.py migrate

.PHONY: \
	docker-run-dev \
	docker-run-production \
	run-dev \
	migrate
