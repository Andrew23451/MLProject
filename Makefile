COMPOSE=sudo docker compose

.PHONY: build up down restart clean logs

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up

down:
	$(COMPOSE) down

all: 
	$(COMPOSE) up --build

clean:
	$(COMPOSE) down --rmi all --volumes

logs:
	$(COMPOSE) logs -f


