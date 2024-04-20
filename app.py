import math
import pickle
from flask import Flask, render_template, request, jsonify
from definations import *
from heapq import nlargest

# Loded Text Recognizer model
with open('model.pkl', 'rb') as f:
    cv_loaded, clf_loaded = pickle.load(f)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/submit", methods=["GET", "POST"])
def process_text():
    if request.method == "POST":
        operation = request.form['operation']
        text = request.form['text']
        cleaned_text = clean(text)
        # print(cleaned_text)
        if operation == 'recognize':
            
            # Transform the input text using the loaded CountVectorizer
            text_transformed = cv_loaded.transform([cleaned_text]).toarray()
            # Predict using the loaded classifier
            prediction = clf_loaded.predict(text_transformed)
            result = ''
            if prediction[0][0]==1:
                result= "Hatred speech"
            elif prediction[0][1]==1:
                result= "Offensive speech"
            else:
                result= "Neutral speech"
        
        else:
            # Create an instance of Summarize with cleaned text
            summarizer = Summarize(cleaned_text)
            sent_score = summarizer.summarize_text()
            num_lines = math.ceil(len(sent_score) * 0.3)
            result = nlargest(n=num_lines, iterable=sent_score, key=sent_score.get)
            result = [sent.text for sent in result]  # Extract text from Span objects

        return jsonify({'operation': operation, 'result': result})
if __name__ == "__main__":
    app.run(debug=True)