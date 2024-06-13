FROM python:3.12.2-slim-bookworm

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /backend
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app


# Run main.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]


