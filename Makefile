COMPOSE=sudo docker compose

.PHONY: build up down restart clean logs

# Build the docker image in the container
build:
	$(COMPOSE) build

# Run the implementation
up:
	$(COMPOSE) up

# Stop everything and clean the RAM
down:
	$(COMPOSE) down

all: 
	$(COMPOSE) up --build

# Clean everything
clean:
	$(COMPOSE) down --rmi all --volumes

logs:
	$(COMPOSE) logs -f


