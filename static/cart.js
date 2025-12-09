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

updateCartTotal();
document.getElementById("checkoutBtn").addEventListener("click", () => {
  alert("Checkout feature coming soon!");
});