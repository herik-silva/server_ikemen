FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando para iniciar o servidor Gunicorn
CMD ["bash", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 backend.wsgi:application"]
