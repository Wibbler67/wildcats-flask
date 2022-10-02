FROM python

# Copy all Files
WORKDIR /flask-app
COPY    . .

# Install all requirements
RUN     pip install -r requirements.txt

# Ports which will need to be installed
EXPOSE  5000

# Run this on the container start
ENTRYPOINT ["python", "__init__.py"]