(() => {
  const form = document.querySelector('.filters');
  const rows = [...document.querySelectorAll('tr[data-paper]')];
  const papers = [...document.querySelectorAll('details.paper')];
  function filter() {
    if (!form) return;
    const query = form.querySelector('input').value.trim().toLocaleLowerCase();
    const selected = [...form.querySelectorAll('select')];
    let count = 0;
    rows.forEach(row => {
      const show = row.dataset.search.includes(query) && selected.every(s => !s.value || row.dataset[s.name] === s.value);
      row.hidden = !show;
      document.getElementById(row.dataset.paper).hidden = !show;
      count += Number(show);
    });
    document.getElementById('result-count').textContent = `${count} / ${rows.length} 件を表示（採用・保留・関連を含む）`;
    document.getElementById('empty').hidden = count !== 0;
  }
  form?.addEventListener('input', filter);
  form?.addEventListener('change', filter);
  document.getElementById('reset-filters')?.addEventListener('click', () => { form.reset(); filter(); });
  document.querySelectorAll('[data-expand]').forEach(button => button.addEventListener('click', () => {
    papers.filter(p => !p.hidden).forEach(p => { p.open = button.dataset.expand === 'true'; });
  }));
  function revealTarget() {
    const id = location.hash.slice(1);
    const target = document.getElementById(id);
    if (target?.matches('details.paper')) {
      if (target.hidden && form) { form.reset(); filter(); }
      target.open = true;
      requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
    }
  }
  window.addEventListener('hashchange', revealTarget);
  document.querySelectorAll('.print-button').forEach(b => b.addEventListener('click', () => window.print()));
  let printState = [];
  window.addEventListener('beforeprint', () => {
    printState = papers.map(p => [p, p.open]);
    papers.filter(p => !p.hidden).forEach(p => p.open = true);
  });
  window.addEventListener('afterprint', () => printState.forEach(([p, open]) => p.open = open));
  filter();
  revealTarget();
})();
