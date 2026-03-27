<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto px-5 py-4">
      <!-- Loading -->
      <div v-if="allTags.loading" class="flex items-center justify-center py-20">
        <LoadingIndicator :scale="8" class="text-ink-gray-5" />
      </div>

      <template v-else>
        <!-- Assigned tags -->
        <div class="mb-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-ink-gray-9">
              Assigned Tags ({{ assignedTags.length }})
            </h3>
            <Button
              variant="outline"
              size="sm"
              :icon-left="LucidePlus"
              label="Add Tag"
              @click="showPicker = !showPicker"
            />
          </div>

          <!-- Tag picker dropdown -->
          <div v-if="showPicker" class="mb-3 border border-outline-gray-2 rounded-lg p-3 bg-surface-gray-1">
            <div class="mb-2">
              <TextInput
                v-model="search"
                placeholder="Search tags..."
                size="sm"
              />
            </div>
            <div class="space-y-1 max-h-40 overflow-y-auto">
              <div
                v-for="t in filteredAvailableTags"
                :key="t.name"
                class="flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer hover:bg-surface-gray-2"
                @click="addTag(t)"
              >
                <span
                  class="inline-block w-3 h-3 rounded-full flex-shrink-0"
                  :style="{ backgroundColor: t.colour || '#94a3b8' }"
                />
                <span class="text-sm text-ink-gray-8">{{ t.tag_name }}</span>
              </div>
              <div v-if="filteredAvailableTags.length === 0" class="text-xs text-ink-gray-5 py-2 text-center">
                No more tags to add
              </div>
            </div>
          </div>

          <!-- Assigned tag pills -->
          <div v-if="assignedTags.length > 0" class="flex flex-wrap gap-2">
            <span
              v-for="row in assignedTags"
              :key="row.tag"
              class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium text-white"
              :style="{ backgroundColor: getTagColour(row.tag) }"
            >
              {{ row.tag }}
              <button
                class="ml-0.5 hover:opacity-70 focus:outline-none"
                @click="removeTag(row.tag)"
              >
                <LucideX class="size-3" />
              </button>
            </span>
          </div>

          <div v-else-if="!showPicker" class="text-center py-10">
            <LucideTag class="mx-auto h-10 w-10 text-ink-gray-4" />
            <p class="mt-2 text-sm text-ink-gray-6">No tags assigned yet</p>
            <p class="text-xs text-ink-gray-5">Click "Add Tag" to assign one</p>
          </div>
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
import LucidePlus from '~icons/lucide/plus';
import LucideX from '~icons/lucide/x';
import LucideTag from '~icons/lucide/tag';
import { TicketSymbol } from '@/types';
import { createListResource } from 'frappe-ui';
import { Button, LoadingIndicator, TextInput } from 'frappe-ui';
import { computed, inject, ref } from 'vue';

const ticket = inject(TicketSymbol);
const showPicker = ref(false);
const search = ref('');

const allTags = createListResource({
  doctype: 'HD PMS Tags',
  fields: ['name', 'tag_name', 'colour', 'is_active'],
  orderBy: 'tag_name asc',
  auto: true,
});

const assignedTags = computed<{ tag: string }[]>(() => {
  return ticket?.value?.doc?.tags || [];
});

const assignedTagNames = computed(() =>
  new Set(assignedTags.value.map((r) => r.tag))
);

const filteredAvailableTags = computed(() => {
  return (allTags.data || []).filter(
    (t: any) =>
      t.is_active &&
      !assignedTagNames.value.has(t.tag_name) &&
      (search.value === '' || t.tag_name.toLowerCase().includes(search.value.toLowerCase()))
  );
});

function getTagColour(tagName: string): string {
  const found = (allTags.data || []).find((t: any) => t.tag_name === tagName);
  return found?.colour || '#94a3b8';
}

function addTag(t: any) {
  const newTags = [
    ...assignedTags.value,
    { tag: t.tag_name },
  ];
  ticket?.value?.setValue.submit({ tags: newTags });
  showPicker.value = false;
  search.value = '';
}

function removeTag(tagName: string) {
  const newTags = assignedTags.value.filter((r) => r.tag !== tagName);
  ticket?.value?.setValue.submit({ tags: newTags });
}
</script>
