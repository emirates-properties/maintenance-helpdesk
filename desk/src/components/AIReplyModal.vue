<template>
  <!-- Right Side Panel Overlay -->
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-stretch justify-end"
      @click.self="show = false"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/20"></div>

      <!-- Side Panel -->
      <Transition
        enter-active-class="transition-transform duration-300 ease-out"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition-transform duration-200 ease-in"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <div
          v-if="show"
          class="relative w-full max-w-xl bg-white shadow-2xl flex flex-col h-full"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-outline-gray-2">
            <div class="flex items-center gap-3">
              <div class="flex items-center gap-2 bg-purple-100 px-3 py-1.5 rounded-lg">
                <LucideSparkles class="h-4 w-4 text-purple-600" />
                <span class="text-xs font-semibold text-purple-700 uppercase tracking-wide">AI Copilot</span>
              </div>
            </div>
            <button
              @click="show = false"
              class="p-2 hover:bg-surface-gray-1 rounded-lg transition-colors"
            >
              <LucideX class="size-5 text-ink-gray-6" />
            </button>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto">
            <!-- Tone Selector -->
            <div class="px-6 py-5 border-b border-outline-gray-2">
              <label class="block text-sm font-medium text-ink-gray-8 mb-3">
                {{ __("Select Reply Tone") }}
              </label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="tone in toneOptions"
                  :key="tone.value"
                  @click="selectedTone = tone.value"
                  :class="[
                    'px-4 py-2.5 rounded-lg text-sm font-medium transition-all',
                    selectedTone === tone.value
                      ? 'bg-black text-white shadow-sm'
                      : 'bg-surface-gray-1 text-ink-gray-7 hover:bg-surface-gray-2'
                  ]"
                >
                  {{ tone.label }}
                </button>
              </div>
            </div>

            <!-- User Input -->
            <div class="px-6 py-5 border-b border-outline-gray-2">
              <label class="block text-sm font-medium text-ink-gray-8 mb-2">
              </label>
              <textarea
                v-model="userInput"
                class="w-full px-3 py-2.5 border border-outline-gray-2 rounded-lg text-sm text-ink-gray-9 placeholder-ink-gray-5 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                :placeholder="__('e.g., Mention our refund policy or Suggest troubleshooting steps')"
                rows="3"
              ></textarea>
              <p class="mt-1.5 text-xs text-ink-gray-6">
                {{ __("Add specific instructions to help the AI generate better replies") }}
              </p>
            </div>

            <!-- Generate Button -->
            <div class="px-6 py-4 border-b border-outline-gray-2">
              <Button
                variant="solid"
                class="w-full bg-purple-600 hover:bg-purple-700"
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

            <!-- Suggestions Area -->
            <div class="px-6 py-5">
              <!-- Error State -->
              <div
                v-if="error"
                class="flex flex-col items-center justify-center py-10"
              >
                <div class="bg-red-50 rounded-full p-3 mb-3">
                  <LucideAlertCircle class="size-7 text-red-500" />
                </div>
                <p class="text-sm font-medium text-ink-gray-8 mb-2">{{ __("Failed to Generate") }}</p>
                <p class="text-xs text-ink-gray-6 text-center mb-4 max-w-xs">{{ error }}</p>
                <button
                  @click="generateSuggestions"
                  class="px-4 py-2 text-sm font-medium text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                >
                  {{ __("Try Again") }}
                </button>
              </div>

              <!-- Empty State -->
              <div
                v-else-if="!suggestions.length && !generateResource.loading"
                class="flex flex-col items-center justify-center py-16"
              >
                <div class="bg-purple-50 rounded-full p-4 mb-4">
                  <LucideSparkles class="size-8 text-purple-500" />
                </div>
                <p class="text-sm font-medium text-ink-gray-8 mb-2">{{ __("Ready to Generate") }}</p>
                <p class="text-xs text-ink-gray-6 text-center max-w-xs">{{ __("Select a tone and click 'Generate Replies' to get AI-powered suggestions") }}</p>
              </div>

              <!-- Loading State -->
              <div
                v-else-if="generateResource.loading"
                class="space-y-3"
              >
                <div
                  v-for="i in 3"
                  :key="i"
                  class="border border-outline-gray-2 rounded-xl p-4 animate-pulse"
                >
                  <div class="flex items-center justify-between mb-3">
                    <div class="h-3 bg-surface-gray-2 rounded w-20"></div>
                  </div>
                  <div class="space-y-2">
                    <div class="h-2.5 bg-surface-gray-2 rounded w-full"></div>
                    <div class="h-2.5 bg-surface-gray-2 rounded w-11/12"></div>
                    <div class="h-2.5 bg-surface-gray-2 rounded w-5/6"></div>
                  </div>
                </div>
              </div>

              <!-- Suggestions -->
              <div
                v-else
                class="space-y-3"
              >
                <div
                  v-for="suggestion in suggestions"
                  :key="suggestion.id"
                  class="border border-outline-gray-2 rounded-xl p-4 hover:border-purple-300 hover:shadow-sm transition-all cursor-pointer group"
                  @click="useSuggestion(suggestion)"
                >
                  <div class="flex items-start justify-between mb-3">
                    <span class="text-xs font-semibold text-purple-600 bg-purple-50 px-2 py-1 rounded">
                      {{ __("Option") }} {{ suggestion.id }}
                    </span>
                    <button
                      class="p-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                      @click.stop="useSuggestion(suggestion)"
                    >
                      <LucideCheck class="size-3.5" />
                    </button>
                  </div>
                  <p class="text-sm text-ink-gray-8 leading-relaxed whitespace-pre-wrap">
                    {{ suggestion.text }}
                  </p>
                </div>

                <!-- Regenerate Button -->
                <button
                  @click="generateSuggestions"
                  class="w-full mt-4 px-4 py-2.5 text-sm font-medium text-purple-600 hover:bg-purple-50 rounded-lg transition-colors border border-purple-200"
                >
                  {{ __("Generate 3 New Suggestions") }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { Button, createResource } from "frappe-ui";
import LucideSparkles from "~icons/lucide/sparkles";
import LucideCheck from "~icons/lucide/check";
import LucideX from "~icons/lucide/x";
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
const userInput = ref("");

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
    user_input: userInput.value,
  });
}

// Select a suggestion
function useSuggestion(suggestion: Suggestion) {
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
        userInput.value = "";
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
