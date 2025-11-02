function openModal(){ const m=document.getElementById('modal'); m.classList.add('open'); }
function closeModal(){ const m=document.getElementById('modal'); m.classList.remove('open'); }
window.openModal = openModal; window.closeModal = closeModal;

document.addEventListener('htmx:afterSwap', (e) => {
  if (!e.detail.target) return;
  const closable = ['patients-table', 'doctors-table', 'appointments-table'];
  if (closable.includes(e.detail.target.id)) {
    closeModal();
  }
});
