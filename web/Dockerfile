FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY  ./static /home/myapp/static/
COPY  ./templates /home/myapp/templates/
COPY  app.py /home/myapp/
EXPOSE 5050
CMD python /home/myapp/app.py