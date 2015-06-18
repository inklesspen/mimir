FROM python:3.4

EXPOSE 6543

COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install --upgrade setuptools && pip install --upgrade wheel && pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

ADD . /code
WORKDIR /code

RUN pip install -e .

CMD ["mserve", "--app-name", "development", "--server-name", "development", "--logging-config", "development", "--reload", "config.toml.mako"]
