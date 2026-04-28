# Python image and utils
FROM python:3.11-slim

# Make sure that the print works and it is not buffered
ENV PYTHONUNBUFFERED=1

# Set working dir and install requirements
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Load the sentence_transformers at the build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Don't want to contact HuggingFace at runtime
ENV TRANSFORMERS_OFFLINE=1

# Make sure to run the programm
CMD ["python", "solution.py"]