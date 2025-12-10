const cart = JSON.parse(localStorage.getItem("cart")) || [];
const cartDisplay = document.getElementById("cartDisplay");
cartDisplay.innerHTML = "... list of items ..."

if (cart.length === 0) {
  cartDisplay.innerHTML = "<p>No items in cart.</p>";
} else {
  cartDisplay.innerHTML = `
    <ul>
      ${cart.map(item => `
        <li>${item.name} — $${item.price} (x${item.quantity})</li>
      `).join("")}
    </ul>
  `;
}

function updateCartTotal() {
  const totalBox = document.getElementById("cartTotal");
  if (!totalBox) return;

  if (cart.length === 0) {
    totalBox.innerHTML = "";
    return;
  }

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  totalBox.innerHTML = `<strong>Total: $${total.toFixed(2)}</strong>`;
}

function loadPreviousTransactions() {
  const customerId = localStorage.getItem("customerId");
  const container = document.getElementById("transactionsContainer");
  if (!container) return;

  if (!customerId) {
    container.innerHTML = "<p>No customer selected.</p>";
    return;
  }

  fetch(`/transactions?customerId=${encodeURIComponent(customerId)}`)
    .then(res => res.json())
    .then(data => {
      const txns = data.transactions || [];

      if (txns.length === 0) {
        container.innerHTML = "<p>No previous transactions.</p>";
        return;
      }

      let html = `
        <table border="1" cellpadding="4" cellspacing="0">
          <tr>
            <th>Transaction #</th>
            <th>Date</th>
            <th>Store</th>
            <th>Status</th>
            <th>Total</th>
          </tr>
      `;

      txns.forEach(t => {
        html += `
          <tr>
            <td>${t.transactionKey}</td>
            <td>${t.date}</td>
            <td>${t.storeName}</td>
            <td>${t.status}</td>
            <td>$${Number(t.total).toFixed(2)}</td>
          </tr>
        `;
      });

      html += "</table>";
      container.innerHTML = html;
    })
    .catch(err => {
      console.error("Error loading transactions", err);
      container.innerHTML = "<p>Error loading transactions.</p>";
    });
}

function checkout() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    if (cart.length === 0) return;
    const customerId = localStorage.getItem("customerId");

    fetch("/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customerId: customerId,
        cart: cart
      })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
        alert("Checkout complete! Transaction #" + data.transactionKey);

        localStorage.removeItem("cart");
        window.location = "/";
    })
    .catch(err => {
        console.error(err);
        alert("Checkout failed.");
    });
}

updateCartTotal();
loadPreviousTransactions();
document.getElementById("checkoutBtn").addEventListener("click", () => checkout());