<template>
  <FormControl
    v-if="filter.type == 'Check'"
    :label="filter.label"
    type="checkbox"
    :checked="props.value"
    @change.stop="updateFilter(filter, $event.target.checked)"
    class="w-44"
  />
  <FormControl
    v-else-if="filter.type === 'Select'"
    class="form-control cursor-pointer [&_select]:cursor-pointer w-44"
    type="select"
    :model-value="props.value"
    :options="filter.options"
    :placeholder="filter.label"
    @change.stop="updateFilter(filter, $event.target.value)"
  />
  <Link
    v-else-if="filter.type === 'Link'"
    :value="props.value"
    :doctype="filter.options"
    :filters="getLinkFilters(filter)"
    :placeholder="getPlaceholder(filter)"
    :disabled="isFilterDisabled(filter)"
    @change="(data) => updateFilter(filter, data)"
    class="w-44"
  />
  <MultiSelect
    v-else-if="filter.type === 'Table MultiSelect'"
    v-model="tagSelection"
    :options="tagOptions"
    :placeholder="filter.label"
    :loading="pmsTags.loading"
  />
  <component
    v-else-if="['Date', 'Datetime'].includes(filter.type)"
    class="border-none w-44"
    :is="filter.type === 'Date' ? DatePicker : DateTimePicker"
    :value="props.value"
    @change="(v) => updateFilter(filter, v)"
    :placeholder="filter.label"
  />
  <TextInput
    v-else
    :value="props.value"
    type="text"
    :placeholder="filter.label"
    @input.stop="debouncedFn(filter, $event.target.value)"
  />
</template>
<script setup>
import { Link } from "@/components";
import { useDebounceFn } from "@vueuse/core";
import { DatePicker, DateTimePicker, FormControl, TextInput, MultiSelect, createListResource } from "frappe-ui";
import { inject, computed, watch } from "vue";

const props = defineProps({
  filter: {
    type: Object,
    required: true,
  },
  value: {
    type: [String, Boolean, Array],
    required: true,
  },
});

const emit = defineEmits(["applyQuickFilter"]);

// Inject listViewData to access current filter values
const listViewData = inject("listViewData");
const { list } = listViewData || {};

// Watch for property changes and clear unit if property changes
watch(
  () => list?.params?.filters?.property,
  (newProperty, oldProperty) => {
    // If property changed and this is the unit filter, clear it
    if (props.filter.name === 'unit' && newProperty !== oldProperty && props.value) {
      updateFilter(props.filter, '');
    }
  }
);

// Load HD PMS Tags for the Table MultiSelect filter
const pmsTags = createListResource({
  doctype: "HD PMS Tags",
  fields: ["tag_name", "colour"],
  filters: { is_active: 1 },
  auto: computed(() => props.filter.type === "Table MultiSelect"),
});

const tagOptions = computed(() =>
  (pmsTags.data || []).map((t) => ({ value: t.tag_name, label: t.tag_name }))
);

const tagSelection = computed({
  get() {
    return Array.isArray(props.value) ? props.value : [];
  },
  set(newValue) {
    updateFilter(props.filter, newValue);
  }
});

const debouncedFn = useDebounceFn((f, value) => {
  emit("applyQuickFilter", f, value);
}, 500);

function updateFilter(f, value) {
  emit("applyQuickFilter", f, value);
}

// Function to determine filters for Link fields based on dependencies
function getLinkFilters(filter) {
  // Handle unit filter - should be filtered by selected property
  if (filter.name === 'unit' && filter.options === 'PM Unit') {
    const currentFilters = list?.params?.filters || {};
    const propertyValue = currentFilters['property'];
    
    if (propertyValue) {
      return { property: propertyValue };
    }
  }
  
  return {};
}

// Function to determine if a filter should be disabled
function isFilterDisabled(filter) {
  // Disable unit filter if no property is selected
  if (filter.name === 'unit' && filter.options === 'PM Unit') {
    const currentFilters = list?.params?.filters || {};
    return !currentFilters['property'];
  }
  return false;
}

// Function to get dynamic placeholder text
function getPlaceholder(filter) {
  // Show helpful message for unit filter when no property selected
  if (filter.name === 'unit' && filter.options === 'PM Unit') {
    const currentFilters = list?.params?.filters || {};
    if (!currentFilters['property']) {
      return 'Select property first';
    }
  }
  return filter.label;
}
</script>
