// localStorage.setItem("customerId", "1000"); // TODO: UPDATE AFTER LOGIN IS IMPLEMENTED

const campusDropdown = document.getElementById("campusDropdown");
const categoryDropdown = document.getElementById("categoryDropdown");
const storeList = document.getElementById("storeList");

let cart = JSON.parse(localStorage.getItem("cart")) || [];

fetch("/campuses")
  .then(res => res.json())
  .then(data => {

    campusDropdown.innerHTML = `<option value="">-- Select a campus --</option>`;

    data.campuses.forEach(campus => {
      const option = document.createElement("option");
      option.value = campus.campusKey;
      option.textContent = campus.campusName;
      campusDropdown.appendChild(option);
    });
  });

function loadStores() {
  const campusKey = campusDropdown.value;
  const category = categoryDropdown.value;

  let url = `/stores?category=${encodeURIComponent(category)}`;

  if (campusKey) {
    url += `&campusKey=${encodeURIComponent(campusKey)}`;
  }

  fetch(url)
    .then(res => res.json())
    .then(data => {
      storeList.innerHTML = "";

      if (!data.stores || data.stores.length === 0) {
        storeList.innerHTML = "<p>No results found.</p>";
        return;
      }

      data.stores.forEach(store => {
        const header = document.createElement("h3");
        header.textContent = store.storeName;
        storeList.appendChild(header);

        const table = document.createElement("table");
        table.border = "1";
        table.innerHTML = `
          <tr>
            <th>Product</th>
            <th>Price</th>
            <th>Add to Cart</th>
          </tr>
        `;

        store.products.forEach(product => {
          const row = document.createElement("tr");

          const inCart = cart.some(
            item => item.productKey == product.productKey && item.storeKey == store.storeKey
          );
          let buttonLabel = inCart ? "Remove" : "Add";
          let buttonClass = inCart ? "cart-btn in-cart" : "cart-btn";

          row.innerHTML = `
            <td>${product.productName}</td>
            <td>$${product.price.toFixed(2)}</td>
            <td>
              <button class="${buttonClass}"
                      data-productkey="${product.productKey}"
                      data-productname="${product.productName}"
                      data-price="${product.price}"
                      data-storekey="${store.storeKey}"
                      data-storename="${store.storeName}">
                ${buttonLabel}
              </button>
            </td>
          `;
          table.appendChild(row);
        });

        storeList.appendChild(table);
      });
    })
    .catch(err => {
      storeList.innerHTML = "<p>Error loading data.</p>";
      console.error(err);
    });
    console.log("LOCAL STORAGE CUSTOMER ID: ", localStorage.getItem("customerId"));
}

function addRemoveItems(event) {
  if (!event.target.classList.contains("cart-btn")) return;

  const btn = event.target;
  const key = btn.dataset.productkey;
  const name = btn.dataset.productname;
  const price = parseFloat(btn.dataset.price);
  const storeKey = btn.dataset.storekey;
  const storeName = btn.dataset.storename;

  const existing = cart.find(
    item => item.productKey == key && item.storeKey == storeKey
  );

  if (!existing) {
    cart.push({
      productKey: key,
      name: name,
      price: price,
      storeKey: storeKey,
      storeName: storeName,
      quantity: 1
    });
    btn.textContent = "Remove";
    btn.classList.add("in-cart");
  } else {
    cart = cart.filter(
      item => !(item.productKey == key && item.storeKey == storeKey)
    );
    btn.textContent = "Add";
    btn.classList.remove("in-cart");
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  console.log(cart);
}

document.addEventListener("click", (event) => addRemoveItems(event));

campusDropdown.addEventListener("change", loadStores);
categoryDropdown.addEventListener("change", loadStores);

loadStores();