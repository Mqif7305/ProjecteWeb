# Instruccions d'us:


## Primera vegada:

S'ha penjat la base de dades al git per ahorrar temps d'execució. 
És una mala practica pero serà útil ja que al basar-se tot en apis triga molt en cargar dades.

S'utilitza uv per gestionar les dependencies, per cargar-les:

    (si no es disposa de uv):  sudo apt install uv

    uv sync

### Amb BBD plena:

    uv run python manage.py makemigrations
    uv run python manage.py migrate

Temps estimat: 5 > min 
    

### Amb BDD buida:

    uv run python manage.py makemigrations
    uv run python manage.py migrate
    docker compose run load-all 

Temps estimat: 45 < min


## Per obrir la web:

    docker compose up web


## Per la base de dades:


Al fer ús d'apis s'ha possat un temps generos entre request de 5 seg.
Aquest temps és important per evitar bloqueig temporals del servidor per abusar de request.


### Per cargar tot en un unic proces:

    docker compose run load-all

        (temps estimat: 45 min)


### Per cargar per parts:

#### Cargar ApiSteam:

    docker compose run load-steam

#### Cargar Ofertes:

    docker compose run load-api