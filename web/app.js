const elements = {
  summary: document.querySelector("#summary"),
  date: document.querySelector("#today-date"),
  total: document.querySelector("#total-water"),
  target: document.querySelector("#target-caption"),
  rate: document.querySelector("#completion-rate"),
  remaining: document.querySelector("#remaining-water"),
  count: document.querySelector("#record-count"),
  progress: document.querySelector("#progress-fill"),
  message: document.querySelector("#load-message"),
  form: document.querySelector("#record-form"),
  item: document.querySelector("#item-name"),
  quantity: document.querySelector("#quantity"),
  quantityUnit: document.querySelector("#quantity-unit"),
  meal: document.querySelector("#meal"),
  note: document.querySelector("#note"),
  itemDefaults: document.querySelector("#item-defaults"),
  estimate: document.querySelector("#estimated-water"),
  formMessage: document.querySelector("#form-message"),
  submit: document.querySelector("#submit-record"),
  recordsList: document.querySelector("#records-list"),
  recordsMessage: document.querySelector("#records-message"),
  clearToday: document.querySelector("#clear-today"),
};

let commonItems = [];
let todayRecords = [];

const categoryLabels = {
  water: "白水",
  beverage: "饮品",
  food: "食物",
};

const mealLabels = {
  breakfast: "早餐",
  lunch: "午餐",
  dinner: "晚餐",
  snack: "加餐",
  none: "无餐次",
};

function formatNumber(value) {
  return new Intl.NumberFormat("zh-CN", {
    maximumFractionDigits: 1,
  }).format(Number(value) || 0);
}

function selectedCategory() {
  return document.querySelector('input[name="category"]:checked').value;
}

function selectedItem() {
  return commonItems.find((item) => item.name === elements.item.value);
}

function showTodayDate() {
  elements.date.textContent = new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "short",
  }).format(new Date());
}

async function loadTodaySummary() {
  try {
    const response = await fetch("/api/today", {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error("无法读取今日数据");
    }

    const data = await response.json();
    elements.total.textContent = formatNumber(data.total_water_ml);
    elements.target.textContent = formatNumber(data.target_ml);
    elements.rate.textContent = formatNumber(data.completion_rate);
    elements.remaining.textContent = formatNumber(data.remaining_ml);
    elements.count.textContent = formatNumber(data.record_count);
    elements.progress.style.width = `${Math.min(Number(data.completion_rate) || 0, 100)}%`;
    elements.message.textContent = "本地记录已读取";
    elements.message.classList.remove("error");
  } catch (error) {
    elements.message.textContent = "暂时无法读取本地记录，请确认服务器仍在运行。";
    elements.message.classList.add("error");
  } finally {
    elements.summary.setAttribute("aria-busy", "false");
  }
}

function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  element.className = className;
  element.textContent = text;
  return element;
}

function renderTodayRecords() {
  elements.recordsList.replaceChildren();
  if (todayRecords.length === 0) {
    elements.recordsList.append(
      createTextElement("div", "empty-records", "今天还没有记录")
    );
    elements.clearToday.disabled = true;
    return;
  }

  elements.clearToday.disabled = false;
  for (const record of [...todayRecords].reverse()) {
    const item = document.createElement("article");
    item.className = "record-item";

    const main = document.createElement("div");
    main.className = "record-main";
    const meta = document.createElement("p");
    meta.className = "record-meta";
    meta.append(
      createTextElement("span", "", record.time || "--:--"),
      createTextElement("span", "", categoryLabels[record.category] || "未知类型"),
      createTextElement("span", "", mealLabels[record.meal] || "无餐次")
    );
    main.append(
      meta,
      createTextElement("h3", "record-name", record.name || "未命名"),
      createTextElement(
        "p",
        "record-amount",
        `${formatNumber(record.amount)} ${record.unit || ""}`.trim()
      )
    );
    if (record.note) {
      main.append(createTextElement("p", "record-note", `备注：${record.note}`));
    }

    const water = document.createElement("div");
    water.className = "record-water";
    water.append(
      createTextElement("strong", "", formatNumber(record.estimated_water_ml)),
      createTextElement("span", "", "ml 估算水分")
    );

    const deleteButton = createTextElement("button", "delete-button", "删除");
    deleteButton.type = "button";
    deleteButton.disabled = !record.id;
    deleteButton.setAttribute("aria-label", `删除 ${record.name || "未命名"}`);
    deleteButton.addEventListener("click", () => deleteRecord(record, deleteButton));

    item.append(main, water, deleteButton);
    elements.recordsList.append(item);
  }
}

async function loadTodayRecords() {
  elements.recordsList.setAttribute("aria-busy", "true");
  try {
    const response = await fetch("/api/records/today", {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "无法读取今日记录。");
    }

    todayRecords = Array.isArray(data.records) ? data.records : [];
    renderTodayRecords();
    elements.recordsMessage.textContent = `今天共有 ${todayRecords.length} 条记录`;
    elements.recordsMessage.className = "records-message";
  } catch (error) {
    todayRecords = [];
    elements.recordsList.replaceChildren();
    elements.clearToday.disabled = true;
    elements.recordsMessage.textContent = error.message || "无法读取今日记录。";
    elements.recordsMessage.className = "records-message error";
  } finally {
    elements.recordsList.setAttribute("aria-busy", "false");
  }
}

async function refreshTodayViews() {
  await Promise.all([loadTodaySummary(), loadTodayRecords()]);
}

async function deleteRecord(record, button) {
  const confirmed = window.confirm(
    `确认删除“${record.name || "未命名"}”吗？此操作无法撤销。`
  );
  if (!confirmed) {
    return;
  }

  button.disabled = true;
  try {
    const response = await fetch(`/api/records/${encodeURIComponent(record.id)}`, {
      method: "DELETE",
      headers: { Accept: "application/json" },
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "删除失败。");
    }

    await refreshTodayViews();
    elements.recordsMessage.textContent = `已删除 ${record.name || "记录"}`;
    elements.recordsMessage.className = "records-message success";
  } catch (error) {
    button.disabled = false;
    elements.recordsMessage.textContent = error.message || "删除失败，请稍后重试。";
    elements.recordsMessage.className = "records-message error";
  }
}

async function clearTodayRecords() {
  const confirmed = window.confirm(
    `确认清空今天的 ${todayRecords.length} 条记录吗？此操作无法撤销。`
  );
  if (!confirmed) {
    return;
  }

  elements.clearToday.disabled = true;
  try {
    const response = await fetch("/api/records/today", {
      method: "DELETE",
      headers: { Accept: "application/json" },
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "清空失败。");
    }

    await refreshTodayViews();
    elements.recordsMessage.textContent = `已清空今天的 ${data.deleted_count} 条记录`;
    elements.recordsMessage.className = "records-message success";
  } catch (error) {
    elements.clearToday.disabled = todayRecords.length === 0;
    elements.recordsMessage.textContent = error.message || "清空失败，请稍后重试。";
    elements.recordsMessage.className = "records-message error";
  }
}

function populateCommonItems() {
  const items = commonItems.filter((item) => item.category === selectedCategory());
  elements.item.replaceChildren();
  for (const item of items) {
    const option = document.createElement("option");
    option.value = item.name;
    option.textContent = item.name;
    elements.item.append(option);
  }
  updateEstimatePreview();
}

function updateEstimatePreview() {
  const item = selectedItem();
  const quantity = Number(elements.quantity.value);
  if (!item) {
    elements.quantityUnit.textContent = "份";
    elements.itemDefaults.textContent = "暂无可用项目";
    elements.estimate.textContent = "--";
    return;
  }

  elements.quantityUnit.textContent = item.unit;
  elements.itemDefaults.textContent = `1 ${item.unit}约 ${formatNumber(item.base_amount)} ${item.base_unit} · 含水率估算 ${Number(item.water_ratio).toFixed(2)}`;
  const estimatedWater = quantity > 0
    ? quantity * Number(item.base_amount) * Number(item.water_ratio)
    : 0;
  elements.estimate.textContent = formatNumber(estimatedWater);
}

async function loadCommonItems() {
  try {
    const response = await fetch("/api/common-items", {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error("无法读取常用项目");
    }
    const data = await response.json();
    commonItems = Array.isArray(data.items) ? data.items : [];
    populateCommonItems();
  } catch (error) {
    elements.formMessage.textContent = "无法读取常用项目，请确认服务器仍在运行。";
    elements.formMessage.className = "error";
    elements.submit.disabled = true;
  }
}

async function submitRecord(event) {
  event.preventDefault();
  elements.formMessage.textContent = "正在保存...";
  elements.formMessage.className = "";
  elements.submit.disabled = true;

  const payload = {
    category: selectedCategory(),
    name: elements.item.value,
    quantity: Number(elements.quantity.value),
    meal: elements.meal.value,
    note: elements.note.value,
  };

  try {
    const response = await fetch("/api/records", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "记录保存失败。");
    }

    elements.formMessage.textContent = `已保存 ${payload.name}，估算水分 ${formatNumber(data.estimated_water_ml)} ml。`;
    elements.formMessage.className = "success";
    elements.quantity.value = "1";
    elements.note.value = "";
    updateEstimatePreview();
    await refreshTodayViews();
  } catch (error) {
    elements.formMessage.textContent = error.message || "记录保存失败，请稍后重试。";
    elements.formMessage.className = "error";
  } finally {
    elements.submit.disabled = false;
  }
}

for (const input of document.querySelectorAll('input[name="category"]')) {
  input.addEventListener("change", populateCommonItems);
}
elements.item.addEventListener("change", updateEstimatePreview);
elements.quantity.addEventListener("input", updateEstimatePreview);
elements.form.addEventListener("submit", submitRecord);
elements.clearToday.addEventListener("click", clearTodayRecords);

showTodayDate();
loadTodaySummary();
loadCommonItems();
loadTodayRecords();
