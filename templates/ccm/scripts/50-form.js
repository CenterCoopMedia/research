
  /* The signup form. The markup posts on its own with no script at all, so
     everything here improves a form that already works: inline errors on the
     field, a summary of them at the top, and one sentence at the end that
     names what the reader gave. Every string the reader sees comes from the
     markup, so the copy lives in one file.

     There are two sends. Without `data-inline` the script checks the fields
     and then lets the native post run, so the endpoint answers with its own
     page. With it the script posts with fetch and the reader stays here, which
     works only when the endpoint sends CORS headers: without them the browser
     rejects an answer the endpoint already accepted, and the page would tell
     the reader their reply failed when it landed. */
  const initForm = () => {
    const form = document.querySelector('.signup');
    if (!form) return;
    const status = document.querySelector('.form-status');
    const summary = form.querySelector('.form-summary');
    const summaryList = summary.querySelector('ul');
    const sendError = form.querySelector('.form-send-error');
    const button = form.querySelector('button[type="submit"]');
    const trap = form.querySelector('.form-trap input');
    const fields = [...form.querySelectorAll('.form-input')];
    const inline = form.dataset.inline === 'true';
    let sending = false;

    /* Our own wording replaces the browser's bubbles. The attribute stays off
       the markup, so with this script gone the browser still checks a field
       before the page posts. */
    form.noValidate = true;

    const labelOf = input => document.querySelector(`label[for="${input.id}"]`).textContent;
    const errorOf = input => document.getElementById(`${input.id}-error`);

    const messageFor = input => {
      if (input.validity.valueMissing) return input.dataset.requiredError || '';
      if (input.validity.typeMismatch) return input.dataset.formatError || '';
      return '';
    };

    /* A field is checked when the reader leaves it. Once it has shown an
       error it is checked on every keystroke, so the message goes as soon as
       the reader fixes it. Nothing is checked while they are still typing the
       first time. */
    const check = input => {
      const message = messageFor(input);
      const error = errorOf(input);
      error.querySelector('.error-text').textContent = message;
      error.hidden = !message;
      if (message) {
        input.setAttribute('aria-invalid', 'true');
        input.dataset.live = 'true';
      } else {
        input.removeAttribute('aria-invalid');
      }
      return !message;
    };

    /* A reader on their way to the button gets no message on the way out of
       the field. The message would grow the form between the press and the
       release, the button would move out from under the pointer, and the
       click would be lost. The submit checks every field a moment later. */
    let pressing = false;
    button.addEventListener('pointerdown', () => { pressing = true; });
    document.addEventListener('pointerup', () => { pressing = false; });

    fields.forEach(input => {
      input.addEventListener('blur', () => { if (!pressing) check(input); });
      input.addEventListener('input', () => { if (input.dataset.live) check(input); });
    });

    const showSummary = broken => {
      summaryList.replaceChildren(...broken.map(input => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = `#${input.id}`;
        link.textContent = messageFor(input);
        item.append(link);
        return item;
      }));
      summary.hidden = false;
      summary.focus();
    };

    /* The end of the flow. The form goes and one sentence takes its place,
       and it names the reader's own answer so they can see it landed. The
       sentence takes the first field the reader filled: an empty field names
       nothing, and one of the fields is always required, so the short sentence
       is there for the trap alone. */
    const succeed = () => {
      const first = fields.find(input => input.value.trim());
      status.textContent = first
        ? form.dataset.success
            .replace('{field}', labelOf(first).toLowerCase())
            .replace('{value}', first.value)
        : form.dataset.successEmpty;
      form.hidden = true;
      status.hidden = false;
      status.focus();
    };

    const send = () => {
      sending = true;
      const label = button.textContent;
      button.textContent = button.dataset.sending;
      form.setAttribute('aria-busy', 'true');
      /* The two attributes, never the properties of the same name: a field
         called "action" would hide `form.action` behind its own input. The
         build stops such a name, and this reads the attribute in any case. */
      fetch(form.getAttribute('action'), {
        method: form.getAttribute('method'),
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      }).then(response => {
        if (!response.ok) throw new Error(response.status);
        succeed();
      }).catch(() => {
        sending = false;
        button.textContent = label;
        form.removeAttribute('aria-busy');
        sendError.hidden = false;
      });
    };

    form.addEventListener('submit', event => {
      if (sending) { event.preventDefault(); return; }
      sendError.hidden = true;
      /* Nothing leaves the page until every field passes, so a reader never
         waits on a post that the endpoint will reject. */
      const broken = fields.filter(input => !check(input));
      if (broken.length) { event.preventDefault(); showSummary(broken); return; }
      summary.hidden = true;
      /* A filled trap is a machine, so the page answers it and posts nothing. */
      if (trap && trap.value) { event.preventDefault(); succeed(); return; }
      /* The native post runs from here unless the form asked for the inline
         send. The page is about to go, so it changes nothing on the way out. */
      if (!inline) return;
      event.preventDefault();
      send();
    });
  };
  kit.onReady(initForm);
