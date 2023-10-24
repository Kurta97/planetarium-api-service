# planetarium_api_service

Django project for managing planetarium API service

Welcome to the Planetarium API service! 
This application allows you to CRUD operations of ShowTheme, PlanetariumDome, 
AstronomyShow, ShowSession, Reservation models, keep track of shows, 
reservations and show schedule in your planetarium.

- To get started, users need to register and get JWT token.
- Default life-time of access token — 30 min, refresh token — 1 day.
- Download [ModHeader](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en)
Once registered, you can reserve seats at the planetarium,
view show sessions and information about different shows. 
But you can see only yours reservations and of course you can delete them.
You can also perform all data manipulations through the admin panel.

Also, you have documentations to all endpoints of the API (swagger or redoc).

## Installation

Python3 must be already installed

For Windows:
```shell
git clone https://github.com/Kurta97/planetarium_api_service.git
cd planetarium_api_service
python venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata planetarium_service_db_data.json
python manage.py runserver
```
For Mac (and Linux):
```shell
git clone https://github.com/Kurta97/planetarium_api_service.git
cd planetarium_api_service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata planetarium_service_db_data.json
python manage.py runserver
```

## Features

- Create an ingredient
- Edit an ingredient
- Delete an ingredient
- Create a dish
- Edit a dish
- Delete dish
- Read about dish
- Create a cooker
- Edit a cooker
- Delete a cooker
- Read about cooker
- You can use the service only after registration


## DB structure
![Db structure](planetarium_db_structure.png)
