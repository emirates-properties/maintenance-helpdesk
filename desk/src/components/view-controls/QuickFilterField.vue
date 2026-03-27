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
    :placeholder="filter.label"
    @change="(data) => updateFilter(filter, data)"
    class="w-44"
  />
  <SearchMultiSelect
    v-else-if="filter.type === 'Table MultiSelect'"
    :model-value="Array.isArray(props.value) ? props.value : []"
    :options="tagOptions"
    :placeholder="filter.label"
    :label="filter.label"
    selection-text="tags"
    @update:model-value="(val) => updateFilter(filter, val)"
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
import SearchMultiSelect from "@/components/SearchMultiSelect.vue";
import { useDebounceFn } from "@vueuse/core";
import { DatePicker, DateTimePicker, FormControl, TextInput, createListResource } from "frappe-ui";
import { inject, computed } from "vue";

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
</script>
