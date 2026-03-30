<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto px-5 py-4">
      <!-- Loading -->
      <div v-if="allTags.loading" class="flex items-center justify-center py-20">
        <LoadingIndicator :scale="8" class="text-ink-gray-5" />
      </div>

      <template v-else>
        <!-- Button-based tag assignment -->
        <div>
          <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">
            Assigned Tags ({{ assignedTags.length }})
          </h3>
          
          <!-- Tag buttons -->
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tag in availableTags"
              :key="tag.name"
              @click="toggleTag(tag.tag_name)"
              class="flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all hover:scale-105"
              :class="isTagAssigned(tag.tag_name) 
                ? 'border-ink-gray-9 bg-surface-gray-2 shadow-sm' 
                : 'border-outline-gray-2 bg-surface-white hover:bg-surface-gray-1'"
            >
              <span
                class="inline-block w-3 h-3 rounded-full flex-shrink-0"
                :style="{ backgroundColor: tag.colour || '#94a3b8' }"
              />
              <span 
                class="text-sm font-medium"
                :class="isTagAssigned(tag.tag_name) ? 'text-ink-gray-9' : 'text-ink-gray-7'"
              >
                {{ tag.tag_name }}
              </span>
              <LucideCheck 
                v-if="isTagAssigned(tag.tag_name)"
                class="w-4 h-4 text-green-600"
              />
            </button>
          </div>
          
          <!-- Empty state -->
          <div
            v-if="!availableTags || availableTags.length === 0"
            class="text-center py-8 text-ink-gray-6 text-sm"
          >
            No active tags available. Create tags from the Tags page.
          </div>
          
          <p class="text-xs text-ink-gray-6 mt-3">
            Click tags to assign or unassign them to this ticket
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { TicketSymbol } from '@/types';
import { LoadingIndicator, createListResource } from 'frappe-ui';
import { computed, inject } from 'vue';
import LucideCheck from "~icons/lucide/check";

const ticket = inject(TicketSymbol);

const allTags = createListResource({
  doctype: 'HD PMS Tags',
  fields: ['name', 'tag_name', 'colour', 'is_active'],
  orderBy: 'tag_name asc',
  auto: true,
});

const availableTags = computed(() => {
  return (allTags.data || []).filter((t: any) => t.is_active);
});

const assignedTags = computed(() => {
  return ticket?.value?.doc?.tags || [];
});

const assignedTagNames = computed(() => {
  return assignedTags.value.map((t: { tag: string }) => t.tag);
});

function isTagAssigned(tagName: string): boolean {
  return assignedTagNames.value.includes(tagName);
}

function toggleTag(tagName: string) {
  let currentTags = [...assignedTagNames.value];
  
  if (isTagAssigned(tagName)) {
    // Remove tag
    currentTags = currentTags.filter(t => t !== tagName);
  } else {
    // Add tag
    currentTags.push(tagName);
  }
  
  // Update ticket tags
  ticket?.value?.setValue.submit({ 
    tags: currentTags.map((v) => ({ tag: v })) 
  });
}
</script>
