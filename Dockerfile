FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py migrate

# Comando para iniciar o servidor Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
