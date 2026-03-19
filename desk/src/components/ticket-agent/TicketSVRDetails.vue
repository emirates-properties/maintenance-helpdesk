<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto px-5 py-4">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <LoadingIndicator :scale="8" class="text-ink-gray-5" />
      </div>

      <div v-else-if="error" class="text-center py-10">
        <p class="text-red-600">Error loading SVR details: {{ error }}</p>
      </div>

      <div v-else-if="!svrLog" class="text-center py-20">
        <svg
          class="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No SVR Log</h3>
        <p class="mt-1 text-sm text-gray-500">
          This ticket doesn't have an associated SVR log yet.
        </p>
      </div>

      <div v-else class="space-y-6">
        <!-- SVR Information -->
        <div class="bg-surface-gray-1 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold text-ink-gray-9">SVR Information</h3>
            <Button
              v-if="svrLog.name"
              variant="outline"
              size="sm"
              @click="openSVRLog"
            >
              View Full SVR
            </Button>
          </div>
          
          <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt class="text-sm font-medium text-ink-gray-7">SVR Number</dt>
              <dd class="mt-1 text-sm text-ink-gray-9 font-semibold">
                {{ svrLog.svr_number || '-' }}
              </dd>
            </div>
            
            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Status</dt>
              <dd class="mt-1">
                <span
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getStatusClass(svrLog.status)"
                >
                  {{ svrLog.status || 'OPEN' }}
                </span>
              </dd>
            </div>
            
            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Date</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ formatDate(svrLog.date) }}
              </dd>
            </div>
            
            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Priority</dt>
              <dd class="mt-1">
                <span
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getPriorityClass(svrLog.priority)"
                >
                  {{ svrLog.priority || 'Low' }}
                </span>
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Zone</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ svrLog.zone || '-' }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Property</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ svrLog.property || '-' }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Unit</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ svrLog.unit || '-' }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Contract Number</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ svrLog.contract_number || '-' }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Tenant Name</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ svrLog.tenant_name || '-' }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Service Category</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ svrLog.service_category || '-' }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Assigned To</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ svrLog.assigned_to || '-' }}
              </dd>
            </div>

            <div>
              <dt class="text-sm font-medium text-ink-gray-7">Work Done By</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ svrLog.work_done_by || '-' }}
              </dd>
            </div>

            <div v-if="svrLog.remarks" class="sm:col-span-2">
              <dt class="text-sm font-medium text-ink-gray-7">Remarks</dt>
              <dd class="mt-1 text-sm text-ink-gray-9 bg-white rounded p-2">
                {{ svrLog.remarks }}
              </dd>
            </div>

            <div v-if="svrLog.supervisor_inspection_required !== undefined" class="sm:col-span-2">
              <dt class="text-sm font-medium text-ink-gray-7">Supervisor Inspection Required</dt>
              <dd class="mt-1">
                <span
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="svrLog.supervisor_inspection_required ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'"
                >
                  {{ svrLog.supervisor_inspection_required ? 'Yes - Required' : 'No' }}
                </span>
              </dd>
            </div>

            <div v-if="svrLog.tags && svrLog.tags.length > 0" class="sm:col-span-2">
              <dt class="text-sm font-medium text-ink-gray-7">Tags</dt>
              <dd class="mt-1 flex flex-wrap gap-2">
                <span
                  v-for="tag in svrLog.tags"
                  :key="tag"
                  class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded"
                >
                  {{ tag }}
                </span>
              </dd>
            </div>

            <div v-if="svrLog.creation">
              <dt class="text-sm font-medium text-ink-gray-7">Created</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ formatDateTime(svrLog.creation) }}
              </dd>
            </div>

            <div v-if="svrLog.modified">
              <dt class="text-sm font-medium text-ink-gray-7">Last Modified</dt>
              <dd class="mt-1 text-sm text-ink-gray-9">
                {{ formatDateTime(svrLog.modified) }}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button, LoadingIndicator, createResource } from "frappe-ui";
import { computed, inject } from "vue";
import { TicketSymbol } from "@/types";

const ticket = inject(TicketSymbol);

const svrLogResource = createResource({
  url: "helpdesk.api.svr.get_svr_log",
  makeParams() {
    return {
      name: ticket?.value?.doc?.svr_log_id || null,
    };
  },
  auto: false,
});

// Watch for changes in SVR log ID and fetch if exists
const svrLogId = computed(() => ticket?.value?.doc?.svr_log_id);
if (svrLogId.value) {
  svrLogResource.fetch();
}

const loading = computed(() => svrLogResource.loading);
const error = computed(() => svrLogResource.error);
const svrLog = computed(() => svrLogResource.data);

const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const formatDateTime = (dateString: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    'COMPLETED': 'bg-green-100 text-green-800',
    'RESOLVED': 'bg-emerald-100 text-emerald-800',
    'INPROGRESS': 'bg-blue-100 text-blue-800',
    'ASSIGNED': 'bg-cyan-100 text-cyan-800',
    'OPEN': 'bg-yellow-100 text-yellow-800',
    'HOLD': 'bg-orange-100 text-orange-800',
    'MATERIAL PENDING': 'bg-purple-100 text-purple-800',
    'REASSIGNMENT': 'bg-indigo-100 text-indigo-800',
    'REASSIGNED COMPLETED': 'bg-teal-100 text-teal-800',
  };
  return statusMap[status] || 'bg-gray-100 text-gray-800';
};

const getPriorityClass = (priority: string) => {
  const priorityMap: Record<string, string> = {
    'Urgent': 'bg-red-100 text-red-800',
    'High': 'bg-orange-100 text-orange-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'Low': 'bg-green-100 text-green-800',
  };
  return priorityMap[priority] || 'bg-gray-100 text-gray-800';
};

const openSVRLog = () => {
  if (svrLog.value && svrLog.value.name) {
    const logId = svrLog.value.name;
    
    // Open the EPFM Vue app on port 8081
    // Ports: Helpdesk (8080/8082), EPFM (8081), Backend (8000)
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    
    // Always use port 8081 for EPFM Vue app
    const epfmUrl = `${protocol}//${hostname}:8081/epfm-ot/maintenance-log/${logId}`;
    
    console.log('Opening SVR log in EPFM Vue app at:', epfmUrl);
    window.open(epfmUrl, '_blank');
  }
};
</script>
