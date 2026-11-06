
  /* The lightbox. A native <dialog> already holds focus inside itself,
     closes on Escape and paints its own backdrop, so this file adds the four
     things it does not do: the trigger, the click outside, the close button,
     and the focus return. */
  const initLightbox = () => {
    document.querySelectorAll('.media-figure.has-lightbox').forEach(figure => {
      const dialog = figure.querySelector('.lightbox');
      const image = figure.querySelector(':scope > img, :scope > a > img');
      if (!dialog || !image) return;
      /* Where the browser has no modal dialog the fallback has to stay: the
         link opens the picture's own file, and a button in its place would
         open nothing at all. Cite is checked the same way in 50-share.js. */
      if (typeof dialog.showModal !== 'function') return;
      /* Scripts off, the picture is a link to its own file. A picture drawn
         into a data: URI has no file to open, so the markup leaves the link
         out and the button below is the only trigger it ever had. A link
         goes somewhere and a button acts, so the link becomes a button once
         this file has run. */
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'lightbox-open';
      button.setAttribute('aria-haspopup', 'dialog');
      (figure.querySelector('a.lightbox-open') || image).replaceWith(button);
      button.append(image);
      button.addEventListener('click', () => dialog.showModal());
      /* A click on the backdrop is a click outside the dialog's own box. */
      dialog.addEventListener('click', event => {
        const box = dialog.getBoundingClientRect();
        const inside = event.clientX >= box.left && event.clientX <= box.right
          && event.clientY >= box.top && event.clientY <= box.bottom;
        if (!inside) dialog.close();
      });
      dialog.addEventListener('close', () => button.focus());
      const close = dialog.querySelector('.lightbox-close');
      if (close) close.addEventListener('click', () => dialog.close());
    });
  };
  kit.onReady(initLightbox);
