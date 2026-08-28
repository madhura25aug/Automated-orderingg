// Global Main JS for CanteenFlow AI
document.addEventListener("DOMContentLoaded", function () {
  // Initialize SocketIO client connection
  if (typeof io !== "undefined") {
    const socket = io();

    socket.on("connect", function () {
      console.log("Connected to CanteenFlow AI WebSocket Server");
    });

    socket.on("order_status_update", function (data) {
      console.log("Order Status Update:", data);
      showToast(
        "Order Update",
        `Order #${data.order_number} status changed to ${data.status.replace("_", " ")}!`,
        "info"
      );

      // Refresh order status if tracking page open
      const statusEl = document.getElementById("order-status-badge");
      if (statusEl) {
        statusEl.innerText = data.status.replace("_", " ");
      }
    });

    socket.on("new_order", function (data) {
      showToast(
        "New Order!",
        `New order #${data.order_number} placed by ${data.user_name} (₹${data.total})`,
        "success"
      );
    });

    socket.on("crowd_update", function (data) {
      showToast(
        "Crowd Alert",
        `Canteen crowd updated to ${data.level} (Wait: ~${data.wait_mins} mins)`,
        "warning"
      );
    });
  }
});

// Toast notification helper
function showToast(title, message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const bgClass =
    type === "success"
      ? "bg-success"
      : type === "warning"
      ? "bg-warning text-dark"
      : type === "danger"
      ? "bg-danger"
      : "bg-primary";

  const toastHtml = `
        <div class="toast show align-items-center text-white ${bgClass} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
          <div class="d-flex">
            <div class="toast-body">
              <strong>${title}</strong>: ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
          </div>
        </div>
    `;

  container.insertAdjacentHTML("beforeend", toastHtml);
  setTimeout(() => {
    const toasts = container.getElementsByClassName("toast");
    if (toasts.length > 0) toasts[0].remove();
  }, 4000);
}

// Cart Addition AJAX Helper
function addToCart(itemId) {
  fetch("/api/cart/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item_id: itemId, quantity: 1 }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.success) {
        showToast("Cart", data.message, "success");
        const badge = document.getElementById("cart-count-badge");
        if (badge) badge.innerText = data.cart_count;
      } else {
        showToast("Error", data.error || "Failed to add item.", "danger");
      }
    })
    .catch((err) => console.error(err));
}
