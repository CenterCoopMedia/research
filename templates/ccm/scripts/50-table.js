
  /* A table sorts in place. The rows move, the focus stays on the button the
     reader pressed, aria-sort states the column and the direction, and one
     hidden status sentence states the new order for a reader who cannot see
     the rows move. Without this file the table is still a whole table. */
  const ORDERS = {
    'number-up': 'smallest first',
    'number-down': 'largest first',
    'text-up': 'A to Z',
    'text-down': 'Z to A',
  };

  const cellValue = (row, index, type) => {
    const cell = row.children[index];
    if (!cell) return type === 'number' ? 0 : '';
    if (type === 'number') return Number(cell.dataset.value);
    return cell.textContent.trim();
  };

  const sortTable = (button, table, status) => {
    const head = button.closest('th');
    const index = Number(button.dataset.column);
    const type = button.dataset.type;
    /* A first press on a column of numbers puts the largest at the top,
       which is the order a reader of a ranking wants. Text starts at A. */
    const up = head.getAttribute('aria-sort') === 'descending'
      || (head.getAttribute('aria-sort') === 'none' && type === 'text');
    const body = table.tBodies[0];
    const rows = [...body.rows];
    rows.sort((one, two) => {
      const first = cellValue(one, index, type);
      const second = cellValue(two, index, type);
      const order = type === 'number' ? first - second
        : String(first).localeCompare(String(second));
      return up ? order : -order;
    });
    rows.forEach(row => body.appendChild(row));
    [...table.tHead.rows[0].cells].forEach(cell => cell.setAttribute('aria-sort', 'none'));
    head.setAttribute('aria-sort', up ? 'ascending' : 'descending');
    if (status) {
      /* The name of the column and nothing else: the unit sits in a span
         beside it, and "Grants per year" is not the name of the column. */
      const name = button.querySelector('.column-name').textContent.trim();
      status.textContent = `Sorted by ${name}, ${ORDERS[`${type}-${up ? 'up' : 'down'}`]}.`;
    }
  };

  const initTables = () => {
    document.querySelectorAll('.column-sort').forEach(button => {
      const table = button.closest('table');
      const status = table.closest('.section') || document;
      button.addEventListener('click', () => {
        sortTable(button, table, status.querySelector('.table-status'));
      });
    });
  };
  kit.onReady(initTables);
