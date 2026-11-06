
  /* Every partial has run and every stage is built and measured, so the page
     can take the layout that needs them. Anything that throws above this line
     leaves the reader the whole text in the order it is written. */
  kit.ready.forEach(work => work());
  root.classList.add('enhanced');
