<template>
  <Dialog
    v-model="show"
    :options="{
      title: 'Assign SVR to Ticket',
      size: 'xl',
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div class="text-sm text-ink-gray-7 mb-4">
          Enter the SVR number to link an existing SVR log to this ticket
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-ink-gray-9 mb-1">
              SVR Number <span class="text-red-500">*</span>
            </label>
            <FormControl
              v-model="svrNumber"
              type="text"
              placeholder="Enter SVR ID or Number (e.g., ML-108 or 12345)"
              @blur="fetchSVRDetails"
            />
           
          </div>

          <div v-if="loading" class="flex items-center justify-center py-4">
            <LoadingIndicator class="text-ink-gray-5" />
            <span class="ml-2 text-sm text-ink-gray-7">Loading SVR details...</span>
          </div>

          <div v-else-if="svrNumber && svrDetails" class="bg-surface-gray-1 rounded-lg p-4 mt-4">
            <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">SVR Details</h3>
            <dl class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt class="text-ink-gray-7">SVR Number</dt>
                <dd class="text-ink-gray-9 font-medium">{{ svrDetails.svr_number }}</dd>
              </div>
              <div>
                <dt class="text-ink-gray-7">Status</dt>
                <dd class="text-ink-gray-9">{{ svrDetails.status || 'OPEN' }}</dd>
              </div>
              <div>
                <dt class="text-ink-gray-7">Property</dt>
                <dd class="text-ink-gray-9">{{ svrDetails.property || '-' }}</dd>
              </div>
              <div>
                <dt class="text-ink-gray-7">Unit</dt>
                <dd class="text-ink-gray-9">{{ svrDetails.unit || '-' }}</dd>
              </div>
              <div>
                <dt class="text-ink-gray-7">Date</dt>
                <dd class="text-ink-gray-9">{{ formatDate(svrDetails.date) }}</dd>
              </div>
              <div>
                <dt class="text-ink-gray-7">Priority</dt>
                <dd class="text-ink-gray-9">{{ svrDetails.priority || '-' }}</dd>
              </div>
              <div v-if="svrDetails.ticket_id" class="col-span-2">
                <dt class="text-ink-gray-7">Current Ticket</dt>
                <dd class="text-orange-600 font-medium">
                  ⚠️ Already linked to ticket: {{ svrDetails.ticket_id }}
                </dd>
              </div>
            </dl>
          </div>

          <div v-if="error" class="text-red-600 text-sm mt-2 bg-red-50 p-3 rounded">
            {{ error }}
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <Button
        label="Cancel"
        @click="show = false"
      />
      <Button
        label="Assign SVR"
        variant="solid"
        :loading="isAssigning"
        :disabled="!svrNumber || !svrDetails || !!svrDetails.ticket_id"
        @click="assignSVR"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Dialog, Button, FormControl, LoadingIndicator, call } from 'frappe-ui';
import { toast } from 'frappe-ui';

interface Props {
  modelValue: boolean;
  ticketId: string;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'success'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const svrNumber = ref('');
const svrDetails = ref<any>(null);
const error = ref('');
const loading = ref(false);
const isAssigning = ref(false);

// Watch for SVR number changes to reset state
watch(svrNumber, (newVal) => {
  if (!newVal) {
    svrDetails.value = null;
    error.value = '';
  }
});

async function fetchSVRDetails() {
  if (!svrNumber.value || !svrNumber.value.trim()) {
    svrDetails.value = null;
    error.value = '';
    return;
  }

  loading.value = true;
  error.value = '';
  svrDetails.value = null;

  try {
    // Fetch SVR log by svr_number field
    const result = await call('frappe.client.get_list', {
      doctype: 'EPFM Maintanace Log',
      filters: { svr_number: svrNumber.value.trim() },
      fields: ['name', 'svr_number', 'date', 'status', 'priority', 'property', 'unit', 'ticket_id'],
      limit: 1
    });

    if (result && result.length > 0) {
      svrDetails.value = result[0];
      if (result[0].ticket_id) {
        error.value = `This SVR is already assigned to ticket ${result[0].ticket_id}`;
      }
    } else {
      error.value = `SVR number "${svrNumber.value}" not found in EPFM Maintenance Logs`;
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to fetch SVR details';
    console.error('Error fetching SVR:', err);
  } finally {
    loading.value = false;
  }
}

function formatDate(dateString: string) {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

async function assignSVR() {
  if (!svrNumber.value || !svrDetails.value) {
    error.value = 'Please enter a valid SVR number';
    return;
  }

  if (svrDetails.value.ticket_id) {
    error.value = 'This SVR is already assigned to another ticket';
    return;
  }

  isAssigning.value = true;
  error.value = '';

  try {
    // Update the ticket_id field in EPFM Maintanace Log
    await call('frappe.client.set_value', {
      doctype: 'EPFM Maintanace Log',
      name: svrDetails.value.name,
      fieldname: 'ticket_id',
      value: props.ticketId,
    });

    toast.success(`SVR ${svrNumber.value} assigned successfully`);
    emit('success');
    show.value = false;
  } catch (err: any) {
    error.value = err.message || 'Failed to assign SVR';
    console.error('Error assigning SVR:', err);
  } finally {
    isAssigning.value = false;
  }
}
</script>
