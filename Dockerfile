FROM python:3.8.3-slim

# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH

# set work directory
WORKDIR /usr/src/app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHON_VERSION 3.11.3

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt


COPY ./src/csv_to_json.py /usr/src/app/csv_to_json.py
RUN ls -lrt

# copy project
COPY . /usr/src/app/

# run entrypoint.sh
#ENTRYPOINT ["python3"]

CMD [ "python", "/usr/src/app/csv_to_json.py", "test"]