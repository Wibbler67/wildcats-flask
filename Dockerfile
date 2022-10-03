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
# Run this on the container start for testing

RUN  ["flask", "--app", "flask-app", "init-db"]
CMD ["flask", "--app", "flask-app", "run", "--host=0.0.0.0"]