FROM python:3.9-alpine

# RUN adduser -D mankiuser
# USER mankiuser
# ENV PATH="/home/mankiuser/.local/bin:${PATH}"

# WORKDIR /home/mankiuser/app

# COPY --chown=mankiuser:mankiuser requirements.txt .
# RUN chmod -R 777 .
# RUN /usr/local/bin/python -m pip install --upgrade pip
# RUN pip install --user -r requirements.txt

# COPY --chown=mankiuser:mankiuser . .
# RUN pip install --user -e .

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

WORKDIR /run

ENTRYPOINT [ "manki" ]