FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
# Download spaCy model
RUN python -m spacy download en_core_web_sm
EXPOSE 5000
CMD ["python", "app.py"]


