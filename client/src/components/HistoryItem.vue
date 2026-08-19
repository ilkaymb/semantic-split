<script setup>
const props = defineProps({
  entry: { type: Object, required: true },
  groupLabel: { type: String, default: "Grup" },
  notFoundLabel: { type: String, default: "Bulunamadı" },
});

function toneClass(opId, label) {
  const l = (label || "").toLowerCase();
  if (opId === "sentiment") {
    if (l.includes("pos")) return "tone-positive";
    if (l.includes("neg")) return "tone-negative";
    return "tone-neutral";
  }
  if (opId === "toxicity") {
    if (l === "toxic") return "tone-negative";
    if (l === "not_toxic") return "tone-positive";
  }
  return "";
}

const cls = toneClass(props.entry.opId, props.entry.data.label);
</script>

<template>
  <article class="history-item">
    <header class="history-head">
      <span class="history-op">{{ entry.opLabel }}<span v-if="entry.modelName" class="history-model"> · {{ entry.modelName }}</span></span>
      <span class="history-time">{{ entry.time }}</span>
    </header>
    <p class="history-snippet">{{ entry.snippet }}</p>

    <div v-if="entry.data.type === 'split'" class="split-groups">
      <div v-for="(sentences, i) in entry.data.clusters" :key="i" class="group-block">
        <span class="group-index">{{ groupLabel }} {{ i + 1 }}</span>
        <p v-for="(s, j) in sentences" :key="j">{{ s }}</p>
      </div>
    </div>

    <div v-else-if="entry.data.type === 'score'" class="score-row">
      <span class="badge-lg" :class="cls">{{ entry.data.label }}</span>
      <span class="score-value">%{{ Math.round(entry.data.score * 100) }}</span>
    </div>

    <p v-else-if="entry.data.type === 'text'" class="text-result">{{ entry.data.text }}</p>

    <div v-else-if="entry.data.type === 'chips'" class="chip-result">
      <span v-for="(kw, i) in entry.data.list" :key="i" class="chip" :title="kw.type">{{ kw.text }}</span>
      <span v-if="!entry.data.list.length" class="empty-note">{{ notFoundLabel }}</span>
    </div>
  </article>
</template>

<style scoped>
.history-item {
  padding: 16px 0;
  border-top: 1px solid var(--panel-border);
}

.history-item:first-child {
  border-top: none;
  padding-top: 0;
}

.history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.history-op {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--accent-2);
}

.history-model {
  color: var(--faint);
  font-weight: 600;
}

.history-time {
  font-size: 11px;
  color: var(--faint);
}

.history-snippet {
  margin: 0 0 12px;
  font-size: 0.82rem;
  color: var(--faint);
  line-height: 1.4;
}

.split-groups {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.group-block .group-index {
  display: block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--accent-2);
  margin-bottom: 6px;
}

.group-block p {
  margin: 0 0 4px;
  font-size: 0.88rem;
  color: var(--text-dim);
  line-height: 1.5;
}

.group-block p:last-child {
  margin-bottom: 0;
}

.score-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.badge-lg {
  padding: 6px 16px;
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  font-weight: 700;
  background: transparent;
  border: 1px solid var(--accent-2);
  color: var(--accent-2);
}

.tone-positive {
  border-color: var(--positive);
  color: var(--positive);
}

.tone-negative {
  border-color: var(--negative);
  color: var(--negative);
}

.tone-neutral {
  border-color: var(--neutral);
  color: var(--neutral);
}

.score-value {
  font-size: 0.85rem;
  color: var(--faint);
}

.text-result {
  margin: 0;
  font-size: 0.94rem;
  line-height: 1.6;
  color: var(--text-dim);
  font-style: italic;
}

.chip-result {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  background: transparent;
  border: 1px solid var(--panel-border);
  color: var(--text-dim);
  border-radius: var(--radius-sm);
  padding: 5px 11px;
  font-size: 0.85rem;
}

.empty-note {
  font-size: 0.85rem;
  color: var(--faint);
}
</style>
