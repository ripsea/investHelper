FROM python:3.12.3
WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENTRYPOINT FLASK_APP=app flask run --host=0.0.0.0
# EXPOSE 5000 #gunicorn default 80 port

COPY app.py .
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# RUN python3 -m pip install flask
# RUN python3 -m pip install requests
# RUN python3 -m pip install selenium
# RUN python3 -m pip install webdriver_manager
# RUN python3 -m pip install beautifulsoup4

COPY . .
# CMD ["flask", "run", '--host', '0.0.0.0']
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]