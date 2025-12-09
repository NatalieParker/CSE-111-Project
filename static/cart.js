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

function checkout() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
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
document.getElementById("checkoutBtn").addEventListener("click", () => checkout());