  /* Copy link and Cite. Both controls are hidden in the markup and shown here,
     so a reader with no script never sees a control that cannot work. */
  const toast = document.querySelector('.toast');
  const canPopover = toast && typeof toast.showPopover === 'function';
  /* --dur-toast is in 00-tokens.css, so the hold is stated once. The
     2400ms the brief states holds until the token lands. */
  const TOAST_HOLD = kit.ms('--dur-toast');
  let toastTimer = 0;

  /* Where anchor positioning is not available, how much of the footer's control
     group is already on the screen is what lifts the message clear of the
     control that opened it. The group is measured rather than the whole footer,
     so the message lands over the buttons and not over the band above them. The
     stylesheet reads it and the anchor overrides it. */
  const controls = document.querySelector('.footer-controls')
    || document.querySelector('.site-footer');
  const lift = () => {
    if (!controls) return;
    const shown = innerHeight - controls.getBoundingClientRect().top;
    toast.style.setProperty('--toast-lift', `${Math.max(0, shown)}px`);
  };

  const say = message => {
    if (!toast) return;
    /* The text is written before the popover opens, so the status region
       carries its message the first time a screen reader reads it. */
    toast.textContent = message;
    toast.hidden = false;
    lift();
    clearTimeout(toastTimer);
    if (!canPopover) {
      /* Where the popover API is not there, the element is shown in the page
         and hidden again after the hold. It keeps role="status", so the
         reader is told what happened either way. */
      toastTimer = setTimeout(() => { toast.hidden = true; }, TOAST_HOLD);
      return;
    }
    if (!toast.matches(':popover-open')) toast.showPopover();
    toastTimer = setTimeout(() => toast.hidePopover(), TOAST_HOLD);
  };

  /* A page opened from disk is not a secure context, so the clipboard API is
     not always there. The selection path is the fallback that still works. */
  const copyBySelection = value => {
    const field = document.createElement('textarea');
    field.value = value;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.opacity = '0';
    document.body.append(field);
    field.select();
    let done = false;
    try {
      done = document.execCommand('copy');
    } catch (error) {
      done = false;
    }
    field.remove();
    return done;
  };

  const report = (done, thing) => say(done
    ? `The ${thing} is on the clipboard.`
    : `The copy did not work. Select the ${thing} and copy it.`);

  const copy = (value, thing) => {
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      report(copyBySelection(value), thing);
      return;
    }
    navigator.clipboard.writeText(value).then(
      () => report(true, thing),
      () => report(copyBySelection(value), thing),
    );
  };

  /* The canonical address of the page, plus the section the reader is in, so a
     shared link opens where the reader was rather than at the cover. */
  const canonical = document.querySelector('link[rel="canonical"]');
  const address = () => {
    const base = canonical ? canonical.href : location.href.split('#')[0];
    return kit.section ? `${base}#${kit.section}` : base;
  };

  const copyLink = document.querySelector('.copy-link-button');
  if (copyLink && (navigator.clipboard || document.execCommand)) {
    copyLink.hidden = false;
    copyLink.addEventListener('click', () => copy(address(), 'link'));
  }

  const dialog = document.querySelector('.cite-dialog');
  const citeButton = document.querySelector('.cite-button');
  if (dialog && citeButton && typeof dialog.showModal === 'function') {
    citeButton.hidden = false;
    citeButton.addEventListener('click', () => dialog.showModal());
    dialog.querySelectorAll('.cite-close').forEach(
      button => button.addEventListener('click', () => dialog.close()),
    );
    /* <dialog> closes on Escape by itself. A click on the backdrop reports the
       dialog as the target, because the backdrop belongs to it, and so does a
       click on the padding of the dialog. The point decides between the two:
       the dialog closes only where the pointer is outside its own box. A
       button pressed from the keyboard reports the button as the target, so
       it never reaches this test. */
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      const outside = event.clientX < box.left || event.clientX > box.right
        || event.clientY < box.top || event.clientY > box.bottom;
      if (outside) dialog.close();
    });
    dialog.querySelectorAll('.cite-copy').forEach(button => {
      const source = document.getElementById(button.dataset.cite);
      if (!source) return;
      button.hidden = false;
      button.addEventListener('click', () => copy(source.textContent, 'citation'));
    });
  }
