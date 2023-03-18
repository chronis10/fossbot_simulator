FROM python:3.8
WORKDIR /app
COPY requirements.txt requirements.txt
COPY requirements_app.txt requirements_app.txt
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements_app.txt
COPY . .
CMD [ "python3", "app.py"]