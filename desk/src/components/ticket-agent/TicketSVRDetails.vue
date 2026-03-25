<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto px-5 py-4">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <LoadingIndicator :scale="8" class="text-ink-gray-5" />
      </div>

      <div v-else-if="error" class="text-center py-10">
        <p class="text-xs text-red-600">Error loading SVR details: {{ error }}</p>
      </div>

      <div v-else-if="!svrLogs || svrLogs.length === 0" class="text-center py-20">
        <LucideClipboardList class="mx-auto h-12 w-12 text-ink-gray-4" />
        <h3 class="mt-3 text-sm font-medium text-ink-gray-9">No SVR Logs</h3>
        <p class="mt-1 text-sm text-ink-gray-6">No SVR logs linked to this ticket yet.</p>
      </div>

      <div v-else class="space-y-3">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-base font-semibold text-ink-gray-9">
            SVR Logs ({{ svrLogs.length }})
          </h3>
        </div>

        <div
          v-for="(svrLog, index) in svrLogs"
          :key="svrLog.name"
          class="bg-surface-gray-1 rounded-lg p-4 border border-outline-gray-2 hover:border-outline-gray-4 transition-colors"
        >
          <!-- Header row -->
          <div class="flex items-start justify-between gap-2 mb-3">
            <div class="flex-1 min-w-0">
              <span class="text-sm font-semibold text-ink-gray-9 block">
                {{ svrLog.svr_number || `SVR #${index + 1}` }}
              </span>
              <span class="text-xs text-ink-gray-6">{{ formatDate(svrLog.date) }}</span>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span
                class="px-2 py-0.5 text-xs font-medium rounded-full"
                :class="getStatusClass(svrLog.status)"
              >
                {{ svrLog.status || 'OPEN' }}
              </span>
              <span
                class="px-2 py-0.5 text-xs font-medium rounded-full"
                :class="getPriorityClass(svrLog.priority)"
              >
                {{ svrLog.priority || 'Low' }}
              </span>
              <Button
                v-if="svrLog.name"
                variant="outline"
                size="sm"
                :icon-left="LucideExternalLink"
                label="Open"
                @click="openSVRLog(svrLog.name)"
              />
            </div>
          </div>

          <!-- Details grid -->
          <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
            <div v-if="svrLog.zone">
              <dt class="text-ink-gray-6">Zone</dt>
              <dd class="font-medium text-ink-gray-9">{{ svrLog.zone }}</dd>
            </div>

            <div v-if="svrLog.property">
              <dt class="text-ink-gray-6">Property</dt>
              <dd class="font-medium text-ink-gray-9">{{ svrLog.property }}</dd>
            </div>

            <div v-if="svrLog.unit">
              <dt class="text-ink-gray-6">Unit</dt>
              <dd class="font-medium text-ink-gray-9">{{ svrLog.unit }}</dd>
            </div>

            <div v-if="svrLog.tenant_name">
              <dt class="text-ink-gray-6">Tenant</dt>
              <dd class="font-medium text-ink-gray-9">{{ svrLog.tenant_name }}</dd>
            </div>

            <div v-if="svrLog.contract_number">
              <dt class="text-ink-gray-6">Contract</dt>
              <dd class="font-medium text-ink-gray-9">{{ svrLog.contract_number }}</dd>
            </div>

            <div v-if="svrLog.service_category">
              <dt class="text-ink-gray-6">Category</dt>
              <dd class="font-medium text-ink-gray-9">{{ svrLog.service_category }}</dd>
            </div>

            <div v-if="svrLog.assigned_to">
              <dt class="text-ink-gray-6">Assigned To</dt>
              <dd class="font-medium text-ink-gray-9">{{ svrLog.assigned_to }}</dd>
            </div>

            <div v-if="svrLog.work_done_by">
              <dt class="text-ink-gray-6">Work Done By</dt>
              <dd class="font-medium text-ink-gray-9">{{ svrLog.work_done_by }}</dd>
            </div>

            <div v-if="svrLog.supervisor_inspection_required" class="col-span-2">
              <dt class="text-ink-gray-6">Supervisor Inspection</dt>
              <dd class="font-medium text-yellow-700">Required</dd>
            </div>

            <div v-if="svrLog.tags && svrLog.tags.length > 0" class="col-span-2">
              <dt class="text-ink-gray-6 mb-1">Tags</dt>
              <dd class="flex flex-wrap gap-1">
                <span
                  v-for="tag in svrLog.tags"
                  :key="tag"
                  class="px-1.5 py-0.5 bg-surface-gray-2 text-ink-gray-7 rounded"
                >{{ tag }}</span>
              </dd>
            </div>

            <div v-if="svrLog.remarks" class="col-span-2">
              <dt class="text-ink-gray-6 mb-1">Remarks</dt>
              <dd class="font-medium text-ink-gray-9 bg-surface-white rounded p-2 leading-relaxed">
                {{ svrLog.remarks }}
              </dd>
            </div>

            <div v-if="svrLog.creation">
              <dt class="text-ink-gray-6">Created</dt>
              <dd class="font-medium text-ink-gray-9">{{ formatDateTime(svrLog.creation) }}</dd>
            </div>

            <div v-if="svrLog.modified">
              <dt class="text-ink-gray-6">Last Modified</dt>
              <dd class="font-medium text-ink-gray-9">{{ formatDateTime(svrLog.modified) }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button, LoadingIndicator, createResource } from "frappe-ui";
import { computed, inject, provide, watch, onMounted } from "vue";
import LucideClipboardList from "~icons/lucide/clipboard-list";
import LucideExternalLink from "~icons/lucide/external-link";
import { TicketSymbol } from "@/types";

const ticket = inject(TicketSymbol);

const svrLogsResource = createResource({
  url: "helpdesk.api.svr.get_ticket_svr_logs",
  makeParams() {
    const ticketId = ticket?.value?.doc?.name;
    return {
      ticket_id: ticketId || null,
    };
  },
  auto: false,
});

// Fetch on mount
onMounted(() => {
  if (ticket?.value?.doc?.name) {
    svrLogsResource.fetch();
  }
});

// Provide reload function for external components to trigger refresh
provide("reloadSVRLogs", () => {
  svrLogsResource.reload();
});

// Watch for changes in ticket and refetch SVR logs
watch(
  () => ticket?.value?.doc?.name,
  (newTicketId) => {
    if (newTicketId) {
      svrLogsResource.reload();
    }
  }
);

const loading = computed(() => svrLogsResource.loading);
const error = computed(() => svrLogsResource.error);
const svrLogs = computed(() => svrLogsResource.data || []);

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

const openSVRLog = (logId: string) => {
  if (logId) {
    // Get EPFM URL from environment variable
    // In dev: http://localhost:8081 (from .env)
    // In prod: configured via deployment (e.g., https://epfm.yourdomain.com)
    // If empty: uses relative path for same-domain deployments
    const baseUrl = import.meta.env.VITE_EPFM_URL || '';
    const epfmUrl = `${baseUrl}/epfm-ot/maintenance-log/${logId}`;
    
    console.log('Opening SVR log in EPFM app at:', epfmUrl);
    window.open(epfmUrl, '_blank');
  }
};
</script>
