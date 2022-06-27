FROM python:3

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code

RUN python -m unittest discover

CMD ["python","Cool_Pouch_Identifier.py"]
