<template>
  <Dialog
    v-model="show"
    :options="{
      title: 'Quick SVR Log',
      size: '2xl',
      actions: [
        {
          label: 'Cancel',
          variant: 'outline',
          theme: 'gray',
          onClick: closeDialog
        },
        {
          label: 'Create SVR',
          variant: 'solid',
          theme: 'gray',
          loading: createSVRLogResource.loading,
          onClick: handleSubmit
        }
      ]
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <!-- Paste SVR Data Section -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-medium text-blue-900">📋 Paste SVR Data</h3>
          </div>
          
          <div class="space-y-3">
            <FormControl
              type="textarea"
              label="Paste SVR formatted text here"
              v-model="pasteData"
              placeholder="Zone 5, SVR-EPF-25/31604&#10;27/09/2025 12:00:00 AM&#10;MURDIH TOWER JVC&#10;EP-329/404&#10;16193&#10;Tenant Name&#10;Carpentry&#10;DOOR ISSUE"
              :rows="7"
            />
            <div class="flex gap-2">
              <Button 
                variant="solid" 
                size="sm" 
                @click="parsePastedData"
                :disabled="!pasteData.trim()"
                theme="blue"
              >
                Parse & Fill Form
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                @click="clearPasteData"
                :disabled="!pasteData.trim()"
              >
                Clear
              </Button>
            </div>
            <div class="text-xs text-blue-700 bg-blue-100 p-2 rounded">
              <strong>Format:</strong> Zone, SVR Number, Date, Property, Unit, Contract Number (optional), Tenant Name (optional), Service Category (optional), Remarks
            </div>
          </div>
        </div>

        <!-- Parse Results Section - Show Errors Only -->
        <div v-if="showParseResults && Object.values(parseResults).some((result: any) => !result.parsed)" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-medium text-red-900">📊 Parsing Results - Errors Only</h3>
            <Button 
              variant="ghost" 
              size="sm" 
              @click="showParseResults = false"
              class="text-red-600 hover:text-red-700"
            >
              Hide
            </Button>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div v-for="(result, key) in parseResults" :key="key" 
              v-show="!result.parsed"
              class="flex items-start space-x-2 p-2 rounded bg-red-100 border border-red-200">
              <div class="flex-shrink-0 mt-0.5">
                <span class="text-red-600">❌</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="font-medium capitalize text-red-800">
                  {{ String(key).replace(/([A-Z])/g, ' $1').trim() }}
                </div>
                <div v-if="result.value" class="text-gray-600 truncate">"{{ result.value }}"</div>
                <div class="mt-1 text-red-700">
                  {{ result.message }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Basic Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormControl
            type="date"
            label="Date"
            v-model="formData.date"
            required
            :error="errors.date"
          />
          
          <FormControl
            type="text"
            label="SVR Number"
            v-model="formData.svr_number"
            placeholder="Enter SVR number..."
            required
            :error="errors.svr_number"
          />
        </div>

        <!-- Property and Location -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Property <span class="text-red-600">*</span>
            </label>
            <Autocomplete
              v-model="formData.property"
              :options="propertyOptions ?? []"
              @update:modelValue="onPropertyChange"
              placeholder="Select property..."
              size="sm"
            />
            <div v-if="errors.property" class="text-sm text-red-600 mt-1">{{ errors.property }}</div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Unit</label>
            <Autocomplete
              v-model="formData.unit"
              :options="unitOptions ?? []"
              placeholder="Select unit..."
              :disabled="!formData.property || unitResource.loading"
              size="sm"
            />
            <div v-if="unitResource.loading" class="text-xs text-gray-500 mt-1">Loading units...</div>
            <div v-else-if="formData.property && unitOptions.length === 0" class="text-xs text-gray-500 mt-1">No units found for this property</div>
            <div v-if="errors.unit" class="text-sm text-red-600 mt-1">{{ errors.unit }}</div>
          </div>
        </div>

        <!-- Tenant Name and Contract Number -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormControl
            type="text"
            label="Tenant Name"
            v-model="formData.tenant_name"
            placeholder="Enter tenant name (optional)..."
            :error="errors.tenant_name"
          />

          <FormControl
            type="text"
            label="Contract Number"
            v-model="formData.contract_number"
            placeholder="Enter contract number (optional)..."
            :error="errors.contract_number"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Zone</label>
            <Autocomplete
              v-model="formData.zone"
              :options="zoneOptions ?? []"
              @update:modelValue="onZoneChange"
              placeholder="Select zone..."
              size="sm"
            />
            <div v-if="errors.zone" class="text-sm text-red-600 mt-1">{{ errors.zone }}</div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Service Category</label>
            <Autocomplete
              v-model="formData.service_category"
              :options="serviceCategoryOptions ?? []"
              placeholder="Select service category..."
              size="sm"
            />
            <div v-if="errors.service_category" class="text-sm text-red-600 mt-1">{{ errors.service_category }}</div>
          </div>
        </div>

        <!-- Assignment and Priority -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Assigned To
              <span v-if="formData.zone && suggestedSupervisor" class="text-xs text-blue-600 ml-1">
                (Auto-assigned from zone)
              </span>
            </label>
            <Link
              class="form-control"
              :value="getUser(formData.assigned_to).full_name"
              doctype="User"
              :filters="{ name: ['like', '%@emiratesproperties.com'] }"
              @change="(option: string) => (formData.assigned_to = option)"
              placeholder="Select user to assign..."
            >
              <template #prefix>
                <UserAvatar class="mr-2 !h-4 !w-4" :name="formData.assigned_to" />
              </template>
            </Link>
          </div>

          <FormControl
            type="select"
            label="Priority"
            v-model="formData.priority"
            :options="priorityOptions"
            placeholder="Select priority..."
            :error="errors.priority"
          />
        </div>

        <!-- Remarks -->
        <FormControl
          type="textarea"
          label="Remarks"
          v-model="formData.remarks"
          placeholder="Enter any remarks or notes"
          :rows="3"
          :error="errors.remarks"
        />

        <!-- Supervisor Inspection Required -->
        <div class="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <input
            type="checkbox"
            id="supervisor-inspection"
            v-model="formData.supervisor_inspection_required"
            class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <div class="flex-1">
            <label
              for="supervisor-inspection"
              class="block text-sm font-medium text-gray-900 cursor-pointer"
            >
              Supervisor Inspection Required
            </label>
            <p class="text-xs text-blue-700 mt-1">
              Check this if supervisor inspection is required before marking this log as completed.
            </p>
          </div>
        </div>

        <!-- Tags Section -->
        <div v-if="tagsOptions.length > 0" class="space-y-2">
          <label class="block text-sm font-medium text-gray-700">
            Tags
            <span class="text-gray-500 text-xs font-normal ml-1">(Optional)</span>
          </label>
          <div v-if="tagsResource.loading" class="text-sm text-gray-500">
            Loading tags...
          </div>
          <div v-else class="flex flex-wrap gap-2">
            <button
              v-for="tag in tagsOptions"
              :key="tag.name"
              type="button"
              @click="toggleTag(tag.name)"
              class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-150 cursor-pointer border-2"
              :class="[
                isTagSelected(tag.name)
                  ? 'border-transparent shadow-sm'
                  : 'border-gray-300 bg-white hover:border-gray-400'
              ]"
              :style="{
                backgroundColor: isTagSelected(tag.name) ? tag.tag_color : 'white',
                color: isTagSelected(tag.name) ? getContrastColor(tag.tag_color) : '#374151'
              }"
            >
              <span class="w-2 h-2 rounded-full mr-2" :style="{ backgroundColor: isTagSelected(tag.name) ? 'currentColor' : tag.tag_color }"></span>
              {{ tag.tag_name }}
              <span v-if="isTagSelected(tag.name)" class="ml-1.5">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                </svg>
              </span>
            </button>
          </div>
          <div v-if="formData.tags.length > 0" class="text-xs text-gray-600 mt-2">
            {{ formData.tags.length }} tag(s) selected
          </div>
        </div>

        <!-- Checking Similar Logs Loader -->
        <div v-if="checkingSimilarLogs" class="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center">
          <svg class="animate-spin h-4 w-4 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-sm text-blue-800">Checking for similar maintenance logs...</span>
        </div>
       
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { Link, Autocomplete, UserAvatar } from "@/components";
import { Dialog, FormControl, createResource, toast, Button } from "frappe-ui";
import { ref, computed, watch, nextTick } from "vue";
import { useUserStore } from "@/stores/user";

interface Props {
  ticketId: string;
}

interface E {
  (event: "success"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<E>();
const show = defineModel<boolean>({ default: false });

const { getUser } = useUserStore();

// Reactive data
const formData = ref({
  date: new Date().toISOString().split('T')[0],
  svr_number: '',
  ticket_id: props.ticketId,
  property: null as string | null,
  unit: null as string | null,
  tenant_name: '',
  contract_number: '',
  zone: null as string | null,
  service_category: null as string | null,
  assigned_to: '',
  priority: null as string | null,
  remarks: '',
  supervisor_inspection_required: false,
  tags: [] as string[]
});

const errors = ref<Record<string, string>>({});
const suggestedSupervisor = ref('');
const pasteData = ref('');
const parseResults = ref({
  zone: { parsed: false, value: '', message: '' },
  svrNumber: { parsed: false, value: '', message: '' },
  date: { parsed: false, value: '', message: '' },
  property: { parsed: false, value: '', message: '' },
  unit: { parsed: false, value: '', message: '' },
  contractNumber: { parsed: false, value: '', message: '' },
  tenant: { parsed: false, value: '', message: '' },
  serviceCategory: { parsed: false, value: '', message: '' },
  remarks: { parsed: false, value: '', message: '' }
});
const showParseResults = ref(false);
const similarLogs = ref<any[]>([]);
const showSimilarLogs = ref(false);
const checkingSimilarLogs = ref(false);

// Resources for dropdown options
const propertyResource = createResource({
  url: "frappe.client.get_list",
  makeParams: () => ({
    doctype: "PM Property",
    fields: JSON.stringify(["name", "property_name"]),
    limit_page_length: 999
  }),
  auto: true
});

const unitResource = createResource({
  url: "frappe.client.get_list",
  makeParams: () => {
    const params = {
      doctype: "PM Unit",
      fields: JSON.stringify(["name", "unit_code", "pact_id", "property"]),
      limit_page_length: 999
    }
    
    // Only add property filter if a property is selected
    if (formData.value.property) {
      const propertyValue = formData.value.property?.value || formData.value.property
      params.filters = JSON.stringify([["property", "=", propertyValue]])
    }
    
    return params
  },
  auto: false
});

const zoneResource = createResource({
  url: "frappe.client.get_list",
  makeParams: () => ({
    doctype: "PM FM Zone",
    fields: JSON.stringify(["name", "fm_supervisor"]),
    limit_page_length: 999
  }),
  auto: true
});

const serviceCategoryResource = createResource({
  url: "frappe.client.get_list",
  makeParams: () => ({
    doctype: "EPFM Service Category",
    fields: JSON.stringify(["name"]),
    limit_page_length: 999
  }),
  auto: true
});

const tagsResource = createResource({
  url: "frappe.client.get_list",
  makeParams: () => ({
    doctype: "EPFM Maintenance Tag",
    fields: JSON.stringify(["name", "tag_name", "tag_color"]),
    filters: JSON.stringify([["is_active", "=", 1]]),
    order_by: "display_order asc",
    limit_page_length: 999
  }),
  auto: true
});

// Create resource for SVR Log
const createSVRLogResource = createResource({
  url: "helpdesk.api.svr.create_svr_log",
  onSuccess: (data: any) => {
    console.log('SVR Log created successfully:', data);
    const message = data.name 
      ? `SVR Log ${data.name} created successfully!` 
      : (data.message || "SVR Log created successfully!");
    toast.success(message);
    emit('success');
    closeDialog();
  },
  onError: (error: any) => {
    console.error('Error creating SVR log:', error);
    let errorMessage = "Failed to create SVR log. Please try again.";
    
    if (error && typeof error === 'object') {
      if (error.messages && Array.isArray(error.messages) && error.messages.length > 0) {
        errorMessage = error.messages[0];
      } else if (error.message) {
        errorMessage = error.message;
      }
    } else if (typeof error === 'string') {
      errorMessage = error;
    }
    
    toast.error(errorMessage);
  }
});

// Computed options
const propertyOptions = computed(() => {
  if (!propertyResource.data || !Array.isArray(propertyResource.data)) return [];
  return propertyResource.data.map((property: any) => ({
    label: property.property_name || property.name,
    value: property.name
  }));
});

const unitOptions = computed(() => {
  if (!unitResource.data || !Array.isArray(unitResource.data)) return [];
  return unitResource.data.map((unit: any) => ({
    label: unit.pact_id ? `${unit.pact_id} (${unit.unit_code || unit.name})` : (unit.unit_code || unit.name),
    value: unit.name
  }));
});

const zoneOptions = computed(() => {
  if (!zoneResource.data || !Array.isArray(zoneResource.data)) return [];
  return zoneResource.data.map((zone: any) => ({
    label: zone.name,
    value: zone.name
  }));
});

const serviceCategoryOptions = computed(() => {
  if (!serviceCategoryResource.data || !Array.isArray(serviceCategoryResource.data)) return [];
  return serviceCategoryResource.data.map((category: any) => ({
    label: category.name,
    value: category.name
  }));
});

const priorityOptions = computed(() => [
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
  { label: 'Urgent', value: 'Urgent' }
]);

const tagsOptions = computed(() => {
  if (!tagsResource.data || !Array.isArray(tagsResource.data)) return [];
  return tagsResource.data.map((tag: any) => ({
    name: tag.name,
    tag_name: tag.tag_name || tag.name,
    tag_color: tag.tag_color || '#6B7280'
  }));
});

// Methods
const resetForm = () => {
  formData.value = {
    date: new Date().toISOString().split('T')[0],
    svr_number: '',
    ticket_id: props.ticketId,
    property: null,
    unit: null,
    tenant_name: '',
    contract_number: '',
    zone: null,
    service_category: null,
    assigned_to: '',
    priority: null,
    remarks: '',
    supervisor_inspection_required: false,
    tags: []
  };
  errors.value = {};
  suggestedSupervisor.value = '';
  similarLogs.value = [];
  showSimilarLogs.value = false;
  checkingSimilarLogs.value = false;
  pasteData.value = '';
  showParseResults.value = false;
};

const toggleTag = (tagName: string) => {
  const index = formData.value.tags.indexOf(tagName);
  if (index > -1) {
    formData.value.tags.splice(index, 1);
  } else {
    formData.value.tags.push(tagName);
  }
};

const isTagSelected = (tagName: string) => {
  return formData.value.tags.includes(tagName);
};

const getContrastColor = (hexColor: string) => {
  if (!hexColor) return '#000000';
  
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
};

const parsePastedData = () => {
  if (!pasteData.value.trim()) {
    toast.error('Please paste SVR data first');
    return;
  }

  Object.keys(parseResults.value).forEach(key => {
    parseResults.value[key as keyof typeof parseResults.value] = { parsed: false, value: '', message: '' };
  });

  try {
    const lines = pasteData.value.trim().split('\n').map(line => line.trim()).filter(line => line.length > 0);
    
    if (lines.length < 4) {
      toast.error('Invalid format. Minimum 4 lines required: Zone/SVR, Date, Property, Unit');
      return;
    }

    // Parse first line
    const firstLine = lines[0];
    const zoneMatch = firstLine.match(/^(.+?),\s*(.+)$/);
    
    if (zoneMatch) {
      const [, zonePart, svrPart] = zoneMatch;
      const zoneText = zonePart.trim().replace(/^Zone\s+/i, '');
      parseResults.value.zone.value = zoneText;
      
      const matchingZone = zoneOptions.value.find((z: any) => 
        z.label.toLowerCase() === zoneText.toLowerCase() ||
        z.label.toLowerCase().includes(zoneText.toLowerCase()) ||
        zoneText.toLowerCase().includes(z.label.toLowerCase())
      );
      
      if (matchingZone) {
        formData.value.zone = matchingZone.value;
        parseResults.value.zone.parsed = true;
        parseResults.value.zone.message = `Matched to: ${matchingZone.label}`;
      } else {
        parseResults.value.zone.parsed = false;
        parseResults.value.zone.message = `Zone "${zoneText}" not found in available options`;
      }
      
      const svrNumberText = svrPart.trim();
      formData.value.svr_number = svrNumberText;
      parseResults.value.svrNumber.parsed = true;
      parseResults.value.svrNumber.value = svrNumberText;
      parseResults.value.svrNumber.message = 'Successfully parsed';
    } else {
      parseResults.value.zone.message = 'Could not parse zone from first line';
      parseResults.value.svrNumber.message = 'Could not parse SVR number from first line';
    }

    // Parse date
    if (lines[1]) {
      const dateStr = lines[1].trim();
      parseResults.value.date.value = dateStr;
      const parsedDate = parseDate(dateStr);
      if (parsedDate) {
        formData.value.date = parsedDate;
        parseResults.value.date.parsed = true;
        parseResults.value.date.message = `Parsed as: ${parsedDate}`;
      } else {
        parseResults.value.date.parsed = false;
        parseResults.value.date.message = 'Could not parse date format';
      }
    } else {
      parseResults.value.date.message = 'Date line not found';
    }

    // Property name
    if (lines[2]) {
      const propertyName = lines[2].trim();
      parseResults.value.property.value = propertyName;
      
      const matchingProperty = propertyOptions.value.find((p: any) => 
        p.label.toLowerCase() === propertyName.toLowerCase()
      );
      
      if (matchingProperty) {
        formData.value.property = matchingProperty.value;
        parseResults.value.property.parsed = true;
        parseResults.value.property.message = `Matched to: ${matchingProperty.label}`;
        onPropertyChange(matchingProperty.value);
      } else {
        parseResults.value.property.parsed = false;
        parseResults.value.property.message = `Property "${propertyName}" not found in available options`;
      }
    } else {
      parseResults.value.property.message = 'Property line not found';
    }

    // Unit
    if (lines[3]) {
      const unitText = lines[3].trim();
      parseResults.value.unit.value = unitText;
      setTimeout(() => {
        const matchingUnit = unitOptions.value.find((u: any) => {
          const unitData = unitResource.data?.find((unit: any) => unit.name === u.value);
          if (unitData) {
            const unitTextLower = unitText.toLowerCase().trim();
            // Check against pact_id, unit_code, or name (with trimming)
            if (unitData.pact_id && unitData.pact_id.toLowerCase().trim() === unitTextLower) {
              return true;
            }
            if (unitData.unit_code && unitData.unit_code.toLowerCase().trim() === unitTextLower) {
              return true;
            }
            if (unitData.name && unitData.name.toLowerCase().trim() === unitTextLower) {
              return true;
            }
            // Also check if the text appears in the label (which includes both pact_id and unit_code)
            if (u.label && u.label.toLowerCase().includes(unitTextLower)) {
              const labelParts = u.label.toLowerCase().split('(');
              if (labelParts[0].trim() === unitTextLower) {
                return true;
              }
            }
          }
          return false;
        });
        
        if (matchingUnit) {
          formData.value.unit = matchingUnit.value;
          parseResults.value.unit.parsed = true;
          parseResults.value.unit.message = `Matched to: ${matchingUnit.label}`;
        } else {
          parseResults.value.unit.parsed = false;
          parseResults.value.unit.message = `Unit "${unitText}" not found in available options`;
        }
        
        showParseResults.value = true;
      }, 500);
    } else {
      parseResults.value.unit.message = 'Unit line not found';
    }

    // Contract Number
    if (lines[4]) {
      const contractNumberText = lines[4].trim();
      parseResults.value.contractNumber.value = contractNumberText;
      if (contractNumberText.toLowerCase() !== 'none' && contractNumberText.length > 0) {
        formData.value.contract_number = contractNumberText;
        parseResults.value.contractNumber.parsed = true;
        parseResults.value.contractNumber.message = 'Successfully parsed';
      } else {
        parseResults.value.contractNumber.parsed = true;
        parseResults.value.contractNumber.message = 'Skipped (None or empty)';
      }
    } else {
      parseResults.value.contractNumber.parsed = true;
      parseResults.value.contractNumber.message = 'Not provided (optional)';
    }

    // Tenant name
    if (lines[5]) {
      const tenantName = lines[5].trim();
      parseResults.value.tenant.value = tenantName;
      if (tenantName.toLowerCase() !== 'none' && tenantName.length > 0) {
        formData.value.tenant_name = tenantName;
        parseResults.value.tenant.parsed = true;
        parseResults.value.tenant.message = 'Successfully parsed';
      } else {
        parseResults.value.tenant.parsed = true;
        parseResults.value.tenant.message = 'Skipped (None or empty)';
      }
    } else {
      parseResults.value.tenant.parsed = true;
      parseResults.value.tenant.message = 'Not provided (optional)';
    }

    // Service category
    if (lines[6]) {
      const serviceCategoryText = lines[6].trim();
      parseResults.value.serviceCategory.value = serviceCategoryText;
      if (serviceCategoryText.toLowerCase() !== 'none' && serviceCategoryText.length > 0) {
        const matchingCategory = serviceCategoryOptions.value.find((cat: any) => 
          cat.label.toLowerCase() === serviceCategoryText.toLowerCase() ||
          cat.label.toLowerCase().includes(serviceCategoryText.toLowerCase()) ||
          serviceCategoryText.toLowerCase().includes(cat.label.toLowerCase())
        );
        if (matchingCategory) {
          formData.value.service_category = matchingCategory.value;
          parseResults.value.serviceCategory.parsed = true;
          parseResults.value.serviceCategory.message = `Matched to: ${matchingCategory.label}`;
        } else {
          parseResults.value.serviceCategory.parsed = false;
          parseResults.value.serviceCategory.message = `Service Category "${serviceCategoryText}" not found in available options`;
        }
      } else {
        parseResults.value.serviceCategory.parsed = true;
        parseResults.value.serviceCategory.message = 'Skipped (None or empty)';
      }
    } else {
      parseResults.value.serviceCategory.parsed = true;
      parseResults.value.serviceCategory.message = 'Not provided (optional)';
    }

    // Remarks
    const remarkLines = [];
    for (let i = 7; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line && line.toLowerCase() !== 'none') {
        remarkLines.push(line);
      }
    }
    
    if (remarkLines.length > 0) {
      const remarksText = remarkLines.join('\n');
      formData.value.remarks = remarksText;
      parseResults.value.remarks.parsed = true;
      parseResults.value.remarks.value = remarksText;
      parseResults.value.remarks.message = 'Successfully parsed';
    } else {
      parseResults.value.remarks.parsed = true;
      parseResults.value.remarks.message = 'Not provided (optional)';
    }

    if (formData.value.zone) {
      onZoneChange(formData.value.zone);
    }
    
    if (!lines[3]) {
      showParseResults.value = true;
    }
    
    const unparsedFields = Object.entries(parseResults.value)
      .filter(([key, result]) => !result.parsed && key !== 'unit')
      .map(([key]) => key);
    
    if (unparsedFields.length > 0) {
      toast.warning('Some fields could not be parsed automatically. Please review the results below.');
    } else {
      toast.success('SVR data parsed successfully!');
    }
    
  } catch (error) {
    console.error('Error parsing pasted data:', error);
    toast.error('Error parsing the pasted data. Please check the format and try again.');
  }
};

const parseDate = (dateStr: string) => {
  try {
    const cleanDate = dateStr.replace(/\s+\d{1,2}:\d{2}:\d{2}(\s+(AM|PM))?/i, '').trim();
    
    const ddmmyyyyMatch = cleanDate.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
    if (ddmmyyyyMatch) {
      const [, day, month, year] = ddmmyyyyMatch;
      const paddedDay = day.padStart(2, '0');
      const paddedMonth = month.padStart(2, '0');
      return `${year}-${paddedMonth}-${paddedDay}`;
    }
    
    const ddmmyyyyHyphenMatch = cleanDate.match(/(\d{1,2})-(\d{1,2})-(\d{4})/);
    if (ddmmyyyyHyphenMatch) {
      const [, day, month, year] = ddmmyyyyHyphenMatch;
      const paddedDay = day.padStart(2, '0');
      const paddedMonth = month.padStart(2, '0');
      return `${year}-${paddedMonth}-${paddedDay}`;
    }
    
    const dateMatch = cleanDate.match(/(\d{1,2})-(\w{3})-(\d{2})/);
    if (dateMatch) {
      const [, day, month, year] = dateMatch;
      const monthMap: Record<string, string> = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
        'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
      };
      
      const fullYear = parseInt(year) + (parseInt(year) > 50 ? 1900 : 2000);
      const paddedDay = day.padStart(2, '0');
      const monthNum = monthMap[month];
      
      if (monthNum) {
        return `${fullYear}-${monthNum}-${paddedDay}`;
      }
    }

    toast.error('Could not parse date. Please use DD/MM/YYYY format.');
    return null;
  } catch (error) {
    console.error('Date parsing error:', error);
    return null;
  }
};

const clearPasteData = () => {
  pasteData.value = '';
};

const onPropertyChange = (selectedValue: string | null) => {
  formData.value.unit = null;
  if (selectedValue) {
    // Fetch units with new property filter
    unitResource.fetch();
  }
};

const onZoneChange = (selectedValue: string | null) => {
  if (selectedValue && zoneResource.data) {
    const selectedZone = zoneResource.data.find((zone: any) => 
      zone.name === selectedValue
    );
    if (selectedZone && selectedZone.fm_supervisor) {
      formData.value.assigned_to = selectedZone.fm_supervisor;
      suggestedSupervisor.value = selectedZone.fm_supervisor;
    }
  }
};

const validateForm = () => {
  errors.value = {};
  
  if (!formData.value.date) {
    errors.value.date = 'Date is required';
  }
  
  if (!formData.value.svr_number || !formData.value.svr_number.trim()) {
    errors.value.svr_number = 'SVR Number is required';
  }
  
  if (!formData.value.property) {
    errors.value.property = 'Property is required';
  }
  
  return Object.keys(errors.value).length === 0;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    toast.error("Please fill in all required fields");
    return;
  }

  try {
    // Helper function to extract value from Autocomplete objects
    const extractValue = (field: any) => {
      if (!field) return null;
      if (typeof field === 'object' && field.value) return field.value;
      return field;
    };

    const submitData: Record<string, any> = {
      date: formData.value.date,
      svr_number: formData.value.svr_number,
      ticket_id: formData.value.ticket_id,
      property: extractValue(formData.value.property),
      unit: extractValue(formData.value.unit),
      tenant_name: formData.value.tenant_name || null,
      contract_number: formData.value.contract_number || null,
      zone: extractValue(formData.value.zone),
      service_category: extractValue(formData.value.service_category),
      assigned_to: formData.value.assigned_to || null,
      priority: extractValue(formData.value.priority),
      remarks: formData.value.remarks || null,
      supervisor_inspection_required: formData.value.supervisor_inspection_required ? 1 : 0,
      status: 'OPEN',
      work_done_by: 'EPFM'
    };

    // Include tags in the correct format
    if (formData.value.tags && formData.value.tags.length > 0) {
      submitData.tags = formData.value.tags;
    }

    // Remove null/empty values
    Object.keys(submitData).forEach(key => {
      if (submitData[key] === null || submitData[key] === '') {
        delete submitData[key];
      }
    });

    console.log('Submitting SVR data:', submitData);

    // Call the custom API endpoint
    await createSVRLogResource.submit({
      data: submitData
    });
  } catch (error) {
    console.error('Submit error:', error);
    toast.error("Error creating SVR log. Please check your data and try again.");
  }
};

const closeDialog = () => {
  show.value = false;
  nextTick(() => {
    resetForm();
  });
};

watch(show, (newValue) => {
  if (newValue) {
    resetForm();
  }
});

watch(() => formData.value?.property, (newProperty) => {
  if (newProperty) {
    // Fetch units when property changes
    unitResource.fetch();
  }
}, { immediate: false });
</script>
