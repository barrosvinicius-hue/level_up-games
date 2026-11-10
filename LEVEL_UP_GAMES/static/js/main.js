const toggle = document.getElementById("menuToggle");
const nav = document.getElementById("mainNav");
if (toggle && nav) toggle.addEventListener("click", () => nav.classList.toggle("open"));

document.querySelectorAll(".edit-product").forEach(button => {
  button.addEventListener("click", () => {
    const form = document.getElementById("productForm");
    if (!form) return;
    ["id","nome","descricao","plataforma","preco","estoque","imagem"].forEach(key => {
      const field = form.querySelector(`[name="${key}"]`) || document.getElementById("productId");
      if (field) field.value = button.dataset[key] || "";
    });
    const categoria = form.querySelector('[name="categoria_id"]');
    if (categoria) categoria.value = button.dataset.categoria || "";
    const destaque = form.querySelector('[name="destaque"]');
    if (destaque) destaque.checked = button.dataset.destaque === "1";
    form.scrollIntoView({behavior:"smooth",block:"center"});
  });
});
const reset = document.getElementById("resetProduct");
if (reset) reset.addEventListener("click", () => {
  const id = document.getElementById("productId");
  if (id) id.value = "";
});
