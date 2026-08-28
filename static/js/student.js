// Student JS Helpers
function updateCartQty(itemId, quantity) {
  fetch("/api/cart/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item_id: itemId, quantity: quantity }),
  })
    .then((r) => r.json())
    .then(() => window.location.reload());
}

let currentVendorId = null;
let currentPickupTime = null;

function openPaymentModal(vendorId, pickupTime, total) {
  currentVendorId = vendorId;
  currentPickupTime = pickupTime;

  const amtEl = document.getElementById("modal-pay-amount");
  if (amtEl) amtEl.innerText = Math.round(total);

  document.getElementById("payment-selection-step").classList.remove("d-none");
  document.getElementById("payment-processing-step").classList.add("d-none");
  document.getElementById("payment-success-step").classList.add("d-none");

  const modal = new bootstrap.Modal(document.getElementById("paymentModal"));
  modal.show();
}

function togglePayOption(method) {
  const upiDiv = document.getElementById("pay-opt-upi");
  const cardDiv = document.getElementById("pay-opt-card");
  if (method === "Card") {
    upiDiv.classList.add("d-none");
    cardDiv.classList.remove("d-none");
  } else {
    upiDiv.classList.remove("d-none");
    cardDiv.classList.add("d-none");
  }
}

function confirmFakePayment() {
  const selMethod = document.querySelector('input[name="payMethod"]:checked')
    ? document.querySelector('input[name="payMethod"]:checked').value
    : "UPI";

  document.getElementById("payment-selection-step").classList.add("d-none");
  document.getElementById("payment-processing-step").classList.remove("d-none");

  // Gather cart items
  const items = [];
  document.querySelectorAll("[data-cart-item-id]").forEach((el) => {
    items.push({
      menu_item_id: parseInt(el.getAttribute("data-cart-item-id")),
      quantity: parseInt(el.getAttribute("data-cart-item-qty")),
    });
  });

  setTimeout(() => {
    fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        vendor_id: currentVendorId,
        items: items,
        pickup_time: currentPickupTime,
        payment_method: selMethod,
      }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) {
          document.getElementById("payment-processing-step").classList.add("d-none");
          document.getElementById("payment-success-step").classList.remove("d-none");

          const tokenDisplay = document.getElementById("token-badge-display");
          if (tokenDisplay) tokenDisplay.innerText = `#${data.pickup_token}`;

          setTimeout(() => {
            window.location.href = `/student/tracking/${data.order_id}`;
          }, 2200);
        } else {
          showToast("Error", data.error || "Payment failed", "danger");
          document.getElementById("payment-processing-step").classList.add("d-none");
          document.getElementById("payment-selection-step").classList.remove("d-none");
        }
      })
      .catch((err) => console.error(err));
  }, 1200);
}

function offerSmartSwap(orderId) {
  fetch("/api/smartswap", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order_id: orderId }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.success) {
        showToast("SmartSwap", data.message, "success");
        setTimeout(() => window.location.reload(), 1200);
      } else {
        showToast("Error", data.error || "Failed to offer swap.", "danger");
      }
    });
}

function claimSmartSwap(swapId) {
  fetch(`/api/smartswap/${swapId}/claim`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.success) {
        showToast("SmartSwap Claimed", data.message, "success");
        setTimeout(() => (window.location.href = "/student/orders"), 1200);
      } else {
        showToast("Error", data.error || "Failed to claim swap.", "danger");
      }
    });
}

function donateOrder(orderId) {
  fetch(`/api/orders/${orderId}/donate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.success) {
        showToast("Order Donated", data.message, "success");
        setTimeout(() => window.location.reload(), 1200);
      } else {
        showToast("Error", data.error || "Failed to donate order.", "danger");
      }
    });
}

function createGroupOrder() {
  fetch("/api/group/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.success) {
        showToast("Group Created", `Share Code: ${data.group_code}`, "success");
        setTimeout(() => window.location.reload(), 1200);
      }
    });
}

function joinGroupOrder() {
  const code = document.getElementById("group-code-input").value;
  if (!code) return;

  fetch("/api/group/join", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ group_code: code }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.success) {
        showToast("Joined Group", data.message, "success");
        setTimeout(() => window.location.reload(), 1200);
      } else {
        showToast("Error", data.error || "Failed to join group.", "danger");
      }
    });
}
