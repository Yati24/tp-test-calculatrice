document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('calc-form');
  const resultEl = document.getElementById('result');
  const resultVal = resultEl.querySelector('.result-val');
  const historyList = document.getElementById('history-list');
  const clearBtn = document.getElementById('clear-history');

  async function loadHistory() {
    const res = await fetch('/api/history');
    const data = await res.json();
    historyList.innerHTML = '';
    data.forEach(item => {
      const li = document.createElement('li');
      li.classList.add('history-item');
      li.dataset.a = item.a;
      li.dataset.b = item.b;
      li.dataset.op = item.op;
      li.dataset.result = item.result;
      li.textContent = `${item.a} ${item.op} ${item.b} = ${item.result}`;
      li.addEventListener('click', () => {
        document.getElementById('a').value = item.a;
        document.getElementById('b').value = item.b;
        document.getElementById('op').value = item.op;
        resultVal.textContent = item.result;
        resultEl.querySelector('.result-left').textContent = `Chargé`;
        document.getElementById('a').focus();
      });
      historyList.appendChild(li);
    });
  }

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const a = document.getElementById('a').value;
    const b = document.getElementById('b').value;
    const op = document.getElementById('op').value;

    const res = await fetch('/api/calc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ a, b, op }),
    });
    const data = await res.json();
    if (data.error) {
      resultEl.querySelector('.result-left').textContent = 'Erreur';
      resultVal.textContent = data.error;
    } else {
      resultEl.querySelector('.result-left').textContent = 'Dernier résultat';
      resultVal.textContent = data.result;
      loadHistory();
    }
  });

  clearBtn.addEventListener('click', async () => {
    await fetch('/api/history/clear', { method: 'POST' });
    loadHistory();
  });

  loadHistory();
});
