db:
	python manage.py makemigrations
	python manage.py migrate
server:
	python manage.py runserver
all:
	make db
	make server
