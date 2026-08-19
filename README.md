# semantic-split

A small Vue 3 + Django playground for text analysis. Paste a paragraph and run it through seven different NLP operations, each powered by a Hugging Face model (except semantic splitting, which runs entirely locally). Several operations let you switch between two different models on the same text and compare results side by side.

## Features

- **Semantic Split** — groups sentences by meaning using `sentence-transformers` + spaCy, fully local (no external API call).
- **Category Classification** — zero-shot classification with user-defined labels (`facebook/bart-large-mnli` or `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`).
- **Sentiment Analysis** — 3-class positive/neutral/negative, or 1-5 star rating (`cardiffnlp/twitter-xlm-roberta-base-sentiment` or `nlptown/bert-base-multilingual-uncased-sentiment`).
- **Summarization** — multilingual or English-tuned (`csebuetnlp/mT5_multilingual_XLSum` or `facebook/bart-large-cnn`).
- **Keywords** — named-entity extraction in Turkish or English (`savasy/bert-base-turkish-ner-cased` or `dslim/bert-base-NER`).
- **Language Detection** — `papluca/xlm-roberta-base-language-detection`.
- **Toxicity Detection** — multilingual or a more detailed English model (`citizenlab/distilbert-base-multilingual-cased-toxicity` or `unitary/toxic-bert`).

Other bits: a bilingual UI (Turkish/English, auto-detected from the browser, manually toggleable), quick-fill example texts, and a scrollable run history so you can compare results across operations and models without losing earlier runs.

## Stack

- **Frontend**: Vue 3, Vite, plain CSS (no UI framework)
- **Backend**: Django, calling the Hugging Face Inference API over HTTP
- **Split logic**: [`semantic-split`](https://github.com/agamm/semantic-split) (SentenceTransformers + spaCy), the original idea this project is built around

## Running locally

You'll need a free [Hugging Face access token](https://huggingface.co/settings/tokens) (fine-grained, with "Make calls to Inference Providers" permission).

### Backend

```bash
cd server
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
python -m spacy download en_core_web_sm

cd backend
cp .env.example .env          # then edit .env and add your HUGGINGFACE_API_TOKEN
python manage.py runserver
```

### Frontend

```bash
cd client
npm install
npm run dev
```

Open `http://localhost:5173`. The backend is expected at `http://127.0.0.1:8000`.

## Notes

- The semantic-split step is language-agnostic in principle but currently uses an English spaCy sentence splitter (`en_core_web_sm`), so sentence boundaries on non-English text may be imperfect.
- Free-tier Hugging Face Inference API calls can have a cold-start delay (a few seconds to ~20s) on the first request to a given model.

---

Developed by [İlkay Bora](https://ilkaybora.com)
