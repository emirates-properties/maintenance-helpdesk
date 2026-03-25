<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto px-5 py-4">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <LoadingIndicator :scale="8" class="text-ink-gray-5" />
      </div>

      <div v-else-if="!tickets || tickets.length === 0" class="text-center py-20">
        <LucideHistory class="mx-auto h-12 w-12 text-ink-gray-4" />
        <h3 class="mt-3 text-sm font-medium text-ink-gray-9">No Previous Tickets</h3>
        <p class="mt-1 text-sm text-ink-gray-6">
          No other tickets found for <span class="font-medium">{{ raisedBy }}</span>.
        </p>
      </div>

      <div v-else class="space-y-3">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-base font-semibold text-ink-gray-9">
            Previous Tickets for {{ raisedBy }} ({{ tickets.length }})
          </h3>
        </div>

        <div
          v-for="t in tickets"
          :key="t.name"
          class="bg-surface-gray-1 rounded-lg p-4 border border-outline-gray-2 hover:border-outline-gray-4 transition-colors"
        >
          <!-- Header row -->
          <div class="flex items-start justify-between gap-2 mb-3">
            <div class="flex-1 min-w-0">
              <a
                :href="`/helpdesk/tickets/${t.name}`"
                target="_blank"
                class="text-sm font-semibold text-ink-gray-9 hover:text-ink-gray-7 truncate block"
              >
                {{ t.subject || '(No subject)' }}
              </a>
              <span class="text-xs text-ink-gray-6">#{{ t.name }}</span>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span
                class="px-2 py-0.5 text-xs font-medium rounded-full"
                :class="getStatusClass(t.status)"
              >
                {{ t.status }}
              </span>
              <Button
                v-if="!t.is_merged && !currentTicket?.is_merged"
                variant="outline"
                size="sm"
                :icon-left="LucideMerge"
                label="Merge"
                @click="openMergeConfirm(t)"
              />
            </div>
          </div>

          <!-- Details grid -->
          <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
            <div v-if="t.priority">
              <dt class="text-ink-gray-6">Priority</dt>
              <dd class="font-medium text-ink-gray-9">
                <span
                  class="px-1.5 py-0.5 rounded-full"
                  :class="getPriorityClass(t.priority)"
                >{{ t.priority }}</span>
              </dd>
            </div>

            <div v-if="t.ticket_type">
              <dt class="text-ink-gray-6">Type</dt>
              <dd class="font-medium text-ink-gray-9">{{ t.ticket_type }}</dd>
            </div>

            <div v-if="t.agent_group">
              <dt class="text-ink-gray-6">Team</dt>
              <dd class="font-medium text-ink-gray-9">{{ t.agent_group }}</dd>
            </div>

            <div v-if="t.property">
              <dt class="text-ink-gray-6">Property</dt>
              <dd class="font-medium text-ink-gray-9">{{ t.property }}</dd>
            </div>

            <div v-if="t.unit">
              <dt class="text-ink-gray-6">Unit</dt>
              <dd class="font-medium text-ink-gray-9">{{ t.unit }}</dd>
            </div>

            <div v-if="t.svr_log_id">
              <dt class="text-ink-gray-6">SVR</dt>
              <dd class="font-medium text-ink-gray-9">{{ t.svr_log_id }}</dd>
            </div>

            <div>
              <dt class="text-ink-gray-6">Created</dt>
              <dd class="font-medium text-ink-gray-9">{{ formatDate(t.creation) }}</dd>
            </div>

            <div v-if="t.resolution_date">
              <dt class="text-ink-gray-6">Resolved</dt>
              <dd class="font-medium text-ink-gray-9">{{ formatDate(t.resolution_date) }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>

  <!-- Merge Confirmation Dialog -->
  <Dialog
    v-model="showMergeDialog"
    :options="{ title: 'Merge Ticket' }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <p class="text-p-base text-ink-gray-8">
          All comments and emails of ticket
          <span class="font-semibold">#{{ mergeTarget?.name }}</span>
          will be moved into the current ticket
          <span class="font-semibold">#{{ currentTicket?.name }}</span>.
        </p>
        <div class="flex items-center gap-2 rounded-md p-2 ring-1 ring-outline-gray-2">
          <LucideTriangleAlert class="size-4 text-yellow-500 flex-shrink-0" />
          <p class="text-sm text-ink-gray-7">This action is irreversible.</p>
        </div>
      </div>
    </template>
    <template #actions>
      <Button
        class="w-full"
        variant="solid"
        :label="`Merge #${mergeTarget?.name} into current ticket`"
        :loading="mergeResource.loading"
        :icon-left="LucideMerge"
        @click="confirmMerge"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { Button, Dialog, LoadingIndicator, createResource, toast } from "frappe-ui";
import { computed, inject, onMounted, ref, watch } from "vue";
import LucideHistory from "~icons/lucide/history";
import LucideMerge from "~icons/lucide/merge";
import LucideTriangleAlert from "~icons/lucide/triangle-alert";
import { TicketSymbol } from "@/types";

const ticket = inject(TicketSymbol);

const raisedBy = computed(() => ticket?.value?.doc?.raised_by || "");
const currentTicket = computed(() => ticket?.value?.doc);

const historyResource = createResource({
  url: "helpdesk.api.svr.get_previous_ticket_history",
  makeParams() {
    return {
      email: ticket?.value?.doc?.raised_by || null,
      current_ticket_id: ticket?.value?.doc?.name || null,
    };
  },
  auto: false,
});

onMounted(() => {
  if (ticket?.value?.doc?.raised_by) {
    historyResource.reload();
  }
});

watch(
  () => ticket?.value?.doc?.raised_by,
  (newEmail) => {
    if (newEmail) {
      historyResource.reload();
    }
  }
);

const loading = computed(() => historyResource.loading);
const tickets = computed(() => historyResource.data || []);

// Merge state
const showMergeDialog = ref(false);
const mergeTarget = ref<any>(null);

function openMergeConfirm(t: any) {
  mergeTarget.value = t;
  showMergeDialog.value = true;
}

const mergeResource = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.merge_ticket",
  onSuccess() {
    toast.success("Ticket merged successfully");
    showMergeDialog.value = false;
    mergeTarget.value = null;
    historyResource.reload();
  },
  onError(err: any) {
    toast.error(err?.message || "Failed to merge ticket");
  },
});

function confirmMerge() {
  if (!mergeTarget.value || !currentTicket.value) return;
  mergeResource.submit({
    source: mergeTarget.value.name,
    target: currentTicket.value.name,
  });
}

const formatDate = (dateString: string) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

const getStatusClass = (status: string) => {
  const map: Record<string, string> = {
    Open: "bg-yellow-100 text-yellow-800",
    Replied: "bg-blue-100 text-blue-800",
    Resolved: "bg-green-100 text-green-800",
    Closed: "bg-surface-gray-3 text-ink-gray-6",
  };
  return map[status] || "bg-surface-gray-3 text-ink-gray-6";
};

const getPriorityClass = (priority: string) => {
  const map: Record<string, string> = {
    Urgent: "bg-red-100 text-red-800",
    High: "bg-orange-100 text-orange-800",
    Medium: "bg-yellow-100 text-yellow-800",
    Low: "bg-green-100 text-green-800",
  };
  return map[priority] || "bg-surface-gray-2 text-ink-gray-7";
};
</script>
