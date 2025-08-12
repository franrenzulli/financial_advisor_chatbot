# Use a Python base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ingestion directory into the container
COPY . .

# Command to run the ingestion script
CMD ["python", "process_s3_documents.py"]
