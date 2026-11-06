
  /* The sidenote in the margin. The stylesheet measures the column between the
     reading column and the figure width; this file decides whether that column
     is wide enough to use, puts each note level with its own reference, and
     moves a note down when it would land on the note above it.

     The id the reference points at travels with the copy that is on the page,
     so the reference always lands the reader on a note they can see and the
     note the reference describes is always the one they hear. */
  const initNotes = () => {
    const columns = [...document.querySelectorAll('.sidenotes')];
    if (!columns.length) return;
    const px = name => parseFloat(getComputedStyle(root).getPropertyValue(name)) || 0;
    /* The narrowest column that still holds about 28 characters at --t0. Under
       it a note stops being a line of prose and becomes a stack of words, so
       the footnote at the end of the section is the better copy. */
    const LEAST = px('--s10') + px('--s7');
    const GAP = px('--s4');
    /* The width the stylesheet opens the margin column at, written the same
       way here so the two cannot drift apart. It is the width the wide layout
       folds its rail at as well, so a note goes to the side or to the foot at
       one width in either layout. */
    const margin = matchMedia('(min-width:1001px)');

    const rows = columns.map(column => {
      const section = column.closest('.section');
      const feet = [...section.querySelectorAll('.footnote-list > li')];
      const notes = [...column.querySelectorAll('.sidenote')].map((note, index) => ({
        note,
        foot: feet[index],
        id: feet[index] ? feet[index].id : '',
      }));
      return { section, column, notes };
    });

    /* The blocks that share the rail with the notes. A pull quote in the wide
       layout floats out of the column into the rail, and it is placed by the
       sentence it lifts rather than by this file, so the notes read its box
       and stand clear of it. In the reading layout it floats nowhere and the
       list is empty. Document order is vertical order here, because each one
       is placed by the paragraph it sits in. */
    const shared = (row, top) => [...row.section.querySelectorAll('.pullquote')]
      .filter(quote => getComputedStyle(quote).cssFloat !== 'none')
      .map(quote => {
        const box = quote.getBoundingClientRect();
        return { top: box.top - top, bottom: box.bottom - top };
      });

    /* Each note goes level with the top of its own reference, and a note that
       would land on the note above it, or on a block the rail already holds,
       goes under it instead. The answer is whether the stack that comes out of
       that still ends inside its section: four long notes beside three lines of
       text run past the end of the section and onto the section under it, and a
       stack like that belongs at the foot of the section instead. */
    const place = row => {
      const top = row.column.getBoundingClientRect().top;
      const taken = shared(row, top);
      const wanted = row.notes.map(pair => {
        const reference = document.getElementById(pair.note.dataset.ref);
        return reference ? reference.getBoundingClientRect().top - top : 0;
      });
      let floor = 0;
      row.notes.forEach((pair, index) => {
        let at = Math.max(wanted[index], floor);
        const height = pair.note.offsetHeight;
        taken.forEach(block => {
          if (at < block.bottom && at + height + GAP > block.top) {
            at = block.bottom + GAP;
          }
        });
        pair.note.style.top = `${Math.round(at)}px`;
        floor = at + height + GAP;
      });
      const last = row.notes[row.notes.length - 1];
      if (!last) return true;
      return last.note.getBoundingClientRect().bottom
        <= row.section.getBoundingClientRect().bottom;
    };

    const hand = (row, toSide) => {
      row.notes.forEach(pair => {
        if (!pair.id) return;
        const keep = toSide ? pair.note : pair.foot;
        const give = toSide ? pair.foot : pair.note;
        give.removeAttribute('id');
        keep.id = pair.id;
      });
    };

    /* The column is measured with the stylesheet's own arithmetic: it is shown
       for the length of one measurement and hidden again, inside one task, so
       nothing is painted in between. */
    const room = row => {
      row.column.style.display = 'block';
      const width = row.column.getBoundingClientRect().width;
      row.column.style.display = '';
      return width;
    };

    /* The column has to be wide enough to read and tall enough to hold the
       stack. The height is known only after the notes are placed, so the
       section takes the margin column, the notes are placed in it, and the
       section gives it back when the stack ends below the section does. */
    const sync = () => rows.forEach(row => {
      let fits = margin.matches && room(row) >= LEAST;
      row.section.classList.toggle('notes-side', fits);
      if (fits) {
        fits = place(row);
        if (!fits) row.section.classList.remove('notes-side');
      }
      hand(row, fits);
    });

    /* A section changes height when an image or a figure above the note lands,
       and it changes width when the window does, so the notes are placed again
       from the section itself rather than from the window alone. */
    const watch = new ResizeObserver(sync);
    rows.forEach(row => watch.observe(row.section));
    margin.addEventListener('change', sync);
    sync();
  };
  kit.onReady(initNotes);
