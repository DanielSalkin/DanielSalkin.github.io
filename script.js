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


// Keep explicit navigation selected throughout smooth scrolling; use the reading
// position once scrolling settles, including anchors close to the page bottom.
const projectLinks = [...document.querySelectorAll('.project-rail a')];
if (projectLinks.length) {
  const projectSections = projectLinks.map(link => document.getElementById(link.hash.slice(1)));
  const railLinks = document.querySelector('.project-rail-links');
  const progressMarker = document.createElement('span');
  progressMarker.className = 'rail-progress-marker';
  progressMarker.setAttribute('aria-hidden', 'true');
  railLinks.append(progressMarker);
  const projectReadingOffset = () => {
    const padding = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
    const margin = parseFloat(getComputedStyle(projectSections[0]).scrollMarginTop) || 0;
    return padding + margin;
  };
  function updateProgressMarker() {
    if (window.matchMedia('(max-width: 700px)').matches) return;
    const readingOffset = projectReadingOffset();
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const anchors = projectSections.map(section => Math.max(0, Math.min(maxScroll,
      section.getBoundingClientRect().top + window.scrollY - readingOffset)));
    const y = window.scrollY;
    let index = 0;
    while (index < anchors.length - 2 && y >= anchors[index + 1]) index++;
    const span = anchors[index + 1] - anchors[index];
    const fraction = span > 0 ? Math.max(0, Math.min(1, (y - anchors[index]) / span)) : 0;
    const railTop = railLinks.getBoundingClientRect().top;
    const centers = projectLinks.map(link => {
      const rect = link.getBoundingClientRect();
      return rect.top - railTop - railLinks.clientTop + railLinks.scrollTop + rect.height / 2;
    });
    progressMarker.style.top = `${centers[index] + fraction * (centers[index + 1] - centers[index])}px`;
  }
  const positionWaypoints = () => {
    const mobile = window.matchMedia('(max-width: 700px)').matches;
    if (mobile) {
      projectLinks.forEach(link => link.style.removeProperty('margin-bottom'));
      return;
    }
    const starts = projectSections.map(section => section.getBoundingClientRect().top);
    const span = starts[starts.length - 1] - starts[0];
    const occupied = projectLinks.reduce((total, link) => total + link.offsetHeight, 0);
    const available = Math.max(0, railLinks.clientHeight - occupied);
    projectLinks.forEach((link, index) => {
      const weight = index < starts.length - 1 && span > 0
        ? (starts[index + 1] - starts[index]) / span : 0;
      link.style.marginBottom = `${Math.max(0, weight * available)}px`;
    });
    updateProgressMarker();
  };
  // Keep all labels in normal flow; distribute only the spare vertical space.
  const waypointObserver = new ResizeObserver(positionWaypoints);
  projectSections.forEach(section => waypointObserver.observe(section));
  waypointObserver.observe(railLinks);
  window.addEventListener('resize', positionWaypoints);
  window.addEventListener('load', positionWaypoints);
  document.fonts?.ready.then(positionWaypoints);
  positionWaypoints();
  let framePending = false;
  let navigationTarget = null;
  let settleTimer;
  const selectProject = index => {
    projectLinks.forEach((link, position) => {
      if (position === index) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };
  const updateProjectRail = () => {
    framePending = false;
    updateProgressMarker();
    if (navigationTarget !== null) {
      selectProject(navigationTarget);
      return;
    }
    let current = 0;
    const marker = projectReadingOffset();
    projectSections.forEach((section, index) => {
      if (section.getBoundingClientRect().top <= marker) current = index;
    });
    if (window.scrollY > 0 && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 8) {
      current = projectLinks.length - 1;
    }
    selectProject(current);
  };
  const finishNavigation = () => {
    clearTimeout(settleTimer);
    navigationTarget = null;
    updateProjectRail();
  };
  projectLinks.forEach((link, index) => {
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      navigationTarget = index;
      selectProject(index);
      clearTimeout(settleTimer);
      settleTimer = setTimeout(finishNavigation, 250);
    });
  });
  window.addEventListener('scroll', () => {
    if (navigationTarget !== null) {
      clearTimeout(settleTimer);
      settleTimer = setTimeout(finishNavigation, 180);
    }
    if (!framePending) {
      framePending = true;
      requestAnimationFrame(updateProjectRail);
    }
  }, { passive: true });
  window.addEventListener('scrollend', finishNavigation);
  window.addEventListener('wheel', finishNavigation, { passive: true });
  window.addEventListener('touchstart', finishNavigation, { passive: true });
  window.addEventListener('keydown', event => {
    if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' '].includes(event.key)) finishNavigation();
  });
  window.addEventListener('hashchange', updateProjectRail);
  window.addEventListener('resize', updateProjectRail);
  window.addEventListener('load', updateProjectRail);
  updateProjectRail();
}
