const campusDropdown = document.getElementById("campusDropdown");
const categoryDropdown = document.getElementById("categoryDropdown");
const storeList = document.getElementById("storeList");

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
          </tr>
        `;

        store.products.forEach(product => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${product.productName}</td>
            <td>$${product.price.toFixed(2)}</td>
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
}

campusDropdown.addEventListener("change", loadStores);
categoryDropdown.addEventListener("change", loadStores);

loadStores();