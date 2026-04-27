# Python image and utils
FROM python:3.11-slim

# Make sure that the print works and it is not buffered
ENV PYTHONUNBUFFERED=1

# Set working dir and install requirements
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

ENV TRANSFORMERS_OFFLINE=1

# Make sure to run the programm
CMD ["python", "solution.py"]