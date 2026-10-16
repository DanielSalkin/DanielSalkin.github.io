document.querySelector('#year').textContent = new Date().getFullYear();
const lightbox = document.querySelector('#lightbox');
const image = lightbox.querySelector('img');
let previousFocus;
for (const link of document.querySelectorAll('a.zoom')) {
  link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || !lightbox.showModal) return;
    event.preventDefault();
    previousFocus = link;
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    lightbox.querySelector('p').textContent = image.alt;
    lightbox.showModal();
  });
}
lightbox.querySelector('button').addEventListener('click', () => lightbox.close());
lightbox.addEventListener('click', event => { if (event.target === lightbox) lightbox.close(); });
lightbox.addEventListener('close', () => { image.removeAttribute('src'); previousFocus?.focus(); });


const menuButton = document.querySelector('.menu-toggle');
const siteHeader = document.querySelector('.site-header');
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  siteHeader.classList.toggle('menu-open', open);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && siteHeader?.classList.contains('menu-open')) {
    siteHeader.classList.remove('menu-open');
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.focus();
  }
});
