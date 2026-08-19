<script setup>
import { ref, computed, watch } from "vue";
import { splitText, classify, sentiment, summarize, keywords, detectLanguage, detectToxicity } from "./api";
import LabelsInput from "./components/LabelsInput.vue";
import HistoryItem from "./components/HistoryItem.vue";

const STRINGS = {
  tr: {
    textLabel: "Metin",
    textPlaceholder: "Metni buraya yapıştır…",
    examplesLabel: "Örnek",
    labelsLabel: "Sınıflandırma etiketleri",
    labelsPlaceholder: "spor, teknoloji, siyaset…",
    resultPlaceholder: "Sonuç burada görünecek",
    running: "Çalışıyor…",
    notFound: "Bulunamadı",
    modelLabel: "Model",
    group: "Grup",
    footer: "Developed by İlkay Bora",
  },
  en: {
    textLabel: "Text",
    textPlaceholder: "Paste your text here…",
    examplesLabel: "Example",
    labelsLabel: "Classification labels",
    labelsPlaceholder: "sports, tech, politics…",
    resultPlaceholder: "Result will appear here",
    running: "Running…",
    notFound: "Not found",
    modelLabel: "Model",
    group: "Group",
    footer: "Developed by İlkay Bora",
  },
};

const OPERATIONS = [
  {
    id: "split",
    label: { tr: "Anlamsal Ayırma", en: "Semantic Split" },
    verb: { tr: "Ayır", en: "Split" },
    models: [
      {
        id: "local",
        name: { tr: "SentenceTransformers + spaCy", en: "SentenceTransformers + spaCy" },
        note: {
          tr: "Lokal çalışır, harici API kullanmaz. Cümleleri anlamca benzerliğine göre gruplar.",
          en: "Runs locally, no external API. Groups sentences by semantic similarity.",
        },
      },
    ],
  },
  {
    id: "classify",
    label: { tr: "Kategori Sınıflandırma", en: "Category Classification" },
    verb: { tr: "Sınıflandır", en: "Classify" },
    models: [
      {
        id: "facebook/bart-large-mnli",
        name: { tr: "BART", en: "BART" },
        note: {
          tr: "İngilizce ağırlıklı sıfır atışlı sınıflandırma.",
          en: "English-centric zero-shot classification.",
        },
      },
      {
        id: "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
        name: { tr: "mDeBERTa", en: "mDeBERTa" },
        note: {
          tr: "Çok dilli, Türkçede genelde daha güçlü sonuçlar verir.",
          en: "Multilingual, often performs better on Turkish text.",
        },
      },
    ],
  },
  {
    id: "sentiment",
    label: { tr: "Duygu Analizi", en: "Sentiment Analysis" },
    verb: { tr: "Analiz Et", en: "Analyze" },
    models: [
      {
        id: "cardiffnlp/twitter-xlm-roberta-base-sentiment",
        name: { tr: "3 Sınıf", en: "3-Class" },
        note: {
          tr: "Pozitif / nötr / negatif olarak etiketler. Türkçeyi destekler.",
          en: "Labels as positive / neutral / negative. Supports Turkish.",
        },
      },
      {
        id: "nlptown/bert-base-multilingual-uncased-sentiment",
        name: { tr: "5 Yıldız", en: "5-Star" },
        note: {
          tr: "1-5 yıldız arasında puanlar (ürün yorumu tarzı).",
          en: "Rates from 1-5 stars (review-style).",
        },
      },
    ],
  },
  {
    id: "summarize",
    label: { tr: "Özetleme", en: "Summarization" },
    verb: { tr: "Özetle", en: "Summarize" },
    models: [
      {
        id: "csebuetnlp/mT5_multilingual_XLSum",
        name: { tr: "Çok Dilli", en: "Multilingual" },
        note: {
          tr: "45 dilde eğitildi, Türkçe metinlerde de kullanılabilir.",
          en: "Trained on 45 languages, usable on Turkish text too.",
        },
      },
      {
        id: "facebook/bart-large-cnn",
        name: { tr: "İngilizce", en: "English" },
        note: {
          tr: "Sadece İngilizce metinlerde iyi sonuç verir.",
          en: "Performs well only on English text.",
        },
      },
    ],
  },
  {
    id: "keywords",
    label: { tr: "Anahtar Kelime", en: "Keywords" },
    verb: { tr: "Çıkar", en: "Extract" },
    models: [
      {
        id: "savasy/bert-base-turkish-ner-cased",
        name: { tr: "Türkçe", en: "Turkish" },
        note: {
          tr: "Türkçe varlık ismi tanıma. Gerçek anahtar kelime değil, kişi/yer/kurum adı bulur.",
          en: "Turkish NER. Not true keywords — finds person/place/org names.",
        },
      },
      {
        id: "dslim/bert-base-NER",
        name: { tr: "İngilizce", en: "English" },
        note: {
          tr: "İngilizce varlık ismi tanıma modeli.",
          en: "English named-entity recognition model.",
        },
      },
    ],
  },
  {
    id: "language",
    label: { tr: "Dil Tespiti", en: "Language Detection" },
    verb: { tr: "Tespit Et", en: "Detect" },
    models: [
      {
        id: "papluca/xlm-roberta-base-language-detection",
        name: { tr: "XLM-RoBERTa", en: "XLM-RoBERTa" },
        note: {
          tr: "20 dili ayırt edebilen çok dilli bir sınıflandırma modeli.",
          en: "A multilingual classifier that distinguishes 20 languages.",
        },
      },
    ],
  },
  {
    id: "toxicity",
    label: { tr: "Toksisite Tespiti", en: "Toxicity Detection" },
    verb: { tr: "Tara", en: "Scan" },
    models: [
      {
        id: "citizenlab/distilbert-base-multilingual-cased-toxicity",
        name: { tr: "Çok Dilli", en: "Multilingual" },
        note: {
          tr: "Çok dilli, toksik/değil şeklinde ikili etiketler.",
          en: "Multilingual, binary toxic / not-toxic labeling.",
        },
      },
      {
        id: "unitary/toxic-bert",
        name: { tr: "İngilizce (Detaylı)", en: "English (Detailed)" },
        note: {
          tr: "İngilizce, hakaret/müstehcenlik gibi alt kategorilere ayırır.",
          en: "English, breaks results into subcategories like insult/obscene.",
        },
      },
    ],
  },
];

const EXAMPLES = [
  {
    id: "tech",
    label: { tr: "Teknoloji", en: "Technology" },
    tr: "Türkiye'nin yapay zeka alanındaki yatırımları son yıllarda hızla arttı. İstanbul merkezli bir teknoloji şirketi, geliştirdiği yeni yapay zeka modeliyle uluslararası bir ödül kazandı. Şirketin kurucusu Mehmet Yılmaz, bu başarının Türk teknoloji sektörü için önemli bir dönüm noktası olduğunu belirtti. Uzmanlar, bu tür gelişmelerin ülke ekonomisine katkı sağlayacağını düşünüyor.",
    en: "Turkey's investments in artificial intelligence have grown rapidly in recent years. An Istanbul-based tech company won an international award for its new AI model. The company's founder, Mehmet Yılmaz, said this achievement marks an important milestone for the Turkish tech sector. Experts believe such developments will make a significant contribution to the country's economy.",
  },
  {
    id: "sports",
    label: { tr: "Spor", en: "Sports" },
    tr: "Fenerbahçe, deplasmanda oynadığı kritik maçı 3-1 kazanarak zirve yarışında iddiasını sürdürdü. Teknik direktör Ali Koç, oyuncuların sahada gösterdiği mücadeleden çok memnun olduğunu söyledi. Milli futbolcu Arda Güler attığı iki golle karşılaşmanın yıldızı oldu. Taraftarlar, sezon sonunda şampiyonluk hedefine daha da yaklaştıklarını düşünüyor.",
    en: "Fenerbahçe kept their title challenge alive by winning a crucial away match 3-1. Head coach Ali Koç said he was very pleased with the players' effort on the pitch. National team player Arda Güler was the star of the match, scoring two goals. Fans believe the team is now even closer to their championship goal.",
  },
  {
    id: "health",
    label: { tr: "Sağlık", en: "Health" },
    tr: "Sağlık Bakanlığı, kış aylarında artan grip vakalarına karşı vatandaşları aşı olmaya çağırdı. Uzmanlar, düzenli el yıkama ve maske kullanımının bulaşı azaltmada etkili olduğunu belirtti. Hacettepe Üniversitesi'nden Dr. Ayşe Demir, özellikle yaşlı ve kronik hastaların risk grubunda olduğunu vurguladı. Yetkililer, hastanelerde yeterli kapasite bulunduğunu ve endişeye gerek olmadığını açıkladı.",
    en: "The Ministry of Health urged citizens to get vaccinated against the rising number of flu cases this winter. Experts said regular handwashing and mask use are effective in reducing transmission. Dr. Ayşe Demir from Hacettepe University emphasized that elderly people and those with chronic illnesses are at higher risk. Officials stated that hospitals have sufficient capacity and there is no cause for concern.",
  },
];

const DEFAULT_LABELS = {
  tr: "spor, teknoloji, siyaset, ekonomi, sağlık, kültür-sanat, magazin",
  en: "sports, technology, politics, economy, health, culture-arts, entertainment",
};

function detectBrowserLang() {
  const raw = (navigator.language || navigator.languages?.[0] || "en").toLowerCase();
  return raw.startsWith("tr") ? "tr" : "en";
}

const lang = ref(detectBrowserLang());
const t = computed(() => STRINGS[lang.value]);

const selectedId = ref("split");
const selectedOp = computed(() => OPERATIONS.find((o) => o.id === selectedId.value));

const selectedModelId = ref(OPERATIONS[0].models[0].id);
const currentModel = computed(
  () => selectedOp.value.models.find((m) => m.id === selectedModelId.value) || selectedOp.value.models[0]
);

const activeExampleId = ref("tech");
const input = ref(EXAMPLES.find((e) => e.id === "tech")[lang.value]);
const labelsInput = ref(DEFAULT_LABELS[lang.value]);
const textEdited = ref(false);
const labelsEdited = ref(false);

function selectExample(id) {
  activeExampleId.value = id;
  textEdited.value = false;
  input.value = EXAMPLES.find((e) => e.id === id)[lang.value];
}

watch(lang, (newLang) => {
  if (!textEdited.value) input.value = EXAMPLES.find((e) => e.id === activeExampleId.value)[newLang];
  if (!labelsEdited.value) labelsInput.value = DEFAULT_LABELS[newLang];
});

const loading = ref(false);
const error = ref("");
const history = ref([]);

function selectOp(id) {
  if (loading.value) return;
  selectedId.value = id;
  selectedModelId.value = OPERATIONS.find((o) => o.id === id).models[0].id;
  error.value = "";
}

async function handleRun() {
  error.value = "";
  loading.value = true;
  try {
    const op = selectedId.value;
    const modelId = selectedModelId.value;
    let data;
    if (op === "split") {
      const res = await splitText(input.value);
      data = { type: "split", clusters: res.message || [] };
    } else if (op === "classify") {
      const labels = labelsInput.value.split(",").map((s) => s.trim()).filter(Boolean);
      data = { type: "score", ...readItem(await classify([input.value], labels, modelId)) };
    } else if (op === "sentiment") {
      data = { type: "score", ...readItem(await sentiment([input.value], modelId)) };
    } else if (op === "summarize") {
      data = { type: "text", text: readItem(await summarize([input.value], modelId), "summary").value };
    } else if (op === "keywords") {
      data = { type: "chips", list: readItem(await keywords([input.value], modelId), "keywords").value || [] };
    } else if (op === "language") {
      data = { type: "score", ...readItem(await detectLanguage([input.value], modelId)) };
    } else if (op === "toxicity") {
      data = { type: "score", ...readItem(await detectToxicity([input.value], modelId)) };
    }

    history.value.unshift({
      id: Date.now() + Math.random(),
      opId: op,
      opLabel: selectedOp.value.label[lang.value],
      modelName: currentModel.value.name[lang.value],
      snippet: input.value.length > 90 ? input.value.slice(0, 90) + "…" : input.value,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      data,
    });
    if (history.value.length > 12) history.value.pop();
  } catch (err) {
    error.value = err.message || "Bir hata oluştu.";
  } finally {
    loading.value = false;
  }
}

function readItem(data, valueKey) {
  const item = (data.results || [])[0];
  if (!item) throw new Error("Boş yanıt");
  if (item.error) throw new Error(item.error);
  if (valueKey) return { value: item[valueKey] };
  return { label: item.label, score: item.score };
}
</script>

<template>
  <div class="page">
    <header class="header">
      <div class="brand">
        <span class="logo-mark">§</span>
        <h1>semantic-split</h1>
      </div>
      <div class="lang-toggle">
        <button type="button" :class="{ active: lang === 'tr' }" @click="lang = 'tr'">TR</button>
        <span class="lang-sep">/</span>
        <button type="button" :class="{ active: lang === 'en' }" @click="lang = 'en'">EN</button>
      </div>
    </header>

    <main class="content">
      <section class="col col-ops">
        <nav class="op-list">
          <button
            v-for="op in OPERATIONS"
            :key="op.id"
            type="button"
            class="op-btn"
            :class="{ active: op.id === selectedId }"
            :disabled="loading"
            @click="selectOp(op.id)"
          >
            {{ op.label[lang] }}
          </button>
        </nav>

        <div class="model-info">
          <span class="model-info-label">{{ t.modelLabel }}</span>

          <div v-if="selectedOp.models.length > 1" class="model-options">
            <button
              v-for="m in selectedOp.models"
              :key="m.id"
              type="button"
              class="model-option"
              :class="{ active: m.id === selectedModelId }"
              :disabled="loading"
              @click="selectedModelId = m.id"
            >
              {{ m.name[lang] }}
            </button>
          </div>
          <p v-else class="model-name">{{ currentModel.name[lang] }}</p>

          <p v-if="currentModel.id !== 'local'" class="model-id">{{ currentModel.id }}</p>
          <p class="model-note">{{ currentModel.note[lang] }}</p>
        </div>
      </section>

      <section class="col col-input">
        <label for="text">{{ t.textLabel }}</label>

        <div class="examples-row">
          <span class="examples-label">{{ t.examplesLabel }}:</span>
          <button
            v-for="ex in EXAMPLES"
            :key="ex.id"
            type="button"
            class="example-chip"
            :class="{ active: ex.id === activeExampleId }"
            @click="selectExample(ex.id)"
          >
            {{ ex.label[lang] }}
          </button>
        </div>

        <textarea
          id="text"
          v-model="input"
          rows="10"
          :placeholder="t.textPlaceholder"
          @input="textEdited = true"
        ></textarea>

        <LabelsInput
          v-if="selectedId === 'classify'"
          v-model="labelsInput"
          :label="t.labelsLabel"
          :placeholder="t.labelsPlaceholder"
          @input="labelsEdited = true"
        />

        <button type="button" class="run-btn" :disabled="loading" @click="handleRun">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? t.running : selectedOp.verb[lang] }}
        </button>
      </section>

      <section class="col col-result">
        <div v-if="loading" class="inline-status">
          <span class="spinner"></span> {{ t.running }}
        </div>
        <div v-else-if="error" class="inline-status error">{{ error }}</div>

        <div v-if="history.length" class="history-scroll">
          <div class="history-list">
            <HistoryItem
              v-for="entry in history"
              :key="entry.id"
              :entry="entry"
              :group-label="t.group"
              :not-found-label="t.notFound"
            />
          </div>
        </div>
        <div v-else-if="!loading && !error" class="state-msg muted">{{ t.resultPlaceholder }}</div>
      </section>
    </main>

    <footer class="footer">
      <a href="https://ilkaybora.com" target="_blank" rel="noopener noreferrer">{{ t.footer }}</a>
    </footer>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--panel-border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-mark {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.header h1 {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.lang-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
}

.lang-toggle button {
  background: none;
  border: none;
  padding: 2px;
  font-family: var(--font-body);
  font-size: 12.5px;
  font-weight: 600;
  color: var(--faint);
  cursor: pointer;
}

.lang-toggle button.active {
  color: var(--accent-2);
}

.lang-sep {
  color: var(--panel-border);
}

.content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 220px 1fr 1fr;
  gap: 0;
  align-items: start;
}

@media (max-width: 900px) {
  .content {
    grid-template-columns: 1fr;
  }
  .col {
    border-right: none !important;
    border-bottom: 1px solid var(--panel-border);
    padding: 20px 0 !important;
  }
}

.col {
  padding: 0 28px;
}

.col-ops {
  border-right: 1px solid var(--panel-border);
  padding-left: 0;
}

.col-input {
  border-right: 1px solid var(--panel-border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.col-result {
  min-height: 360px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.op-list {
  display: flex;
  flex-direction: column;
}

.op-btn {
  text-align: left;
  padding: 9px 2px 9px 12px;
  margin-bottom: 2px;
  font-family: var(--font-body);
  font-size: 0.87rem;
  font-weight: 500;
  color: var(--text-dim);
  background: transparent;
  border: none;
  border-left: 2px solid transparent;
  cursor: pointer;
  transition: color 0.12s ease, border-color 0.12s ease;
}

.op-btn:hover:not(:disabled) {
  color: var(--text);
}

.op-btn.active {
  color: var(--accent-2);
  border-left-color: var(--accent);
  font-weight: 600;
}

.op-btn:disabled {
  cursor: default;
  opacity: 0.6;
}

.model-info {
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px solid var(--panel-border);
}

.model-info-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--faint);
}

.model-name {
  margin: 6px 0 4px;
  font-size: 0.83rem;
  font-weight: 600;
  color: var(--accent-2);
  word-break: break-word;
}

.model-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0 6px;
}

.model-option {
  font-family: var(--font-body);
  font-size: 0.76rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 999px;
  background: transparent;
  border: 1px solid var(--panel-border);
  color: var(--faint);
  cursor: pointer;
  transition: color 0.12s ease, border-color 0.12s ease;
}

.model-option:hover:not(:disabled) {
  color: var(--text-dim);
}

.model-option.active {
  color: var(--accent-2);
  border-color: var(--accent-2);
}

.model-option:disabled {
  cursor: default;
  opacity: 0.6;
}

.model-id {
  margin: 0 0 6px;
  font-size: 0.72rem;
  color: var(--faint);
  word-break: break-word;
}

.model-note {
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--faint);
}

label {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-dim);
}

.examples-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.examples-label {
  font-size: 11.5px;
  color: var(--faint);
  margin-right: 2px;
}

.example-chip {
  font-family: var(--font-body);
  font-size: 11.5px;
  padding: 3px 10px;
  border-radius: 999px;
  background: transparent;
  border: 1px solid var(--panel-border);
  color: var(--faint);
  cursor: pointer;
  transition: color 0.12s ease, border-color 0.12s ease;
}

.example-chip:hover {
  color: var(--text-dim);
}

.example-chip.active {
  color: var(--accent-2);
  border-color: var(--accent-2);
}

textarea {
  width: 100%;
  padding: 12px 13px;
  font-size: 0.92rem;
  font-family: var(--font-body);
  line-height: 1.5;
  background: #0b0c10;
  color: var(--text);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-sm);
  resize: vertical;
}

textarea::placeholder {
  color: var(--faint);
}

textarea:focus,
.run-btn:focus-visible {
  outline: none;
  border-color: var(--accent);
}

.run-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 16px;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 0.9rem;
  color: #fff;
  background: var(--accent);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color 0.12s ease;
}

.run-btn:hover:not(:disabled) {
  background-color: #6a58f5;
}

.run-btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.inline-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--faint);
}

.inline-status .spinner {
  border-color: var(--panel-border);
  border-top-color: var(--accent-2);
}

.inline-status.error {
  color: var(--negative);
}

.state-msg {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  font-size: 0.88rem;
  color: var(--faint);
}

.history-scroll {
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  padding-right: 6px;
  scrollbar-color: var(--panel-border) transparent;
}

.history-scroll::-webkit-scrollbar {
  width: 8px;
}

.history-scroll::-webkit-scrollbar-thumb {
  background: var(--panel-border);
  border-radius: 4px;
}

.history-list {
  display: flex;
  flex-direction: column;
}

.footer {
  padding: 18px 24px;
  text-align: center;
  border-top: 1px solid var(--panel-border);
}

.footer a {
  color: var(--faint);
  font-size: 0.8rem;
  text-decoration: none;
}

.footer a:hover {
  color: var(--accent-2);
}
</style>
