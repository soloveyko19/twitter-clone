FROM python:3.10

COPY ./requirements/requirements-prod.txt /site/requirements.txt
COPY ./src /site

WORKDIR /site
ENV PYTHONPATH=/site

RUN pip install -r requirements.txt

CMD python -m alembic upgrade head && \
    python database/create_test_users.py && \
    uvicorn asgi:app --host "0.0.0.0" --port 8080
