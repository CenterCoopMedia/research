  const print = document.querySelector('.print-button');
  if (print) {
    print.hidden = false;
    print.addEventListener('click', () => window.print());
  }
