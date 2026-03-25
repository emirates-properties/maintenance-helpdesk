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
import { DatePicker, DateTimePicker, FormControl, TextInput } from "frappe-ui";
import { inject, computed } from "vue";

const props = defineProps({
  filter: {
    type: Object,
    required: true,
  },
  value: {
    type: [String, Boolean],
    required: true,
  },
});

const emit = defineEmits(["applyQuickFilter"]);

// Inject listViewData to access current filter values
const listViewData = inject("listViewData");
const { list } = listViewData || {};

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
