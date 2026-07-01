const STORAGE_KEY = "hydration_tracker_v3_records";
const SCHEMA_VERSION = 1;
const EXPORT_APP = "HydrationTracker";
const EXPORT_VERSION = 1;
const EXPORT_SOURCE = "pwa-localStorage";
const DEFAULT_TARGET_ML = 2000;
const VALID_CATEGORIES = new Set(["water", "beverage", "food"]);
const VALID_MEALS = new Set(["breakfast", "lunch", "dinner", "snack", "none"]);

const COMMON_ITEMS = [
  {
    id: "water",
    name: "白水",
    category: "water",
    default_unit: "杯",
    default_amount: 250,
    base_type: "ml",
    water_ratio: 1.0,
  },
  {
    id: "milk",
    name: "牛奶",
    category: "beverage",
    default_unit: "杯",
    default_amount: 250,
    base_type: "ml",
    water_ratio: 0.87,
  },
  {
    id: "soy-milk",
    name: "豆浆",
    category: "beverage",
    default_unit: "杯",
    default_amount: 250,
    base_type: "ml",
    water_ratio: 0.9,
  },
  {
    id: "coffee",
    name: "咖啡",
    category: "beverage",
    default_unit: "杯",
    default_amount: 250,
    base_type: "ml",
    water_ratio: 0.98,
  },
  {
    id: "tea",
    name: "茶",
    category: "beverage",
    default_unit: "杯",
    default_amount: 250,
    base_type: "ml",
    water_ratio: 0.99,
  },
  {
    id: "soup",
    name: "汤",
    category: "beverage",
    default_unit: "碗",
    default_amount: 300,
    base_type: "ml",
    water_ratio: 0.95,
  },
  {
    id: "apple",
    name: "苹果",
    category: "food",
    default_unit: "个",
    default_amount: 180,
    base_type: "g",
    water_ratio: 0.86,
  },
  {
    id: "banana",
    name: "香蕉",
    category: "food",
    default_unit: "根",
    default_amount: 120,
    base_type: "g",
    water_ratio: 0.75,
  },
  {
    id: "peach",
    name: "桃子",
    category: "food",
    default_unit: "个",
    default_amount: 150,
    base_type: "g",
    water_ratio: 0.89,
  },
  {
    id: "watermelon",
    name: "西瓜",
    category: "food",
    default_unit: "份",
    default_amount: 300,
    base_type: "g",
    water_ratio: 0.91,
  },
  {
    id: "orange",
    name: "橙子",
    category: "food",
    default_unit: "个",
    default_amount: 180,
    base_type: "g",
    water_ratio: 0.87,
  },
  {
    id: "mandarin",
    name: "橘子",
    category: "food",
    default_unit: "个",
    default_amount: 100,
    base_type: "g",
    water_ratio: 0.87,
  },
  {
    id: "cucumber",
    name: "黄瓜",
    category: "food",
    default_unit: "根",
    default_amount: 200,
    base_type: "g",
    water_ratio: 0.95,
  },
  {
    id: "tomato",
    name: "西红柿",
    category: "food",
    default_unit: "个",
    default_amount: 150,
    base_type: "g",
    water_ratio: 0.94,
  },
  {
    id: "green-pepper",
    name: "青椒",
    category: "food",
    default_unit: "个",
    default_amount: 100,
    base_type: "g",
    water_ratio: 0.92,
  },
  {
    id: "rice",
    name: "米饭",
    category: "food",
    default_unit: "碗",
    default_amount: 150,
    base_type: "g",
    water_ratio: 0.6,
  },
  {
    id: "bread",
    name: "面包",
    category: "food",
    default_unit: "片",
    default_amount: 30,
    base_type: "g",
    water_ratio: 0.35,
  },
  {
    id: "mantou",
    name: "馒头",
    category: "food",
    default_unit: "个",
    default_amount: 100,
    base_type: "g",
    water_ratio: 0.45,
  },
  {
    id: "egg",
    name: "鸡蛋",
    category: "food",
    default_unit: "个",
    default_amount: 50,
    base_type: "g",
    water_ratio: 0.75,
  },
  {
    id: "chicken-breast",
    name: "鸡胸肉",
    category: "food",
    default_unit: "份",
    default_amount: 100,
    base_type: "g",
    water_ratio: 0.65,
  },
  {
    id: "sausage",
    name: "香肠",
    category: "food",
    default_unit: "根",
    default_amount: 50,
    base_type: "g",
    water_ratio: 0.55,
  },
];

const ITEM_EMOJIS = Object.freeze({
  water: "💧",
  milk: "🥛",
  "soy-milk": "🥛",
  coffee: "☕",
  tea: "🍵",
  soup: "🥣",
  apple: "🍎",
  banana: "🍌",
  peach: "🍑",
  watermelon: "🍉",
  orange: "🍊",
  mandarin: "🍊",
  cucumber: "🥒",
  tomato: "🍅",
  "green-pepper": "🫑",
  rice: "🍚",
  bread: "🍞",
  mantou: "🍽️",
  egg: "🥚",
  "chicken-breast": "🍗",
  sausage: "🌭",
});

const CATEGORY_LABELS = {
  water: "白水",
  beverage: "饮品",
  food: "食物",
};

const MEAL_LABELS = {
  breakfast: "早餐",
  lunch: "午餐",
  dinner: "晚餐",
  snack: "加餐",
  none: "无餐次",
};

function getItemEmoji(item) {
  if (!item) {
    return "";
  }
  const itemId = item.id || item.item_id;
  if (ITEM_EMOJIS[itemId]) {
    return ITEM_EMOJIS[itemId];
  }
  const matchingItem = COMMON_ITEMS.find((entry) => entry.name === item.name);
  if (matchingItem) {
    return ITEM_EMOJIS[matchingItem.id] || "";
  }
  if (item.category === "water") {
    return "💧";
  }
  if (item.category === "beverage") {
    return "🥤";
  }
  return "🍽️";
}

function getProgressMessage(completionRate) {
  const rate = Number(completionRate);
  if (!Number.isFinite(rate) || rate <= 0) {
    return { emoji: "💧", text: "今天还没开始记录，先喝一杯水吧", level: "empty" };
  }
  if (rate <= 20) {
    return { emoji: "🌱", text: "今天刚开始，记得慢慢补水", level: "starting" };
  }
  if (rate <= 50) {
    return { emoji: "🚰", text: "已经开始补水啦，继续保持", level: "steady" };
  }
  if (rate < 80) {
    return { emoji: "💪", text: "进度不错，再喝一点", level: "good" };
  }
  if (rate < 100) {
    return { emoji: "✨", text: "快要完成目标啦", level: "almost" };
  }
  return { emoji: "🎉", text: "成功完成目标，今天做得很好", level: "complete" };
}

// Keep this key stable across upgrades. Backup and migration are handled
// through user-controlled JSON export and import.
function createEmptyData() {
  return {
    schema_version: SCHEMA_VERSION,
    records: [],
  };
}

function formatNumber(value) {
  const rounded = Math.round((Number(value) + Number.EPSILON) * 10) / 10;
  return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
}

function calculateEstimatedWaterMl(item, quantity) {
  const numericQuantity = Number(quantity);
  if (
    !item
    || !["ml", "g"].includes(item.base_type)
    || !Number.isFinite(numericQuantity)
    || numericQuantity <= 0
  ) {
    return null;
  }

  const estimated = numericQuantity * item.default_amount * item.water_ratio;
  return Math.round((estimated + Number.EPSILON) * 10) / 10;
}

function formatLocalDate(value) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatLocalTime(value) {
  const hours = String(value.getHours()).padStart(2, "0");
  const minutes = String(value.getMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

function isValidDateKey(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return false;
  }
  const [year, month, day] = value.split("-").map(Number);
  const candidate = new Date(year, month - 1, day, 12);
  return candidate.getFullYear() === year
    && candidate.getMonth() === month - 1
    && candidate.getDate() === day;
}

function isValidTimeValue(value) {
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(value);
}

function isValidRecord(record) {
  return Boolean(
    record
    && typeof record === "object"
    && typeof record.id === "string"
    && record.id.length > 0
    && /^\d{4}-\d{2}-\d{2}$/.test(record.date)
    && /^\d{2}:\d{2}$/.test(record.time)
    && VALID_CATEGORIES.has(record.category)
    && VALID_MEALS.has(record.meal)
    && typeof record.item_id === "string"
    && record.item_id.length > 0
    && typeof record.name === "string"
    && record.name.length > 0
    && Number.isFinite(record.quantity)
    && record.quantity > 0
    && typeof record.default_unit === "string"
    && record.default_unit.length > 0
    && Number.isFinite(record.default_amount)
    && record.default_amount > 0
    && ["ml", "g"].includes(record.base_type)
    && Number.isFinite(record.water_ratio)
    && record.water_ratio >= 0
    && record.water_ratio <= 1
    && Number.isFinite(record.estimated_water_ml)
    && record.estimated_water_ml >= 0
    && typeof record.note === "string"
    && typeof record.created_at === "string"
  );
}

function validateDataContainer(data) {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    throw new Error("本地数据格式不正确");
  }
  if (data.schema_version !== SCHEMA_VERSION) {
    throw new Error("本地数据版本暂不支持，请勿覆盖原数据");
  }
  if (!Array.isArray(data.records) || !data.records.every(isValidRecord)) {
    throw new Error("本地记录格式不正确，请勿覆盖原数据");
  }
  return data;
}

function parseStoredData(rawValue) {
  return validateDataContainer(JSON.parse(rawValue));
}

function writeDataToStorage(storage, data) {
  validateDataContainer(data);
  storage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function loadDataFromStorage(storage) {
  const rawValue = storage.getItem(STORAGE_KEY);
  if (rawValue === null) {
    const emptyData = createEmptyData();
    writeDataToStorage(storage, emptyData);
    return emptyData;
  }
  return parseStoredData(rawValue);
}

function getRecordsForDate(data, targetDate) {
  return data.records.filter((record) => record.date === targetDate);
}

function calculateSummary(data, targetDate, targetMl = DEFAULT_TARGET_ML) {
  const records = getRecordsForDate(data, targetDate);
  const totalWaterMl = Math.round(
    (records.reduce((total, record) => total + record.estimated_water_ml, 0)
      + Number.EPSILON) * 10
  ) / 10;
  const completionRate = Math.round(
    ((totalWaterMl / targetMl) * 100 + Number.EPSILON) * 10
  ) / 10;
  const remainingMl = Math.round(
    (Math.max(targetMl - totalWaterMl, 0) + Number.EPSILON) * 10
  ) / 10;
  return {
    totalWaterMl,
    completionRate,
    remainingMl,
    recordCount: records.length,
  };
}

function summarizeRecordsByDate(data, targetMl = DEFAULT_TARGET_ML) {
  const dates = [...new Set(data.records.map((record) => record.date))];
  return dates
    .sort((left, right) => right.localeCompare(left))
    .map((date) => ({ date, ...calculateSummary(data, date, targetMl) }));
}

function buildCalendarMonth(
  data,
  year,
  monthIndex,
  today = new Date(),
  targetMl = DEFAULT_TARGET_ML
) {
  const firstDay = new Date(year, monthIndex, 1, 12);
  const mondayOffset = (firstDay.getDay() + 6) % 7;
  const gridStart = new Date(year, monthIndex, 1 - mondayOffset, 12);
  const todayKey = formatLocalDate(today);
  const days = [];

  for (let index = 0; index < 42; index += 1) {
    const date = new Date(gridStart);
    date.setDate(gridStart.getDate() + index);
    const dateKey = formatLocalDate(date);
    const summary = calculateSummary(data, dateKey, targetMl);
    days.push({
      date: dateKey,
      dayNumber: date.getDate(),
      inCurrentMonth: date.getMonth() === monthIndex,
      isToday: dateKey === todayKey,
      hasRecords: summary.recordCount > 0,
      totalWaterMl: summary.totalWaterMl,
      recordCount: summary.recordCount,
      completionRate: summary.completionRate,
    });
  }

  return {
    year,
    monthIndex,
    label: `${year}年${monthIndex + 1}月`,
    days,
  };
}

function buildRecentTrendData(
  data,
  endDate = new Date(),
  dayCount = 7,
  targetMl = DEFAULT_TARGET_ML
) {
  const lastDay = new Date(
    endDate.getFullYear(),
    endDate.getMonth(),
    endDate.getDate(),
    12
  );
  const points = [];

  for (let offset = dayCount - 1; offset >= 0; offset -= 1) {
    const date = new Date(lastDay);
    date.setDate(lastDay.getDate() - offset);
    const dateKey = formatLocalDate(date);
    const summary = calculateSummary(data, dateKey, targetMl);
    points.push({
      date: dateKey,
      totalWaterMl: summary.totalWaterMl,
      recordCount: summary.recordCount,
      completionRate: summary.completionRate,
    });
  }

  return { targetMl, points };
}

function deleteRecordForDateById(data, recordId, targetDate) {
  const matchIndex = data.records.findIndex(
    (record) => record.id === recordId && record.date === targetDate
  );
  if (matchIndex === -1) {
    return { data, deletedCount: 0 };
  }
  const records = data.records.filter((record, index) => index !== matchIndex);
  return {
    data: { ...data, records },
    deletedCount: 1,
  };
}

function resolveRecordDeletion(data, recordId, targetDate, confirmed) {
  if (!confirmed) {
    return { data, deletedCount: 0, cancelled: true };
  }
  return {
    ...deleteRecordForDateById(data, recordId, targetDate),
    cancelled: false,
  };
}

function clearRecordsForDate(data, targetDate) {
  const records = data.records.filter((record) => record.date !== targetDate);
  return {
    data: { ...data, records },
    deletedCount: data.records.length - records.length,
  };
}

function resolveDateClear(data, targetDate, confirmed) {
  if (!confirmed) {
    return { data, deletedCount: 0, cancelled: true };
  }
  return {
    ...clearRecordsForDate(data, targetDate),
    cancelled: false,
  };
}

function generateRecordId(records) {
  let recordId;
  do {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
      recordId = `rec_${globalThis.crypto.randomUUID()}`;
    } else {
      recordId = `rec_${Date.now()}_${Math.random().toString(16).slice(2)}`;
    }
  } while (records.some((record) => record.id === recordId));
  return recordId;
}

function buildRecordForDate({ item, quantity, meal, note, date, time, now, id }) {
  const numericQuantity = Number(quantity);
  const estimatedWaterMl = calculateEstimatedWaterMl(item, numericQuantity);
  if (!item || estimatedWaterMl === null) {
    throw new Error("请选择有效项目并输入大于 0 的数量");
  }
  if (!VALID_MEALS.has(meal)) {
    throw new Error("请选择有效餐次");
  }
  if (typeof note !== "string" || note.length > 500) {
    throw new Error("备注不能超过 500 个字符");
  }
  if (!isValidDateKey(date)) {
    throw new Error("请选择有效日期");
  }
  if (!isValidTimeValue(time)) {
    throw new Error("请输入有效时间，例如 08:30");
  }

  return {
    id,
    date,
    time,
    category: item.category,
    meal,
    item_id: item.id,
    name: item.name,
    quantity: numericQuantity,
    default_unit: item.default_unit,
    default_amount: item.default_amount,
    base_type: item.base_type,
    water_ratio: item.water_ratio,
    estimated_water_ml: estimatedWaterMl,
    note: note.trim(),
    created_at: now.toISOString(),
  };
}

function buildRecord({ item, quantity, meal, note, now, id }) {
  return buildRecordForDate({
    item,
    quantity,
    meal,
    note,
    date: formatLocalDate(now),
    time: formatLocalTime(now),
    now,
    id,
  });
}

function cloneRecords(records) {
  return records.map((record) => ({ ...record }));
}

function buildExportFilename(now = new Date()) {
  return `hydration-tracker-backup-${formatLocalDate(now)}.json`;
}

function buildExportPayload(data, now = new Date()) {
  const validatedData = validateDataContainer(data);
  return {
    app: EXPORT_APP,
    export_version: EXPORT_VERSION,
    schema_version: SCHEMA_VERSION,
    exported_at: now.toISOString(),
    source: EXPORT_SOURCE,
    storage_key: STORAGE_KEY,
    records: cloneRecords(validatedData.records),
  };
}

function validateBackupPayload(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("备份文件格式不正确");
  }
  if (payload.app !== EXPORT_APP) {
    throw new Error("备份文件不是 HydrationTracker 导出");
  }
  if (payload.export_version !== EXPORT_VERSION) {
    throw new Error("备份导出版本暂不支持");
  }
  if (payload.schema_version !== SCHEMA_VERSION) {
    throw new Error("备份数据版本暂不支持");
  }
  if (payload.source !== EXPORT_SOURCE) {
    throw new Error("备份来源与当前应用不匹配");
  }
  if (payload.storage_key !== STORAGE_KEY) {
    throw new Error("备份 storage key 与当前应用不匹配");
  }
  if (!Array.isArray(payload.records)) {
    throw new Error("备份记录格式不正确");
  }

  payload.records.forEach((record, index) => {
    if (!isValidRecord(record)) {
      throw new Error(`备份中的第 ${index + 1} 条记录格式不正确`);
    }
  });

  return payload;
}

function buildDataFromBackupPayload(payload) {
  const validatedPayload = validateBackupPayload(payload);
  return validateDataContainer({
    schema_version: SCHEMA_VERSION,
    records: cloneRecords(validatedPayload.records),
  });
}

function downloadTextFile(filename, content) {
  if (
    typeof Blob !== "function"
    || !globalThis.URL
    || typeof globalThis.URL.createObjectURL !== "function"
    || !document.body
  ) {
    throw new Error("当前浏览器不支持导出备份");
  }

  const blob = new Blob([content], { type: "application/json;charset=utf-8" });
  const downloadUrl = globalThis.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  globalThis.setTimeout(() => globalThis.URL.revokeObjectURL(downloadUrl), 0);
}

function restoreStorageReadyState() {
  storageReady = true;
  elements.storageStatus.textContent = "记录只保存在当前浏览器；刷新页面后仍可读取";
  elements.notice.classList.remove("error");
  elements.saveButton.disabled = false;
  elements.historyBackfillSaveButton.disabled = false;
  elements.exportButton.disabled = false;
}

const elements = {
  date: document.querySelector("#today-date"),
  total: document.querySelector("#total-water"),
  rate: document.querySelector("#completion-rate"),
  progressRing: document.querySelector("#progress-ring"),
  progressEncouragement: document.querySelector("#progress-encouragement"),
  remaining: document.querySelector("#remaining-water"),
  count: document.querySelector("#record-count"),
  notice: document.querySelector(".prototype-notice"),
  storageStatus: document.querySelector("#storage-status"),
  form: document.querySelector("#record-form"),
  item: document.querySelector("#item-name"),
  quantity: document.querySelector("#quantity"),
  quantityUnit: document.querySelector("#quantity-unit"),
  meal: document.querySelector("#meal"),
  note: document.querySelector("#note"),
  itemDefaults: document.querySelector("#item-defaults"),
  estimateMessage: document.querySelector("#estimate-message"),
  message: document.querySelector("#form-message"),
  saveButton: document.querySelector("#save-record"),
  clearButton: document.querySelector("#clear-today"),
  recordsMessage: document.querySelector("#records-message"),
  recordsList: document.querySelector("#records-list"),
  viewTabs: [...document.querySelectorAll(".view-tab")],
  views: {
    today: document.querySelector("#today-view"),
    history: document.querySelector("#history-view"),
    backup: document.querySelector("#backup-view"),
  },
  trendChart: document.querySelector("#trend-chart"),
  trendSummary: document.querySelector("#trend-summary"),
  calendarMonthLabel: document.querySelector("#calendar-month-label"),
  calendarGrid: document.querySelector("#calendar-grid"),
  previousMonthButton: document.querySelector("#previous-month"),
  nextMonthButton: document.querySelector("#next-month"),
  historyDetails: document.querySelector("#history-details"),
  historyDetailsTitle: document.querySelector("#history-details-title"),
  historyDetailsSummary: document.querySelector("#history-details-summary"),
  historyActionMessage: document.querySelector("#history-action-message"),
  historyClearDateButton: document.querySelector("#history-clear-date"),
  historyBackfillToggle: document.querySelector("#history-backfill-toggle"),
  historyBackfillPanel: document.querySelector("#history-backfill-panel"),
  historyBackfillTitle: document.querySelector("#history-backfill-title"),
  historyBackfillForm: document.querySelector("#history-backfill-form"),
  historyBackfillItem: document.querySelector("#history-item-name"),
  historyBackfillQuantity: document.querySelector("#history-quantity"),
  historyBackfillQuantityUnit: document.querySelector("#history-quantity-unit"),
  historyBackfillMeal: document.querySelector("#history-meal"),
  historyBackfillTime: document.querySelector("#history-time"),
  historyBackfillNote: document.querySelector("#history-note"),
  historyBackfillItemDefaults: document.querySelector("#history-item-defaults"),
  historyBackfillEstimateMessage: document.querySelector("#history-estimate-message"),
  historyBackfillMessage: document.querySelector("#history-backfill-message"),
  historyBackfillCancelButton: document.querySelector("#history-backfill-cancel"),
  historyBackfillSaveButton: document.querySelector("#history-backfill-save"),
  historyRecordsList: document.querySelector("#history-records-list"),
  exportButton: document.querySelector("#export-backup"),
  importFile: document.querySelector("#import-file"),
  importButton: document.querySelector("#import-backup"),
  backupFileName: document.querySelector("#backup-file-name"),
  backupMessage: document.querySelector("#backup-message"),
};

let appData = createEmptyData();
let storageReady = false;
let pendingImportFile = null;
let selectedHistoryDate = null;
let visibleCalendarMonth = new Date(
  new Date().getFullYear(),
  new Date().getMonth(),
  1,
  12
);

function getItemsByCategory(category) {
  return COMMON_ITEMS.filter((item) => item.category === category);
}

function selectedCategory() {
  return document.querySelector('input[name="category"]:checked').value;
}

function selectedItem() {
  return COMMON_ITEMS.find((item) => item.id === elements.item.value);
}

function selectedHistoryCategory() {
  const checked = document.querySelector('input[name="history-category"]:checked');
  return checked ? checked.value : "";
}

function selectedHistoryItem() {
  return COMMON_ITEMS.find((item) => item.id === elements.historyBackfillItem.value);
}

function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  element.className = className;
  element.textContent = text;
  return element;
}

function createSvgElement(tagName, attributes = {}, text = "") {
  const element = document.createElementNS("http://www.w3.org/2000/svg", tagName);
  for (const [name, value] of Object.entries(attributes)) {
    element.setAttribute(name, String(value));
  }
  if (text) {
    element.textContent = text;
  }
  return element;
}

function persistData(nextData) {
  if (!storageReady) {
    throw new Error("浏览器本地存储当前不可用");
  }
  writeDataToStorage(globalThis.localStorage, nextData);
  appData = nextData;
}

function renderItemOptions() {
  elements.item.replaceChildren();
  for (const item of getItemsByCategory(selectedCategory())) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = `${item.name} ${getItemEmoji(item)}`;
    elements.item.append(option);
  }
  renderEstimate();
}

function renderEstimate() {
  const item = selectedItem();
  const rawQuantity = elements.quantity.value.trim();

  if (!item) {
    elements.quantityUnit.textContent = "份";
    elements.itemDefaults.textContent = "请选择常用项目";
    elements.estimateMessage.textContent = "暂时无法计算估算水分";
    elements.estimateMessage.className = "error";
    return;
  }

  elements.quantityUnit.textContent = item.default_unit;
  elements.itemDefaults.textContent = `默认 1 ${item.default_unit} = ${formatNumber(item.default_amount)} ${item.base_type} · 含水率 ${item.water_ratio.toFixed(2)}`;

  if (rawQuantity === "") {
    elements.estimateMessage.textContent = "请输入数量以计算估算水分";
    elements.estimateMessage.className = "error";
    return;
  }

  const estimatedWater = calculateEstimatedWaterMl(item, rawQuantity);
  if (estimatedWater === null) {
    elements.estimateMessage.textContent = "数量必须是大于 0 的数字";
    elements.estimateMessage.className = "error";
    return;
  }

  elements.estimateMessage.textContent = `预计本次摄入水分：${formatNumber(estimatedWater)} ml`;
  elements.estimateMessage.className = "";
}

function renderHistoryItemOptions() {
  elements.historyBackfillItem.replaceChildren();
  for (const item of getItemsByCategory(selectedHistoryCategory())) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = `${item.name} ${getItemEmoji(item)}`;
    elements.historyBackfillItem.append(option);
  }
  renderHistoryEstimate();
}

function renderHistoryEstimate() {
  const item = selectedHistoryItem();
  const rawQuantity = elements.historyBackfillQuantity.value.trim();

  if (!item) {
    elements.historyBackfillQuantityUnit.textContent = "份";
    elements.historyBackfillItemDefaults.textContent = "请选择常用项目";
    elements.historyBackfillEstimateMessage.textContent = "暂时无法计算估算水分";
    elements.historyBackfillEstimateMessage.className = "error";
    return;
  }

  elements.historyBackfillQuantityUnit.textContent = item.default_unit;
  elements.historyBackfillItemDefaults.textContent = `默认 1 ${item.default_unit} = ${formatNumber(item.default_amount)} ${item.base_type} · 含水率 ${item.water_ratio.toFixed(2)}`;

  if (rawQuantity === "") {
    elements.historyBackfillEstimateMessage.textContent = "请输入数量以计算估算水分";
    elements.historyBackfillEstimateMessage.className = "error";
    return;
  }

  const estimatedWater = calculateEstimatedWaterMl(item, rawQuantity);
  if (estimatedWater === null) {
    elements.historyBackfillEstimateMessage.textContent = "数量必须是大于 0 的数字";
    elements.historyBackfillEstimateMessage.className = "error";
    return;
  }

  elements.historyBackfillEstimateMessage.textContent = `预计本次摄入水分：${formatNumber(estimatedWater)} ml`;
  elements.historyBackfillEstimateMessage.className = "";
}

function renderOverview() {
  const now = new Date();
  const summary = calculateSummary(appData, formatLocalDate(now));
  elements.date.textContent = new Intl.DateTimeFormat("zh-CN", {
    month: "long",
    day: "numeric",
    weekday: "short",
  }).format(now);
  elements.total.textContent = formatNumber(summary.totalWaterMl);
  elements.rate.textContent = formatNumber(summary.completionRate);
  elements.remaining.textContent = formatNumber(summary.remainingMl);
  elements.count.textContent = formatNumber(summary.recordCount);

  const visualRate = Math.min(Math.max(summary.completionRate, 0), 100);
  elements.progressRing.style.setProperty("--progress-value", `${visualRate}%`);
  elements.progressRing.setAttribute("aria-valuenow", String(visualRate));
  elements.progressRing.setAttribute(
    "aria-valuetext",
    `今日目标完成率 ${formatNumber(summary.completionRate)}%`
  );

  const message = getProgressMessage(summary.completionRate);
  elements.progressEncouragement.className = `progress-encouragement ${message.level}`;
  elements.progressEncouragement.replaceChildren(
    createTextElement("span", "progress-emoji", message.emoji),
    createTextElement("strong", "", message.text)
  );
  elements.progressEncouragement.firstElementChild.setAttribute("aria-hidden", "true");
}

function renderTodayRecords() {
  const today = formatLocalDate(new Date());
  const records = getRecordsForDate(appData, today);
  elements.recordsList.replaceChildren();
  elements.clearButton.disabled = !storageReady || records.length === 0;

  if (records.length === 0) {
    elements.recordsList.append(
      createTextElement("div", "empty-state", "今天还没有记录")
    );
    if (storageReady) {
      elements.recordsMessage.textContent = "今天共有 0 条记录";
      elements.recordsMessage.className = "records-message";
    }
    return;
  }

  elements.recordsMessage.textContent = `今天共有 ${records.length} 条记录`;
  elements.recordsMessage.className = "records-message";
  for (const record of [...records].reverse()) {
    const row = document.createElement("article");
    row.className = "record-item";

    const main = document.createElement("div");
    main.className = "record-main";
    const meta = document.createElement("p");
    meta.className = "record-meta";
    meta.append(
      createTextElement("span", "", record.time),
      createTextElement("span", "", CATEGORY_LABELS[record.category]),
      createTextElement("span", "", MEAL_LABELS[record.meal])
    );
    const name = createTextElement("h3", "record-name", record.name);
    const emoji = createTextElement("span", "record-emoji", getItemEmoji(record));
    emoji.setAttribute("aria-hidden", "true");
    name.append(" ", emoji);
    main.append(
      meta,
      name,
      createTextElement(
        "p",
        "record-quantity",
        `${formatNumber(record.quantity)} ${record.default_unit}`
      )
    );
    if (record.note) {
      main.append(createTextElement("p", "record-note", `备注：${record.note}`));
    }

    const side = document.createElement("div");
    side.className = "record-side";
    side.append(
      createTextElement(
        "p",
        "record-water",
        `${formatNumber(record.estimated_water_ml)} ml`
      )
    );
    const deleteButton = createTextElement("button", "delete-button", "删除");
    deleteButton.type = "button";
    deleteButton.setAttribute("aria-label", `删除 ${record.name}`);
    deleteButton.addEventListener("click", (event) => deleteRecord(record, event));
    side.append(deleteButton);

    row.append(main, side);
    elements.recordsList.append(row);
  }
}

function renderHistoryRecord(record) {
  const row = document.createElement("article");
  row.className = "record-item history-record-item";

  const main = document.createElement("div");
  main.className = "record-main";
  const meta = document.createElement("p");
  meta.className = "record-meta";
  meta.append(
    createTextElement("span", "", record.time),
    createTextElement("span", "", CATEGORY_LABELS[record.category]),
    createTextElement("span", "", MEAL_LABELS[record.meal])
  );
  const name = createTextElement("h3", "record-name", record.name);
  const emoji = createTextElement("span", "record-emoji", getItemEmoji(record));
  emoji.setAttribute("aria-hidden", "true");
  name.append(" ", emoji);
  main.append(
    meta,
    name,
    createTextElement(
      "p",
      "record-quantity",
      `${formatNumber(record.quantity)} ${record.default_unit}`
    )
  );
  if (record.note) {
    main.append(createTextElement("p", "record-note", `备注：${record.note}`));
  }

  const side = document.createElement("div");
  side.className = "record-side";
  side.append(
    createTextElement(
      "p",
      "record-water",
      `${formatNumber(record.estimated_water_ml)} ml`
    )
  );
  const deleteButton = createTextElement("button", "delete-button", "删除");
  deleteButton.type = "button";
  deleteButton.setAttribute(
    "aria-label",
    `删除 ${record.date} 的 ${record.name} 记录`
  );
  deleteButton.addEventListener(
    "click",
    (event) => deleteHistoricalRecord(record, event)
  );
  side.append(deleteButton);

  row.append(main, side);
  return row;
}

function renderTrendChart() {
  const trend = buildRecentTrendData(appData);
  const width = 560;
  const height = 280;
  const left = 32;
  const right = 18;
  const top = 28;
  const bottom = 42;
  const plotWidth = width - left - right;
  const plotHeight = height - top - bottom;
  const maxValue = Math.max(
    trend.targetMl,
    ...trend.points.map((point) => point.totalWaterMl),
    1
  );
  const xFor = (index) => left + (plotWidth * index) / (trend.points.length - 1);
  const yFor = (value) => top + plotHeight * (1 - value / maxValue);

  const svg = createSvgElement("svg", {
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-label": "最近 7 天每日水分摄入折线图",
  });
  svg.append(
    createSvgElement("line", {
      x1: left,
      y1: yFor(0),
      x2: width - right,
      y2: yFor(0),
      class: "trend-grid-line",
    }),
    createSvgElement("line", {
      x1: left,
      y1: yFor(trend.targetMl),
      x2: width - right,
      y2: yFor(trend.targetMl),
      class: "trend-target-line",
    }),
    createSvgElement(
      "text",
      {
        x: width - right,
        y: Math.max(yFor(trend.targetMl) - 8, 16),
        "text-anchor": "end",
        class: "trend-target-label",
      },
      `目标 ${trend.targetMl} ml`
    )
  );

  const coordinates = trend.points.map((point, index) => ({
    ...point,
    x: xFor(index),
    y: yFor(point.totalWaterMl),
  }));
  const pathData = coordinates
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");
  svg.append(createSvgElement("path", { d: pathData, class: "trend-water-line" }));

  for (const point of coordinates) {
    svg.append(
      createSvgElement("circle", {
        cx: point.x,
        cy: point.y,
        r: 6,
        class: "trend-point",
      }),
      createSvgElement(
        "text",
        {
          x: point.x,
          y: Math.max(point.y - 12, 17),
          "text-anchor": "middle",
          class: "trend-value-label",
        },
        formatNumber(point.totalWaterMl)
      ),
      createSvgElement(
        "text",
        {
          x: point.x,
          y: height - 12,
          "text-anchor": "middle",
          class: "trend-label",
        },
        point.date.slice(5).replace("-", "/")
      )
    );
  }

  const total = trend.points.reduce((sum, point) => sum + point.totalWaterMl, 0);
  elements.trendChart.replaceChildren(svg);
  elements.trendSummary.textContent = `近 7 日合计 ${formatNumber(total)} ml · 日均 ${formatNumber(total / trend.points.length)} ml`;
}

function selectCalendarDate(day) {
  showHistoryActionMessage("", "");
  setHistoryBackfillOpen(false);
  resetHistoryBackfillForm();
  selectedHistoryDate = day.date;
  if (!day.inCurrentMonth) {
    const [year, month] = day.date.split("-").map(Number);
    visibleCalendarMonth = new Date(year, month - 1, 1, 12);
  }
  renderCalendar();
}

function renderHistoryDetails() {
  if (!selectedHistoryDate) {
    elements.historyDetails.hidden = true;
    elements.historyRecordsList.replaceChildren();
    return;
  }

  const records = getRecordsForDate(appData, selectedHistoryDate);
  const summary = calculateSummary(appData, selectedHistoryDate);
  elements.historyDetails.hidden = false;
  elements.historyDetailsTitle.textContent = `${selectedHistoryDate} 明细`;
  elements.historyClearDateButton.hidden = records.length === 0;
  elements.historyClearDateButton.disabled = !storageReady || records.length === 0;
  const canBackfill = selectedHistoryDate <= formatLocalDate(new Date());
  elements.historyBackfillToggle.disabled = !canBackfill;
  elements.historyBackfillToggle.textContent = canBackfill
    ? "补录这一天"
    : "不能补录未来日期";
  elements.historyRecordsList.replaceChildren();

  if (records.length === 0) {
    elements.historyDetailsSummary.textContent = "这一天没有记录";
    elements.historyRecordsList.append(
      createTextElement("div", "empty-state", "这一天没有记录")
    );
    return;
  }

  elements.historyDetailsSummary.textContent = `${summary.recordCount} 条记录 · ${formatNumber(summary.totalWaterMl)} ml · 完成率 ${formatNumber(summary.completionRate)}%`;
  for (const record of [...records].reverse()) {
    elements.historyRecordsList.append(renderHistoryRecord(record));
  }
}

function renderCalendar() {
  const calendar = buildCalendarMonth(
    appData,
    visibleCalendarMonth.getFullYear(),
    visibleCalendarMonth.getMonth()
  );
  elements.calendarMonthLabel.textContent = calendar.label;
  elements.calendarGrid.replaceChildren();

  for (const day of calendar.days) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "calendar-day";
    if (!day.inCurrentMonth) {
      button.classList.add("outside-month");
    }
    if (day.hasRecords) {
      button.classList.add("has-records");
    }
    if (day.isToday) {
      button.classList.add("today");
    }
    if (day.date === selectedHistoryDate) {
      button.classList.add("selected");
    }
    button.setAttribute("aria-pressed", String(day.date === selectedHistoryDate));
    button.setAttribute(
      "aria-label",
      day.hasRecords
        ? `${day.date}，${formatNumber(day.totalWaterMl)} ml，${day.recordCount} 条记录`
        : `${day.date}，没有记录`
    );
    button.append(createTextElement("span", "calendar-day-number", String(day.dayNumber)));
    if (day.hasRecords) {
      button.append(
        createTextElement(
          "span",
          "calendar-day-total",
          `${formatNumber(day.totalWaterMl)}ml`
        )
      );
    }
    button.addEventListener("click", () => selectCalendarDate(day));
    elements.calendarGrid.append(button);
  }

  renderHistoryDetails();
}

function changeCalendarMonth(offset, event) {
  releasePointerFocus(event);
  showHistoryActionMessage("", "");
  setHistoryBackfillOpen(false);
  resetHistoryBackfillForm();
  visibleCalendarMonth = new Date(
    visibleCalendarMonth.getFullYear(),
    visibleCalendarMonth.getMonth() + offset,
    1,
    12
  );
  selectedHistoryDate = null;
  renderCalendar();
}

function renderHistory() {
  renderTrendChart();
  renderCalendar();
}

function activateView(viewName, event) {
  if (!Object.prototype.hasOwnProperty.call(elements.views, viewName)) {
    return;
  }
  releasePointerFocus(event);
  for (const [name, view] of Object.entries(elements.views)) {
    view.hidden = name !== viewName;
  }
  for (const tab of elements.viewTabs) {
    const active = tab.dataset.view === viewName;
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
  }
  if (viewName === "history") {
    renderHistory();
  }
}

function renderAll() {
  renderOverview();
  renderTodayRecords();
  renderHistory();
}

function showFormMessage(text, type = "") {
  elements.message.textContent = text;
  elements.message.className = type;
}

function showBackupMessage(text, type = "") {
  elements.backupMessage.textContent = text;
  elements.backupMessage.className = type;
}

function showHistoryActionMessage(text, type = "") {
  elements.historyActionMessage.textContent = text;
  elements.historyActionMessage.className = type
    ? `records-message ${type}`
    : "records-message";
}

function showHistoryBackfillMessage(text, type = "") {
  elements.historyBackfillMessage.textContent = text;
  elements.historyBackfillMessage.className = type
    ? `history-backfill-message ${type}`
    : "history-backfill-message";
}

function setHistoryBackfillOpen(open, event) {
  releasePointerFocus(event);
  const shouldOpen = Boolean(open && selectedHistoryDate);
  elements.historyBackfillPanel.hidden = !shouldOpen;
  elements.historyBackfillToggle.setAttribute("aria-expanded", String(shouldOpen));
  if (shouldOpen) {
    elements.historyBackfillTitle.textContent = `补录 ${selectedHistoryDate}`;
    if (!isValidTimeValue(elements.historyBackfillTime.value)) {
      elements.historyBackfillTime.value = formatLocalTime(new Date());
    }
  }
}

function resetHistoryBackfillForm() {
  for (const input of document.querySelectorAll('input[name="history-category"]')) {
    input.checked = input.value === "water";
  }
  elements.historyBackfillQuantity.value = "1";
  elements.historyBackfillMeal.value = "none";
  elements.historyBackfillTime.value = formatLocalTime(new Date());
  elements.historyBackfillNote.value = "";
  showHistoryBackfillMessage("", "");
  renderHistoryItemOptions();
}

function toggleHistoryBackfill(event) {
  const willOpen = elements.historyBackfillPanel.hidden;
  if (willOpen) {
    resetHistoryBackfillForm();
  }
  setHistoryBackfillOpen(willOpen, event);
}

function cancelHistoryBackfill(event) {
  setHistoryBackfillOpen(false, event);
  resetHistoryBackfillForm();
}

function resetImportSelection() {
  pendingImportFile = null;
  elements.importFile.value = "";
  elements.backupFileName.textContent = "尚未选择备份文件";
  elements.importButton.disabled = true;
}

function saveRecord(event) {
  event.preventDefault();
  if (!storageReady) {
    showFormMessage("本地存储不可用，未保存记录", "error");
    return;
  }

  const item = selectedItem();
  if (!item || item.category !== selectedCategory()) {
    showFormMessage("请选择有效的常用项目", "error");
    return;
  }

  try {
    const now = new Date();
    const record = buildRecord({
      item,
      quantity: elements.quantity.value,
      meal: elements.meal.value,
      note: elements.note.value,
      now,
      id: generateRecordId(appData.records),
    });
    const nextData = {
      ...appData,
      records: [...appData.records, record],
    };
    persistData(nextData);
    elements.quantity.value = "1";
    elements.meal.value = "none";
    elements.note.value = "";
    renderEstimate();
    renderAll();
    showFormMessage(
      `已保存 ${record.name}，估算水分 ${formatNumber(record.estimated_water_ml)} ml`,
      "ready"
    );
  } catch (error) {
    showFormMessage(error.message || "保存失败，未修改本地数据", "error");
  }
}

function saveHistoricalBackfill(event) {
  event.preventDefault();
  showHistoryBackfillMessage("", "");
  if (!storageReady) {
    showHistoryBackfillMessage("本地存储不可用，未保存补录记录", "error");
    return;
  }
  if (!selectedHistoryDate || !isValidDateKey(selectedHistoryDate)) {
    showHistoryBackfillMessage("请先在月历中选择有效日期", "error");
    return;
  }
  if (selectedHistoryDate > formatLocalDate(new Date())) {
    showHistoryBackfillMessage("不能补录未来日期", "error");
    return;
  }

  const item = selectedHistoryItem();
  if (!item || item.category !== selectedHistoryCategory()) {
    showHistoryBackfillMessage("请选择有效的常用项目", "error");
    return;
  }

  try {
    const now = new Date();
    const record = buildRecordForDate({
      item,
      quantity: elements.historyBackfillQuantity.value,
      meal: elements.historyBackfillMeal.value,
      note: elements.historyBackfillNote.value,
      date: selectedHistoryDate,
      time: elements.historyBackfillTime.value,
      now,
      id: generateRecordId(appData.records),
    });
    persistData({
      ...appData,
      records: [...appData.records, record],
    });
    const savedDate = selectedHistoryDate;
    setHistoryBackfillOpen(false);
    resetHistoryBackfillForm();
    renderAll();
    showHistoryActionMessage(`已补录 ${savedDate} 的记录。`, "ready");
  } catch (error) {
    showHistoryBackfillMessage(error.message || "补录失败，当前数据未修改", "error");
  }
}

function releasePointerFocus(event) {
  const button = event && event.currentTarget;
  if (event && event.detail !== 0 && button && typeof button.blur === "function") {
    button.blur();
  }
}

function deleteRecord(record, event) {
  const confirmed = globalThis.confirm(`确认删除“${record.name}”吗？此操作无法撤销。`);
  releasePointerFocus(event);
  if (!confirmed) {
    return;
  }

  const today = formatLocalDate(new Date());
  const result = deleteRecordForDateById(appData, record.id, today);
  if (result.deletedCount !== 1) {
    elements.recordsMessage.textContent = "今天没有找到这条记录";
    elements.recordsMessage.className = "records-message error";
    return;
  }

  try {
    persistData(result.data);
    renderAll();
    elements.recordsMessage.textContent = `已删除 ${record.name}`;
    elements.recordsMessage.className = "records-message ready";
  } catch (error) {
    elements.recordsMessage.textContent = error.message || "删除失败";
    elements.recordsMessage.className = "records-message error";
  }
}

function deleteHistoricalRecord(record, event) {
  showHistoryActionMessage("", "");
  const targetDate = selectedHistoryDate;
  if (!targetDate || record.date !== targetDate) {
    releasePointerFocus(event);
    showHistoryActionMessage("未找到当前日期对应的历史记录，数据未修改", "error");
    return;
  }

  const confirmed = globalThis.confirm(
    `确定删除 ${targetDate} 的“${record.name}”记录吗？此操作无法撤销。`
  );
  releasePointerFocus(event);
  const result = resolveRecordDeletion(
    appData,
    record.id,
    targetDate,
    confirmed
  );
  if (result.cancelled) {
    return;
  }
  if (result.deletedCount !== 1) {
    showHistoryActionMessage("没有找到这条历史记录，数据未修改", "error");
    return;
  }

  try {
    persistData(result.data);
    renderAll();
    showHistoryActionMessage("历史记录已删除。", "ready");
  } catch (error) {
    showHistoryActionMessage(error.message || "历史记录删除失败", "error");
  }
}

function clearSelectedHistoryDate(event) {
  showHistoryActionMessage("", "");
  const targetDate = selectedHistoryDate;
  if (!targetDate || !isValidDateKey(targetDate)) {
    releasePointerFocus(event);
    showHistoryActionMessage("请先在月历中选择有效日期", "error");
    return;
  }

  const recordCount = getRecordsForDate(appData, targetDate).length;
  if (recordCount === 0) {
    releasePointerFocus(event);
    showHistoryActionMessage("这一天没有可清空的记录", "error");
    renderHistoryDetails();
    return;
  }

  const confirmed = globalThis.confirm(
    `确定清空 ${targetDate} 的全部 ${recordCount} 条记录吗？此操作无法撤销。`
  );
  releasePointerFocus(event);
  const result = resolveDateClear(appData, targetDate, confirmed);
  if (result.cancelled) {
    return;
  }
  if (result.deletedCount !== recordCount) {
    showHistoryActionMessage("记录数量发生变化，未执行清空", "error");
    return;
  }

  try {
    persistData(result.data);
    setHistoryBackfillOpen(false);
    resetHistoryBackfillForm();
    renderAll();
    showHistoryActionMessage(
      `已清空 ${targetDate} 的 ${result.deletedCount} 条记录。`,
      "ready"
    );
  } catch (error) {
    showHistoryActionMessage(error.message || "清空失败，当前数据未修改", "error");
  }
}

function clearTodayRecords(event) {
  const today = formatLocalDate(new Date());
  const result = clearRecordsForDate(appData, today);
  if (result.deletedCount === 0) {
    return;
  }
  const confirmed = globalThis.confirm(
    `确认清空今天的 ${result.deletedCount} 条记录吗？此操作无法撤销。`
  );
  releasePointerFocus(event);
  if (!confirmed) {
    return;
  }

  try {
    persistData(result.data);
    renderAll();
    elements.recordsMessage.textContent = `已清空今天的 ${result.deletedCount} 条记录`;
    elements.recordsMessage.className = "records-message ready";
  } catch (error) {
    elements.recordsMessage.textContent = error.message || "清空失败";
    elements.recordsMessage.className = "records-message error";
  }
}

async function exportBackup(event) {
  releasePointerFocus(event);

  if (!storageReady) {
    showBackupMessage("当前本地数据无法读取，请先导入有效备份", "error");
    return;
  }

  try {
    const now = new Date();
    const payload = buildExportPayload(appData, now);
    const filename = buildExportFilename(now);
    downloadTextFile(filename, JSON.stringify(payload, null, 2));
    showBackupMessage("备份已导出", "ready");
  } catch (error) {
    showBackupMessage(error.message || "导出失败，当前数据未修改", "error");
  }
}

function handleImportFileChange() {
  pendingImportFile = elements.importFile.files && elements.importFile.files[0]
    ? elements.importFile.files[0]
    : null;
  elements.importButton.disabled = !pendingImportFile;
  elements.backupFileName.textContent = pendingImportFile
    ? `已选择：${pendingImportFile.name}`
    : "尚未选择备份文件";
  if (pendingImportFile) {
    showBackupMessage("", "");
  }
}

async function importBackup(event) {
  if (!pendingImportFile) {
    showBackupMessage("请先选择一个 JSON 备份文件", "error");
    return;
  }

  let payload;
  let nextData;
  try {
    payload = JSON.parse(await pendingImportFile.text());
  } catch (error) {
    showBackupMessage("备份文件不是有效 JSON，当前数据未修改", "error");
    return;
  }

  try {
    nextData = buildDataFromBackupPayload(payload);
  } catch (error) {
    showBackupMessage(error.message || "备份校验失败，当前数据未修改", "error");
    return;
  }

  const confirmed = globalThis.confirm(
    "导入会用备份文件中的记录替换当前本机记录，当前本机记录会被覆盖。建议导入前先导出当前备份。确认继续吗？"
  );
  releasePointerFocus(event);
  if (!confirmed) {
    showBackupMessage("已取消导入，当前数据未修改", "");
    return;
  }

  try {
    writeDataToStorage(globalThis.localStorage, nextData);
    appData = nextData;
    restoreStorageReadyState();
    showHistoryActionMessage("", "");
    setHistoryBackfillOpen(false);
    resetHistoryBackfillForm();
    renderAll();
    resetImportSelection();
    showBackupMessage(`备份已导入，共 ${nextData.records.length} 条记录`, "ready");
  } catch (error) {
    showBackupMessage(error.message || "导入失败，当前数据未修改", "error");
  }
}

function initializeStorage() {
  try {
    appData = loadDataFromStorage(globalThis.localStorage);
    restoreStorageReadyState();
  } catch (error) {
    appData = createEmptyData();
    storageReady = false;
    elements.storageStatus.textContent = `${error.message || "无法读取浏览器本地数据"}，原数据未被覆盖`;
    elements.notice.classList.add("error");
    elements.saveButton.disabled = true;
    elements.historyBackfillSaveButton.disabled = true;
    elements.exportButton.disabled = true;
    elements.recordsMessage.textContent = "本地数据读取失败，请勿继续写入；可导入有效备份进行恢复";
    elements.recordsMessage.className = "records-message error";
  }
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }

  if (globalThis.location.protocol === "file:") {
    console.info("HydrationTracker: file:// 预览模式下跳过 Service Worker 注册");
    return;
  }

  globalThis.addEventListener("load", () => {
    navigator.serviceWorker
      .register("./service-worker.js")
      .then(() => {
        console.info("HydrationTracker: Service Worker 已注册");
      })
      .catch((error) => {
        console.warn("HydrationTracker: Service Worker 注册失败", error);
      });
  });
}

const appShellReady = Boolean(
  elements.date
  && elements.total
  && elements.rate
  && elements.progressRing
  && elements.progressEncouragement
  && elements.remaining
  && elements.count
  && elements.notice
  && elements.storageStatus
  && elements.form
  && elements.item
  && elements.quantity
  && elements.quantityUnit
  && elements.meal
  && elements.note
  && elements.itemDefaults
  && elements.estimateMessage
  && elements.message
  && elements.saveButton
  && elements.clearButton
  && elements.recordsMessage
  && elements.recordsList
  && elements.viewTabs.length === 3
  && elements.views.today
  && elements.views.history
  && elements.views.backup
  && elements.trendChart
  && elements.trendSummary
  && elements.calendarMonthLabel
  && elements.calendarGrid
  && elements.previousMonthButton
  && elements.nextMonthButton
  && elements.historyDetails
  && elements.historyDetailsTitle
  && elements.historyDetailsSummary
  && elements.historyActionMessage
  && elements.historyClearDateButton
  && elements.historyBackfillToggle
  && elements.historyBackfillPanel
  && elements.historyBackfillTitle
  && elements.historyBackfillForm
  && elements.historyBackfillItem
  && elements.historyBackfillQuantity
  && elements.historyBackfillQuantityUnit
  && elements.historyBackfillMeal
  && elements.historyBackfillTime
  && elements.historyBackfillNote
  && elements.historyBackfillItemDefaults
  && elements.historyBackfillEstimateMessage
  && elements.historyBackfillMessage
  && elements.historyBackfillCancelButton
  && elements.historyBackfillSaveButton
  && elements.historyRecordsList
  && elements.exportButton
  && elements.importFile
  && elements.importButton
  && elements.backupFileName
  && elements.backupMessage
);

if (appShellReady) {
  for (const input of document.querySelectorAll('input[name="category"]')) {
    input.addEventListener("change", renderItemOptions);
  }
  elements.item.addEventListener("change", renderEstimate);
  elements.quantity.addEventListener("input", renderEstimate);
  elements.form.addEventListener("submit", saveRecord);
  for (const input of document.querySelectorAll('input[name="history-category"]')) {
    input.addEventListener("change", renderHistoryItemOptions);
  }
  elements.historyBackfillItem.addEventListener("change", renderHistoryEstimate);
  elements.historyBackfillQuantity.addEventListener("input", renderHistoryEstimate);
  elements.historyBackfillForm.addEventListener("submit", saveHistoricalBackfill);
  elements.historyBackfillToggle.addEventListener("click", toggleHistoryBackfill);
  elements.historyBackfillCancelButton.addEventListener("click", cancelHistoryBackfill);
  elements.historyClearDateButton.addEventListener("click", clearSelectedHistoryDate);
  elements.clearButton.addEventListener("click", clearTodayRecords);
  elements.previousMonthButton.addEventListener(
    "click",
    (event) => changeCalendarMonth(-1, event)
  );
  elements.nextMonthButton.addEventListener(
    "click",
    (event) => changeCalendarMonth(1, event)
  );
  for (const tab of elements.viewTabs) {
    tab.addEventListener("click", (event) => activateView(tab.dataset.view, event));
  }
  elements.exportButton.addEventListener("click", exportBackup);
  elements.importFile.addEventListener("change", handleImportFileChange);
  elements.importButton.addEventListener("click", importBackup);

  renderItemOptions();
  resetHistoryBackfillForm();
  initializeStorage();
  resetImportSelection();
  renderAll();
  activateView("today");
  registerServiceWorker();
}

globalThis.HydrationTrackerV3 = Object.freeze({
  STORAGE_KEY,
  SCHEMA_VERSION,
  COMMON_ITEMS,
  ITEM_EMOJIS,
  EXPORT_APP,
  EXPORT_VERSION,
  EXPORT_SOURCE,
  calculateEstimatedWaterMl,
  getItemEmoji,
  getProgressMessage,
  isValidDateKey,
  isValidTimeValue,
  createEmptyData,
  parseStoredData,
  getRecordsForDate,
  calculateSummary,
  summarizeRecordsByDate,
  buildCalendarMonth,
  buildRecentTrendData,
  deleteRecordForDateById,
  resolveRecordDeletion,
  clearRecordsForDate,
  resolveDateClear,
  buildRecordForDate,
  buildExportFilename,
  buildExportPayload,
  validateBackupPayload,
  buildDataFromBackupPayload,
});
