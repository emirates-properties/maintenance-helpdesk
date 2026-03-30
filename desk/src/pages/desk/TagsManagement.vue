<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="border-b border-outline-gray-2 px-5 py-4">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-semibold text-ink-gray-9">Tags Management</h1>
        <Button
          v-if="isAdmin"
          label="New Tag"
          variant="solid"
          @click="openCreateModal"
        >
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </div>
      <p class="text-sm text-ink-gray-6 mt-1">
        Manage tags used for organizing tickets
      </p>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-5 py-4">
      <!-- Loading -->
      <div v-if="allTags.loading" class="flex items-center justify-center py-20">
        <LoadingIndicator :scale="8" class="text-ink-gray-5" />
      </div>

      <!-- Tags List -->
      <div v-else class="space-y-2">
        <div
          v-for="tag in (allTags.data || [])"
          :key="tag.name"
          class="flex items-center gap-4 rounded-lg border border-outline-gray-2 bg-surface-white px-4 py-3 hover:bg-surface-gray-1 transition-colors"
        >
          <span
            class="inline-block w-4 h-4 rounded-full flex-shrink-0"
            :style="{ backgroundColor: tag.colour || '#94a3b8' }"
          />
          <span class="text-base text-ink-gray-9 flex-1 font-medium">
            {{ tag.tag_name }}
          </span>
          <Badge
            :label="tag.is_active ? 'Active' : 'Inactive'"
            :theme="tag.is_active ? 'green' : 'gray'"
            variant="subtle"
          />
          <div v-if="isAdmin" class="flex items-center gap-2">
            <Button
              icon="edit"
              variant="ghost"
              @click="openEditModal(tag)"
            />
            <Button
              icon="trash-2"
              variant="ghost"
              theme="red"
              @click="confirmDelete(tag)"
            />
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="!allTags.data || allTags.data.length === 0"
          class="flex flex-col items-center justify-center py-20 text-center"
        >
          <LucideTag class="h-12 w-12 text-ink-gray-4 mb-4" />
          <h3 class="text-lg font-medium text-ink-gray-8 mb-2">No tags yet</h3>
          <p class="text-sm text-ink-gray-6 mb-4">
            Create your first tag to start organizing tickets
          </p>
          <Button
            v-if="isAdmin"
            label="Create Tag"
            variant="solid"
            @click="openCreateModal"
          >
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>
    </div>
  </div>

  <!-- Tag Create/Edit Modal -->
  <Dialog
    v-model="showTagModal"
    :options="{
      title: editingTag ? 'Edit Tag' : 'Create Tag',
      size: 'sm',
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <FormControl
          label="Tag Name"
          v-model="tagForm.tag_name"
          placeholder="Enter tag name"
          required
        />
        <div>
          <label class="block text-sm font-medium text-ink-gray-9 mb-2">
            Color
          </label>
          <div class="flex gap-2 flex-wrap">
            <button
              v-for="color in colorOptions"
              :key="color"
              @click="tagForm.colour = color"
              class="w-10 h-10 rounded-full border-2 transition-all hover:scale-110"
              :class="tagForm.colour === color ? 'border-ink-gray-9 scale-110' : 'border-outline-gray-2'"
              :style="{ backgroundColor: color }"
            />
          </div>
        </div>
        <div class="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_active"
            v-model="tagForm.is_active"
            class="h-4 w-4 rounded border-outline-gray-3 text-ink-gray-9"
          />
          <label for="is_active" class="text-sm text-ink-gray-8">
            Active (visible for ticket assignment)
          </label>
        </div>
      </div>
    </template>
    <template #actions>
      <Button
        label="Cancel"
        variant="ghost"
        @click="showTagModal = false"
      />
      <Button
        :label="editingTag ? 'Update' : 'Create'"
        variant="solid"
        @click="saveTag"
        :loading="savingTag"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { 
  LoadingIndicator, 
  createListResource, 
  Button, 
  Dialog, 
  FormControl,
  createResource,
  toast,
  Badge
} from 'frappe-ui';
import { computed, ref, reactive } from 'vue';
import LucidePlus from "~icons/lucide/plus";
import LucideTag from "~icons/lucide/tag";
import { globalStore } from "@/stores/globalStore";
import { useAuthStore } from "@/stores/auth";

const { $dialog } = globalStore();
const authStore = useAuthStore();

const allTags = createListResource({
  doctype: 'HD PMS Tags',
  fields: ['name', 'tag_name', 'colour', 'is_active'],
  orderBy: 'tag_name asc',
  auto: true,
});

// Check if user is admin
const isAdmin = computed(() => authStore.isAdmin);

// Tag management
const showTagModal = ref(false);
const editingTag = ref<any>(null);
const savingTag = ref(false);

const tagForm = reactive({
  tag_name: '',
  colour: '#94a3b8',
  is_active: true,
});

const colorOptions = [
  '#EF4444', // red
  '#F59E0B', // amber
  '#10B981', // green
  '#3B82F6', // blue
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#94a3b8', // gray
  '#06B6D4', // cyan
  '#F97316', // orange
];

const createTagResource = createResource({
  url: 'frappe.client.insert',
  onSuccess() {
    toast.success('Tag created successfully');
    allTags.reload();
    showTagModal.value = false;
    resetForm();
  },
  onError(_error: any) {
    toast.error('Failed to create tag');
  },
});

const updateTagResource = createResource({
  url: 'frappe.client.set_value',
  onSuccess() {
    toast.success('Tag updated successfully');
    allTags.reload();
    showTagModal.value = false;
    resetForm();
  },
  onError(_error: any) {
    toast.error('Failed to update tag');
  },
});

const deleteTagResource = createResource({
  url: 'frappe.client.delete',
  onSuccess() {
    toast.success('Tag deleted successfully');
    allTags.reload();
  },
  onError(_error: any) {
    toast.error('Failed to delete tag');
  },
});

function openCreateModal() {
  editingTag.value = null;
  resetForm();
  showTagModal.value = true;
}

function openEditModal(tag: any) {
  editingTag.value = tag;
  tagForm.tag_name = tag.tag_name;
  tagForm.colour = tag.colour || '#94a3b8';
  tagForm.is_active = tag.is_active;
  showTagModal.value = true;
}

function resetForm() {
  tagForm.tag_name = '';
  tagForm.colour = '#94a3b8';
  tagForm.is_active = true;
}

async function saveTag() {
  if (!tagForm.tag_name.trim()) {
    toast.error('Tag name is required');
    return;
  }

  savingTag.value = true;

  if (editingTag.value) {
    // Update existing tag
    await updateTagResource.submit({
      doctype: 'HD PMS Tags',
      name: editingTag.value.name,
      fieldname: {
        tag_name: tagForm.tag_name,
        colour: tagForm.colour,
        is_active: tagForm.is_active ? 1 : 0,
      },
    });
  } else {
    // Create new tag
    await createTagResource.submit({
      doc: {
        doctype: 'HD PMS Tags',
        tag_name: tagForm.tag_name,
        colour: tagForm.colour,
        is_active: tagForm.is_active ? 1 : 0,
      },
    });
  }

  savingTag.value = false;
}

function confirmDelete(tag: any) {
  $dialog({
    title: 'Delete Tag',
    message: `Are you sure you want to delete "${tag.tag_name}"? This action cannot be undone.`,
    actions: [
      {
        label: 'Cancel',
        variant: 'ghost',
      },
      {
        label: 'Delete',
        variant: 'solid',
        theme: 'red',
        onClick: ({ close }: any) => {
          deleteTag(tag.name);
          close();
        },
      },
    ],
  });
}

function deleteTag(tagName: string) {
  deleteTagResource.submit({
    doctype: 'HD PMS Tags',
    name: tagName,
  });
}
</script>
