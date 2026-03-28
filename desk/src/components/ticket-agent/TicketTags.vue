<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto px-5 py-4">
      <!-- Loading -->
      <div v-if="allTags.loading" class="flex items-center justify-center py-20">
        <LoadingIndicator :scale="8" class="text-ink-gray-5" />
      </div>

      <template v-else>
        <!-- MultiSelect for managing tags -->
        <div class="mb-5">
          <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">
            Assigned Tags ({{ assignedTags.length }})
          </h3>
          <MultiSelect
            v-model="selectedTagValues"
            :options="tagOptions"
            placeholder="Select tags"
            :loading="allTags.loading"
          />
        </div>

        <!-- All available tags list -->
        <div class="border-t border-outline-gray-2 pt-4">
          <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">
            All Tags
          </h3>
          <div class="space-y-2">
            <div
              v-for="t in (allTags.data || [])"
              :key="t.name"
              class="flex items-center gap-3 py-1.5"
            >
              <span
                class="inline-block w-3 h-3 rounded-full flex-shrink-0"
                :style="{ backgroundColor: t.colour || '#94a3b8' }"
              />
              <span class="text-sm text-ink-gray-8 flex-1">{{ t.tag_name }}</span>
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :class="t.is_active ? 'bg-green-100 text-green-700' : 'bg-surface-gray-2 text-ink-gray-6'"
              >
                {{ t.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { TicketSymbol } from '@/types';
import { MultiSelect, LoadingIndicator, createListResource } from 'frappe-ui';
import { computed, inject } from 'vue';

const ticket = inject(TicketSymbol);

const allTags = createListResource({
  doctype: 'HD PMS Tags',
  fields: ['name', 'tag_name', 'colour', 'is_active'],
  orderBy: 'tag_name asc',
  auto: true,
});

const tagOptions = computed(() =>
  (allTags.data || []).filter((t: any) => t.is_active).map((t: any) => ({ label: t.tag_name, value: t.tag_name }))
);

const assignedTags = computed(() => {
  return ticket?.value?.doc?.tags || [];
});

const selectedTagValues = computed<string[]>({
  get() {
    return (ticket?.value?.doc?.tags || []).map((r: { tag: string }) => r.tag);
  },
  set(values: string[]) {
    ticket?.value?.setValue.submit({ tags: values.map((v) => ({ tag: v })) });
  },
});
</script>
