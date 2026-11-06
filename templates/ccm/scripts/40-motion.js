  const media = matchMedia('(prefers-reduced-motion: reduce)');
  const motion = document.querySelector('.motion-button');
  const motionLabel = motion && (motion.querySelector('.motion-label') || motion);
  let paused = media.matches;
  const setMotion = () => {
    root.classList.toggle('no-motion', paused);
    /* The stylesheet stops at .01ms under prefers-reduced-motion unless this
       class says the reader asked for motion back. */
    root.classList.toggle('motion-on', !paused);
    if (!motion) return;
    const label = paused ? 'Resume motion' : 'Pause motion';
    if (motionLabel) motionLabel.textContent = label;
    motion.setAttribute('aria-label', label);
    motion.setAttribute('aria-pressed', String(paused));
  };
  setMotion();
  if (motion) {
    motion.hidden = false;
    motion.addEventListener('click', () => { paused = !paused; setMotion(); });
  }
  media.addEventListener('change', event => { paused = event.matches; setMotion(); });

