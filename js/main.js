// ===== 모바일 네비 토글 =====
const toggle = document.querySelector('.nav__toggle');
const links = document.querySelector('.nav__links');
toggle.addEventListener('click', () => {
  const open = links.classList.toggle('is-open');
  toggle.setAttribute('aria-expanded', String(open));
});
links.querySelectorAll('a').forEach((a) =>
  a.addEventListener('click', () => links.classList.remove('is-open'))
);

// ===== 칩 선택 (그룹당 하나만) =====
document.querySelectorAll('.chips').forEach((group) => {
  group.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    group.querySelectorAll('.chip').forEach((c) => c.classList.remove('is-active'));
    chip.classList.add('is-active');
  });
});

function getSelected(name) {
  const active = document.querySelector(`.chips[data-name="${name}"] .chip.is-active`);
  return active ? active.dataset.value : '';
}

// ===== 추천 폼 제출 =====
const form = document.getElementById('menu-form');
const errorEl = document.getElementById('form-error');
const resultEl = document.getElementById('result');
const submitBtn = document.getElementById('submit-btn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorEl.textContent = '';
  errorEl.className = 'form__hint';

  const situation = getSelected('situation');
  const mood = getSelected('mood');
  const budget = getSelected('budget');
  const exclude = document.getElementById('exclude').value.trim();

  // [실패처리 1] 빈 입력(필수값 누락)
  if (!situation || !mood) {
    errorEl.textContent = '상황과 기분은 꼭 골라줘! (필수)';
    errorEl.classList.add('error');
    return;
  }

  await requestRecommend({ situation, mood, budget, exclude });
});

async function requestRecommend(payload) {
  // 로딩 상태
  submitBtn.disabled = true;
  resultEl.innerHTML = `
    <div class="state">
      <div class="spinner"></div>
      <p class="state__msg">AI가 오늘 저녁 고르는 중… 🍳</p>
    </div>`;

  // [실패처리 3] 지연/타임아웃 — 20초 넘으면 중단
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60000);

  try {
    const res = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    clearTimeout(timer);

    // [실패처리 2] API 오류(4xx/5xx)
    if (!res.ok) {
      throw new Error(`서버 오류 (${res.status})`);
    }

    const data = await res.json();
    if (!data.menus || !data.menus.length) {
      throw new Error('추천 결과를 받지 못했어');
    }
    renderResult(data);
  } catch (err) {
    clearTimeout(timer);
    const msg =
      err.name === 'AbortError'
        ? '응답이 너무 늦네… 잠시 후 다시 시도해줘 ⏳'
        : '메뉴를 불러오지 못했어. 잠시 후 다시 시도해줘 🙏';
    resultEl.innerHTML = `
      <div class="state state--error">
        <p class="state__msg">${msg}</p>
        <button class="btn btn--ghost state__retry" onclick="document.getElementById('submit-btn').click()">다시 시도</button>
      </div>`;
  } finally {
    submitBtn.disabled = false;
  }
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"]/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])
  );
}

function renderResult(data) {
  const cards = data.menus
    .slice(0, 3)
    .map(
      (m) => `
    <div class="card">
      <div class="card__emoji">${esc(m.emoji || '🍽️')}</div>
      <h3 class="card__name">${esc(m.name)}</h3>
      <p class="card__reason">${esc(m.reason)}</p>
      <span class="card__keyword">🔎 ${esc(m.keyword || m.name)}</span>
    </div>`
    )
    .join('');

  resultEl.innerHTML = `
    ${data.comment ? `<p class="result__comment">${esc(data.comment)}</p>` : ''}
    <div class="cards">${cards}</div>`;
  resultEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ===== 문의 폼 (로컬 안내만) =====
const contactForm = document.getElementById('contact-form');
const contactMsg = document.getElementById('contact-msg');
contactForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const msg = document.getElementById('c-msg').value.trim();
  contactMsg.className = 'form__hint';
  if (!msg) {
    contactMsg.textContent = '내용을 입력해줘!';
    contactMsg.classList.add('error');
    return;
  }
  contactForm.reset();
  contactMsg.textContent = '보냈어! 소중한 의견 고마워 🙌';
  contactMsg.classList.add('ok');
});
