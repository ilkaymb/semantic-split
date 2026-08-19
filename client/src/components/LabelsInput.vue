<script setup>
import { computed } from "vue";

const props = defineProps({
  modelValue: String,
  label: { type: String, default: "Sınıflandırma etiketleri" },
  placeholder: { type: String, default: "spor, teknoloji, siyaset…" },
});
defineEmits(["update:modelValue"]);

const parsedLabels = computed(() =>
  (props.modelValue || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
);
</script>

<template>
  <div class="labels-input">
    <label for="labels">{{ label }}</label>
    <input
      id="labels"
      type="text"
      :placeholder="placeholder"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <div v-if="parsedLabels.length" class="preview">
      <span v-for="label in parsedLabels" :key="label" class="preview-chip">{{ label }}</span>
    </div>
  </div>
</template>

<style scoped>
.labels-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-dim);
}

input {
  width: 100%;
  padding: 11px 13px;
  background: #0b0c10;
  color: var(--text);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-family: var(--font-body);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

input::placeholder {
  color: var(--faint);
}

input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(124, 107, 255, 0.25);
}

.preview {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.preview-chip {
  font-size: 11.5px;
  padding: 3px 9px;
  border-radius: 4px;
  background: transparent;
  color: var(--accent-2);
  border: 1px solid var(--panel-border);
}
</style>
