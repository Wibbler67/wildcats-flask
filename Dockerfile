FROM python

RUN     apt update

# Copy all Files
WORKDIR /flask-app
COPY    . .

# Install all requirements
RUN     pip install -r requirements.txt

# Ports which will need to be installed
EXPOSE  5000

WORKDIR /
# Comment this out if you don't need the db wiped and re-seeded
RUN  ["flask", "--app", "flask-app", "init-db"]

# This will run the app
CMD ["flask", "--app", "flask-app", "run", "--host=0.0.0.0"]