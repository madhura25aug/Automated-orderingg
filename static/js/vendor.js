// Vendor JS Helpers
function updateOrderStatus(orderId, newStatus) {
  fetch(`/api/orders/${orderId}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.success) {
        showToast(
          "Status Updated",
          `Order #${orderId} moved to ${newStatus}`,
          "success"
        );
        setTimeout(() => window.location.reload(), 800);
      } else {
        showToast("Error", data.error || "Failed to update status", "danger");
      }
    });
}

function sendCopilotQuery(customQuestion = null) {
  const inputEl = document.getElementById("copilot-input");
  const question = customQuestion || (inputEl ? inputEl.value : "");

  if (!question.trim()) return;

  const chatContainer = document.getElementById("copilot-chat-history");
  if (chatContainer) {
    chatContainer.insertAdjacentHTML(
      "beforeend",
      `
            <div class="d-flex justify-content-end mb-3">
              <div class="bg-primary text-white p-3 rounded-3 max-w-75">
                <strong>You:</strong> ${question}
              </div>
            </div>
        `
    );
  }

  if (inputEl) inputEl.value = "";

  fetch("/api/copilot/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: question }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (chatContainer) {
        chatContainer.insertAdjacentHTML(
          "beforeend",
          `
                <div class="d-flex justify-content-start mb-3">
                  <div class="bg-light border p-3 rounded-3 max-w-75">
                    <strong>🤖 Canteen Copilot:</strong><br>${data.answer}
                  </div>
                </div>
            `
        );
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    });
}

function createSmartBatches() {
  fetch('/api/batches/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vendor_id: 1 })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast('Smart Batches', data.message, 'success');
      setTimeout(() => window.location.reload(), 1000);
    }
  });
}

function startBatchCooking(batchNum, orderIds) {
  fetch('/api/batches/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batch_number: batchNum, order_ids: orderIds })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast('Batch Started', data.message, 'success');
      setTimeout(() => window.location.reload(), 1000);
    }
  });
}
