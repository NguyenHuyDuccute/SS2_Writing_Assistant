import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/grammar-check", methods=['GET', 'POST'])
def check_grammar():
    if request.method == "POST":
        input_text = request.form['text']
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Correct this to standard English:\n\n{input_text}.",
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        corrected_text = response.choices[0].text.strip()
        return render_template('grammar_check.html', corrected_text=corrected_text)
    return render_template('grammar_check.html')


@app.route("/grammar-check-post", methods=['POST'])
def test():
    input_text = request.form['text']
    return input_text


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        paraphrase = request.form["paraphrase"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(paraphrase),
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(paraphrase):
    prompt_dict = {
        "Hulu has a big user base.": "Hulu commands a sizeable market.",
        "Milk is good for your bones.": "Milk strengthens one’s bones.",
        "GMOs are seen as bad, but that’s not accurate.": "GMOs command a negative reputation, but this sentiment is "
                                                          "inaccurate."
    }
    rewrite = prompt_dict.get(paraphrase)
    if not rewrite:
        return None
    keywords = {
        "Hulu commands a sizeable market.": ["wields", "reach"],
        "Milk strengthens one’s bones.": ["documented", "bolster"],
        "GMOs command a negative reputation, but this sentiment is inaccurate.": ["tainted", "inaccurate"]
    }
    prompt = f"Rewrite: (Keywords: {', '.join(keywords[paraphrase])}) {rewrite} "
    return prompt
