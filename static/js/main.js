
/* ---------- UTILITY ---------- */
function $(sel) { return document.querySelector(sel); }
function $all(sel) { return Array.from(document.querySelectorAll(sel)); }

/* ---------- PRODUCTS ---------- */
function renderProductsGrid(targetId = "product-list", limit = 0) {
  const container = document.getElementById(targetId);
  if (!container) return;
  const list = limit > 0 ? products.slice(0, limit) : products;

  container.innerHTML = list.map(p => `
    <div class="product-card style-b">
      <a href="/products/${p.id}/">
        <div class="product-image-wrapper">
          <img src="${p.image}" alt="${p.name}" class="product-image"/>
        </div>
        <div class="product-info">
          <h3 class="product-name">${p.name}</h3>
          <p class="product-description">${p.description}</p>
          <p class="price">Rs. ${p.price}</p>
        </div>
      </a>
      <button class="btn-cart" onclick="addToCart(${p.id}, this)">Add to Cart</button>
    </div>
  `).join("");
}

function renderProductDetail() {
  const detailContainer = document.getElementById("product-detail");
  if (!detailContainer) return;

  const product = products.find(p => p.id === productId);
  if (!product) {
    detailContainer.innerHTML = "<p>Product not found.</p>";
    return;
  }

  let galleryImages = product.gallery.length ? product.gallery : [product.image];

  detailContainer.innerHTML = `
    <div class="product-detail-wrapper">
      <div class="carousel-container">
        <img id="carouselMainImage" src="${galleryImages[0]}" alt="${product.name}" class="detail-main-image"/>
        <button class="carousel-arrow left" onclick="prevCarouselImage()">&#10094;</button>
        <button class="carousel-arrow right" onclick="nextCarouselImage()">&#10095;</button>
        <div class="carousel-thumbnails">
          ${galleryImages.map((img, i) => `<img src="${img}" class="thumb-img" onclick="goToCarouselImage(${i})">`).join('')}
        </div>
      </div>
      <div class="product-info">
        <h2>${product.name}</h2>
        <p>${product.description}</p>
        <p style="font-weight:700">Rs. ${product.price}</p>
        <div>
          <input type="number" id="qty" min="1" value="1"/>
          <button class="btn-cart" onclick="addToCart(${product.id})">Add to Cart</button>
        </div>
      </div>
    </div>
  `;

  currentCarouselImages = galleryImages;
  currentCarouselIndex = 0;
}
// Carousel state
let currentCarouselImages = [];
let currentCarouselIndex = 0;

function prevCarouselImage() {
  currentCarouselIndex = (currentCarouselIndex - 1 + currentCarouselImages.length) % currentCarouselImages.length;
  document.getElementById("carouselMainImage").src = currentCarouselImages[currentCarouselIndex];
}

function nextCarouselImage() {
  currentCarouselIndex = (currentCarouselIndex + 1) % currentCarouselImages.length;
  document.getElementById("carouselMainImage").src = currentCarouselImages[currentCarouselIndex];
}

function goToCarouselImage(index) {
  currentCarouselIndex = index;
  document.getElementById("carouselMainImage").src = currentCarouselImages[currentCarouselIndex];
}

// Call this function when page loads
document.addEventListener("DOMContentLoaded", renderProductDetail);



/* ---------- CART ---------- */
function getCart() { return JSON.parse(localStorage.getItem("cart") || "[]"); }
function setCart(cart) { localStorage.setItem("cart", JSON.stringify(cart)); }

function addToCart(id, fromElement=null) {
  const qtyInput = document.getElementById("qty") || document.getElementById(`qty-${id}`);
  const qty = Math.max(1, parseInt(qtyInput?.value || 1, 10));
  const product = products.find(p => p.id === id);
  if (!product) return alert("Product not found.");
  const cart = getCart();
  const existing = cart.find(i => i.id === id);
  if (existing) existing.qty += qty;
  else cart.push({ id: product.id, name: product.name, price: product.price, image: product.image, qty });
  setCart(cart);
  showToast("Added to cart", 1500, product.image, fromElement);
  renderCart();
}

/* ---------- RENDER CART PAGE ---------- */
function renderCart() {
  const cartSection = document.querySelector(".cart-section");
  const cartTotal = document.getElementById("cart-total");
  if (!cartSection || !cartTotal) return;
  const cart = getCart();
  if (!cart.length) {
    cartSection.innerHTML = "<p class='center small-muted'>Your cart is empty.</p>";
    cartTotal.innerHTML = "";
    return;
  }
  let total = 0;
  cartSection.innerHTML = cart.map((item, idx) => {
    const subtotal = item.price * item.qty;
    total += subtotal;
    return `
      <div class="cart-item" data-index="${idx}">
        <img src="${item.image}" alt="${item.name}">
        <div>
          <h3>${item.name}</h3>
          <div>
            <label>Qty
              <input class="qty-input" data-index="${idx}" type="number" min="1" value="${item.qty}">
            </label>
            <button class="btn-cart remove-btn" data-index="${idx}">Remove</button>
          </div>
          <p>Price: Rs. ${item.price}</p>
          <p style="font-weight:700">Subtotal: Rs. ${subtotal}</p>
        </div>
      </div>
    `}).join("");
  cartTotal.innerHTML = `Total: Rs. ${total}`;

  $all(".qty-input").forEach(input => input.onchange = (e) => {
    const idx = parseInt(e.target.dataset.index, 10);
    let newQty = Math.max(1, parseInt(e.target.value, 10) || 1);
    const cart = getCart();
    cart[idx].qty = newQty;
    setCart(cart);
    renderCart();
  });
  $all(".remove-btn").forEach(btn => btn.onclick = (e) => {
    const idx = parseInt(e.target.dataset.index, 10);
    const cart = getCart();
    cart.splice(idx,1);
    setCart(cart);
    renderCart();
  });
}
/* ---------- AUTH ---------- */
function initAuthForms() {
  // --- SIGNUP ---
  const signupForm = document.getElementById("signup-form");
  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(signupForm);
      // backend expects 'name', 'email', 'password'
      try {
        const res = await fetch("/signup/", {
          method: "POST",
          body: new URLSearchParams({
    ...Object.fromEntries(formData),
    next: formData.get('next') || window.location.href // ✅ preserve next
  }),
          credentials: "same-origin",
          headers: { "X-CSRFToken": getCSRF() }
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Signup failed");

        // update frontend state
        document.body.dataset.user = data.username;
        showUser();
        showToast(data.message);

        // redirect
        setTimeout(() => window.location.href = data.redirect || "/", 50);
      } catch (err) {
        alert(err.message);
      }
    });
  }

  // --- LOGIN ---
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(loginForm);
      // backend expects 'email' and 'password'
      try {
        const res = await fetch("/login/", {
          method: "POST",
          body: new URLSearchParams({
    ...Object.fromEntries(formData),
    next: formData.get('next') || window.location.href // ✅ preserve next
  }),
          credentials: "same-origin",
          headers: { "X-CSRFToken": getCSRF() }
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Login failed");

        // update frontend state
        document.body.dataset.user = data.username;
        showUser();
        showToast(data.message);

        // redirect
        setTimeout(() => window.location.href = data.redirect || "/", 50);
      } catch (err) {
        alert(err.message);
      }
    });
  }

  // --- LOGOUT ---




}
function bindLogout() {
  const logoutLink = document.getElementById("logout-link");
  if (!logoutLink) return;

  logoutLink.addEventListener("click", async (e) => {
    e.preventDefault();

    const res = await fetch("/logout/", {
      method: "POST",
      headers: { "X-CSRFToken": getCSRF() },
      credentials: "same-origin"
    });

    if (res.ok) {
      window.location.href = "/";
    } else {
      alert("Logout failed");
    }
  });
}

/* ---------- SHOW USER IN NAVBAR ---------- */
function showUser() {
  const username = document.body.dataset.user || "";

  const signinLinks = $all("#nav-signin, #mobile-nav-signin");
  const loginLinks  = $all("#nav-login, #mobile-nav-login");

  const oldBanner = document.querySelector(".user-banner-corner");
  if (oldBanner) oldBanner.remove();
window.USER_LOGGED_IN = !!username; // true if user is logged in

 if (username) {
  signinLinks.forEach(l => { l.style.opacity = "0.4"; l.style.pointerEvents = "none"; });
  loginLinks.forEach(l => { l.style.opacity = "0.4"; l.style.pointerEvents = "none"; });

  const banner = document.createElement("div");
  banner.className = "user-banner-corner";
  banner.innerHTML = `
    Welcome, <strong>${username}</strong>
    <a href="#" id="logout-link">
      <i class="fas fa-sign-out-alt"></i> Logout
    </a>
  `;
const navbar = document.querySelector(".navbar");
if (navbar) {
  navbar.appendChild(banner);
} else {
  document.body.appendChild(banner); // fallback
}
  bindLogout();
} else {
  signinLinks.forEach(l => { l.style.opacity = "1"; l.style.pointerEvents = "auto"; });
  loginLinks.forEach(l => { l.style.opacity = "1"; l.style.pointerEvents = "auto"; });
}
}


/* ---------- GALLERY ---------- */
let currentGallery = []; let currentIndex = 0;
function openGallery(productId, index) {
  const p = products.find(x => x.id === productId);
  if (!p) return;
  currentGallery = p.gallery || [p.image];
  currentIndex = index || 0;
  const modal = document.getElementById("galleryModal");
  const modalImage = document.getElementById("modalImage");
  if (modal && modalImage) {
    modal.style.display = "flex";
    modalImage.src = currentGallery[currentIndex];
  }
}
function closeGallery() { const modal = document.getElementById("galleryModal"); if (modal) modal.style.display = "none"; }
function prevImage(e) { e.stopPropagation(); currentIndex = (currentIndex - 1 + currentGallery.length) % currentGallery.length; document.getElementById("modalImage").src = currentGallery[currentIndex]; }
function nextImage(e) { e.stopPropagation(); currentIndex = (currentIndex + 1) % currentGallery.length; document.getElementById("modalImage").src = currentGallery[currentIndex]; }


/* ---------- CHECKOUT ---------- */
function handleCheckoutForm() {
  const form = document.getElementById("checkout-form");
  if (!form) return; // Stop if no checkout form on page

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const overlay = document.getElementById("processing-overlay");
    const errorBox = document.getElementById("order-error");
    const errorMsg = document.getElementById("error-msg");

function showError(msg) {
  if (!errorBox || !errorMsg) return alert(msg);
  errorMsg.textContent = msg;
  errorBox.style.display = "flex"; // show dynamically
  setTimeout(() => { errorBox.style.display = "none"; }, 5000);
}

// Show overlay only when submitting
if (overlay) overlay.style.display = "flex";


    if (!window.USER_LOGGED_IN) {
      const currentUrl = encodeURIComponent(window.location.href);
      window.location.href = `/signin/?next=${currentUrl}&msg=You need to sign in first`;
      return;
    }

    const fullName = form.querySelector("#full-name")?.value.trim();
    const email = form.querySelector("#email")?.value.trim();
    const contact = form.querySelector("#contact")?.value.trim();
    const address = form.querySelector("#address")?.value.trim();
    const paymentMethod = form.querySelector("#payment-method")?.value;
    const cart = JSON.parse(localStorage.getItem("cart") || "[]");

    if (!fullName || !email || !contact || !address || !paymentMethod || !cart.length) {
        showError("Please fill all fields and add items to cart.");
        return;
    }

    const payload = {
      full_name: fullName,
      email,
      contact,
      address,
      payment_method: paymentMethod,
      cart: cart.map(item => ({ id: item.id, quantity: item.qty }))
    };

    try {
      if (overlay) overlay.style.display = "flex"; // show spinner

      const response = await fetch("/checkout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRF()
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (overlay) overlay.style.display = "none"; // hide spinner

      if (data.status === "success") {
        localStorage.removeItem("cart");
        showToast("Order placed successfully!");
        window.location.href = data.redirect_url || "/thankyou/";
      } else {
        showError(data.message || "Checkout failed. Please try again.");
      }

    } catch (err) {
      if (overlay) overlay.style.display = "none"; // only if overlay exists
      console.error("Checkout error:", err);
      showError("Network error. Please try again.");
    }
  });
}

/* ---------- TOAST ---------- */
function showToast(msg = 'Added to cart', options = {}) {
  const {
    duration = 1500,
    background = '#4caf50',
    color = '#fff',
    icon = '✅',
    position = { top: '20px', right: '20px' }
  } = options;

  // Create toast container if it doesn't exist
  let toast = document.getElementById("site-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "site-toast";
    Object.assign(toast.style, {
      position: "fixed",
      zIndex: 9999,
      padding: "16px 24px",
      borderRadius: "50px",
      boxShadow: "0 8px 20px rgba(0,0,0,0.25)",
      fontWeight: "700",
      fontSize: "15px",
      display: "flex",
      alignItems: "center",
      gap: "10px",
      pointerEvents: "none",
      opacity: 0,
      transform: "translateY(-40px)",
      transition: "opacity 0.4s ease, transform 0.4s ease"
    });
    document.body.appendChild(toast);
  }

  // Apply position and colors
  Object.assign(toast.style, {
    top: position.top,
    right: position.right,
    background: background,
    color: color
  });

  // Set content
  toast.innerHTML = "";
  if (icon) {
    const iconElem = document.createElement("span");
    iconElem.textContent = icon;
    toast.appendChild(iconElem);
  }
  const textElem = document.createElement("span");
  textElem.textContent = msg;
  toast.appendChild(textElem);

  // Show toast
  toast.style.opacity = 1;
  toast.style.transform = "translateY(0)";

  // Hide toast after duration
  setTimeout(() => {
    toast.style.opacity = 0;
    toast.style.transform = "translateY(-40px)";
  }, duration);
}
/* ---------- MOBILE MENU ---------- */
  /* ---------- HAMBURGER MENU (CLASS-BASED) ---------- */
  const hamburger = document.getElementById("hamburgerBtn");
  const mobileMenu = document.getElementById("mobileMenu");

  if (hamburger && mobileMenu) {
    hamburger.addEventListener("click", () => {
      mobileMenu.classList.toggle("show");
    });
  }

/* ---------- HELPER ---------- */
function getCSRF() {
  return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
}

/* ---------- INIT ---------- */
window.addEventListener("DOMContentLoaded", () => {
  renderProductsGrid("product-list");
  renderProductsGrid("product-grid", 4);
  renderProductDetail();
  renderCart();
  initAuthForms();
  handleCheckoutForm();
  showUser();
  document.addEventListener("click", (e) => {
    const modal = document.getElementById("galleryModal");
    if (modal && e.target === modal) closeGallery();
  });
});
