/* Quiz application logic */

let questions = [];
let currentIndex = 0;
let answers = {}; // { q_id: { value, category } }

async function loadQuestions() {
  try {
    const res = await fetch('/api/questions');
    const data = await res.json();
    questions = data.questions;
    document.getElementById('quizLoading').style.display = 'none';
    document.getElementById('quizBody').style.display = 'block';
    renderQuestion();
  } catch (e) {
    document.getElementById('quizLoading').innerHTML =
      '<p style="color:#e74c3c">質問の読み込みに失敗しました。<a href="/quiz">再読み込み</a></p>';
  }
}

function renderQuestion() {
  const q = questions[currentIndex];
  const total = questions.length;

  // Progress
  const pct = ((currentIndex + 1) / total * 100).toFixed(0);
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('progressText').textContent = `${currentIndex + 1} / ${total}`;

  // Question
  document.getElementById('questionNumber').textContent = `Q${currentIndex + 1}`;
  document.getElementById('questionText').textContent = q.text;

  // Options
  const list = document.getElementById('optionsList');
  list.innerHTML = '';
  const saved = answers[q.id];

  q.options.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn' + (saved !== undefined && saved.value === opt.value && saved.optIdx === i ? ' selected' : '');
    btn.textContent = opt.label;
    btn.addEventListener('click', () => selectOption(opt.value, i));
    list.appendChild(btn);
  });

  // Nav buttons
  document.getElementById('btnPrev').style.visibility = currentIndex === 0 ? 'hidden' : 'visible';
  updateNextButton();

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function selectOption(value, optIdx) {
  const q = questions[currentIndex];
  answers[q.id] = { value, category: q.category, optIdx };

  document.querySelectorAll('.option-btn').forEach((btn, i) => {
    btn.classList.toggle('selected', i === optIdx);
  });

  updateNextButton();
}

function updateNextButton() {
  const q = questions[currentIndex];
  const answered = answers[q.id] !== undefined;
  const btn = document.getElementById('btnNext');
  btn.disabled = !answered;

  if (currentIndex === questions.length - 1) {
    btn.textContent = '結果を見る 🍽️';
  } else {
    btn.textContent = '次へ →';
  }
}

function nextQuestion() {
  const q = questions[currentIndex];
  if (answers[q.id] === undefined) return;

  if (currentIndex < questions.length - 1) {
    currentIndex++;
    renderQuestion();
  } else {
    submitAnswers();
  }
}

function prevQuestion() {
  if (currentIndex > 0) {
    currentIndex--;
    renderQuestion();
  }
}

async function submitAnswers() {
  document.getElementById('quizBody').style.display = 'none';
  document.getElementById('quizSubmitting').style.display = 'flex';

  const payload = { answers: {} };
  for (const [qid, ans] of Object.entries(answers)) {
    payload.answers[qid] = { value: ans.value, category: ans.category };
  }

  try {
    const res = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.result_id) {
      window.location.href = '/result/' + data.result_id;
    } else {
      throw new Error('No result id');
    }
  } catch (e) {
    document.getElementById('quizSubmitting').innerHTML =
      '<p style="color:#e74c3c">送信に失敗しました。<a href="/quiz">もう一度試す</a></p>';
  }
}

// Boot
document.addEventListener('DOMContentLoaded', loadQuestions);
