FROM python:3.9-alpine as build

# Don't create `.pyc` files:
# ENV POETRY_HOME="/opt/poetry" \
    # POETRY_NO_INTERACTION=1 \
    # POETRY_VERSION=1.2.2
# ENV PATH="$PATH:/root/.local/bin/"

# RUN pip install -f requirements.txt
# RUN pip install -e .
# RUN apk add gcc libffi-dev linux-headers musl-dev
# RUN pipx install poetry==${POETRY_VERSION}


WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# RUN poetry config virtualenvs.create false
# RUN poetry install --no-ansi --no-dev
COPY . .
RUN pip install -e .

# Label the container
LABEL maintainer="Frieder Frank"
LABEL repository="https://github.com/raverank/manki"
LABEL homepage="https://github.com/raverank/manki"

WORKDIR /app/run

CMD [ "manki" ]





  


