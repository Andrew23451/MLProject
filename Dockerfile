# Python image and utils
FROM python:3.11-slim

# Make sure that the print works and it is not buffered
ENV PYTHONUNBUFFERED=1

# Set working dir and install requirements
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of code
COPY ./ ./

# Build embeddings once during the image build and never again at runtime
RUN python -c "from utils.data_parsing import df; import embedding.transformers as emb; emb.build_and_save(df)"

# Make sure to run the programm
CMD ["python", "solution.py"]