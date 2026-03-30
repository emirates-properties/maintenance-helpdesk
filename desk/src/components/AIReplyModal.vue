<template>
  <Dialog
    v-model="show"
    :options="{
      size: '4xl',
      title: 'Draft with AI',
    }"
  >
    <template #body-title>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 bg-purple-100 px-3 py-1.5 rounded-lg">
          <LucideSparkles class="h-5 w-5 text-purple-600" />
          <span class="text-xs font-bold text-purple-700 uppercase tracking-wide">AI Powered</span>
        </div>
      </div>
      <h2 class="text-2xl font-semibold text-ink-gray-9 mt-2">{{ __("Draft with AI") }}</h2>
      <p class="text-sm text-ink-gray-6 mt-1">{{ __("Generate AI-powered reply suggestions for this ticket") }}</p>
    </template>
    <template #body>
      <div class="max-h-[600px]" :style="{ height: 'calc(100vh - 8rem)' }">
        <!-- Header with close button -->
        <div class="flex items-center justify-end w-full px-6 pt-4 pb-2">
          <Button
            variant="ghost"
            icon="x"
            @click="show = false"
          />
        </div>

        <!-- Tone Selector & Generate Button -->
        <div class="p-6 pb-4 border-y border-outline-gray-2">
          <div class="flex flex-col gap-4">
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-3">
                {{ __("Select Reply Tone") }}
              </label>
              <div class="flex gap-2 flex-wrap">
                <Button
                  v-for="tone in toneOptions"
                  :key="tone.value"
                  :variant="selectedTone === tone.value ? 'solid' : 'outline'"
                  size="sm"
                  @click="selectedTone = tone.value"
                  class="flex-1 min-w-[120px]"
                >
                  {{ tone.label }}
                </Button>
              </div>
            </div>
            <Button
              variant="solid"
              class="w-full"
              :loading="generateResource.loading"
              :disabled="!ticketId"
              @click="generateSuggestions"
            >
              <template #prefix>
                <LucideSparkles class="size-4" />
              </template>
              {{ generateResource.loading ? __("Generating...") : __("Generate Replies") }}
            </Button>
          </div>
        </div>

        <!-- Content Area -->
        <div class="p-6 overflow-y-auto" :style="{ maxHeight: 'calc(100vh - 24rem)' }">
          <!-- Error State -->
          <div
            v-if="error"
            class="flex flex-col items-center justify-center py-12 px-4"
          >
            <div class="bg-surface-gray-1 rounded-full p-4 mb-4">
              <LucideAlertCircle class="size-8 text-ink-gray-5" />
            </div>
            <p class="text-base font-medium text-ink-gray-8 mb-2">{{ __("Failed to Generate") }}</p>
            <p class="text-sm text-ink-gray-6 text-center mb-4">{{ error }}</p>
            <Button
              variant="outline"
              @click="generateSuggestions"
            >
              {{ __("Try Again") }}
            </Button>
          </div>

          <!-- Empty State -->
          <div
            v-else-if="!suggestions.length && !generateResource.loading"
            class="flex flex-col items-center justify-center py-16 px-4"
          >
            <div class="bg-surface-gray-1 rounded-full p-4 mb-4">
              <LucideSparkles class="size-8 text-ink-gray-5" />
            </div>
            <p class="text-base font-medium text-ink-gray-8 mb-2">{{ __("No suggestions yet") }}</p>
            <p class="text-sm text-ink-gray-6 text-center">{{ __("Select a tone and click 'Generate Replies' to get AI-powered suggestions") }}</p>
          </div>

          <!-- Loading State -->
          <div
            v-else-if="generateResource.loading"
            class="space-y-4"
          >
            <div
              v-for="i in 3"
              :key="i"
              class="border border-outline-gray-2 rounded-lg p-4 bg-surface-white animate-pulse"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="h-4 bg-surface-gray-2 rounded w-24"></div>
                <div class="h-8 bg-surface-gray-2 rounded w-32"></div>
              </div>
              <div class="space-y-2">
                <div class="h-3 bg-surface-gray-2 rounded w-full"></div>
                <div class="h-3 bg-surface-gray-2 rounded w-5/6"></div>
                <div class="h-3 bg-surface-gray-2 rounded w-4/6"></div>
              </div>
            </div>
          </div>

          <!-- Suggestions -->
          <div
            v-else-if="suggestions.length"
            class="space-y-3"
          >
            <div
              v-for="suggestion in suggestions"
              :key="suggestion.id"
              class="border-2 border-outline-gray-2 rounded-lg p-5 bg-surface-white hover:border-outline-gray-4 transition-all duration-200"
            >
              <div class="flex items-start justify-between mb-3 gap-3">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="text-sm font-semibold text-ink-gray-9">
                    {{ __("Suggestion") }} {{ suggestion.id }}
                  </span>
                  <div class="flex items-center gap-1 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                    <LucideSparkles class="h-3 w-3 text-purple-600" />
                    <span class="text-xs font-medium text-purple-700">AI</span>
                  </div>
                  <span class="text-xs text-ink-gray-5 bg-surface-gray-1 px-2 py-0.5 rounded capitalize">{{ suggestion.tone }}</span>
                </div>
                <Button
                  variant="solid"
                  size="sm"
                  @click="selectSuggestion(suggestion)"
                  class="shrink-0"
                >
                  <template #prefix>
                    <LucideCheck class="size-4" />
                  </template>
                  {{ __("Use") }}
                </Button>
              </div>
              <div
                class="text-sm text-ink-gray-8 leading-normal max-h-48 overflow-y-auto border-l-2 border-outline-gray-2 pl-3"
                v-html="formatSuggestionText(suggestion.text)"
              ></div>
            </div>

            <!-- Regenerate Button -->
            <div class="flex flex-col items-center gap-3 pt-6 pb-4 mt-6 border-t-2 border-outline-gray-3 bg-surface-gray-1 rounded-b-lg mx-[-1.5rem] px-6">
              <p class="text-sm text-ink-gray-7 font-medium">Don't like these suggestions?</p>
              <Button
                variant="solid"
                @click="generateSuggestions"
                :loading="generateResource.loading"
                class="w-full max-w-md"
              >
                <template #prefix>
                  <LucideRefreshCw class="size-5" />
                </template>
                <span class="font-semibold">{{ generateResource.loading ? __("Generating...") : __("Generate 3 New Suggestions") }}</span>
              </Button>
              <p class="text-xs text-ink-gray-5">Click to get completely different reply options</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { Dialog, Button, createResource } from "frappe-ui";
import LucideSparkles from "~icons/lucide/sparkles";
import LucideCheck from "~icons/lucide/check";
import LucideRefreshCw from "~icons/lucide/refresh-cw";
import LucideAlertCircle from "~icons/lucide/alert-circle";

interface Suggestion {
  id: number;
  text: string;
  tone: string;
}

interface Props {
  modelValue: boolean;
  ticketId: string;
}

interface Emits {
  (e: "update:modelValue", value: boolean): void;
  (e: "select", suggestion: Suggestion): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

// Tone options
const toneOptions = [
  { label: "Professional", value: "professional" },
  { label: "Friendly", value: "friendly" },
  { label: "Concise", value: "concise" },
  { label: "Detailed", value: "detailed" },
];

const selectedTone = ref("professional");
const suggestions = ref<Suggestion[]>([]);
const error = ref<string | null>(null);

// API resource for generating suggestions
const generateResource = createResource({
  url: "helpdesk.api.ai_reply.generate_reply_suggestions",
  onSuccess(data: any) {
    if (data.success && data.suggestions) {
      suggestions.value = data.suggestions;
      error.value = null;
    } else {
      error.value = "Failed to generate suggestions. Please try again.";
    }
  },
  onError(err: any) {
    console.error("AI Reply Generation Error:", err);
    error.value = err.messages?.[0] || err.message || "An error occurred while generating suggestions.";
    suggestions.value = [];
  },
});

// Generate suggestions
function generateSuggestions() {
  if (!props.ticketId) return;
  
  error.value = null;
  generateResource.submit({
    ticket_id: props.ticketId,
    tone: selectedTone.value,
  });
}

// Select a suggestion
function selectSuggestion(suggestion: Suggestion) {
  emit("select", suggestion);
  show.value = false;
}

// Format suggestion text to preserve line breaks
function formatSuggestionText(text: string): string {
  return text.replace(/\n\n/g, "</p><p>").replace(/\n/g, "<br>");
}

// Reset state when modal closes
watch(show, (newValue) => {
  if (!newValue) {
    // Don't reset immediately to allow animation
    setTimeout(() => {
      if (!show.value) {
        suggestions.value = [];
        error.value = null;
      }
    }, 300);
  }
});

// Auto-generate on first open if ticket is available
watch(() => props.modelValue, (newValue) => {
  if (newValue && props.ticketId && !suggestions.value.length && !error.value) {
    // Auto-generate with professional tone on first open
    setTimeout(() => {
      generateSuggestions();
    }, 300);
  }
});
</script>
