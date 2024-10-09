# Use the official Python 2.7 image from Docker Hub
FROM python:2.7-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port your app runs on (change if necessary)
EXPOSE 5000

# Define the command to run your application
CMD ["python", "app.py"]
