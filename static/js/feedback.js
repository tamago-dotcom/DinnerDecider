/* feedback.js — フィードバック機能 */

(function () {
  let selectedFood = null;
  let selectedStar = 0;

  // 食べた料理ボタンの選択
  document.querySelectorAll('.feedback-food-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.feedback-food-btn').forEach(function (b) {
        b.classList.remove('selected');
      });
      btn.classList.add('selected');
      selectedFood = btn.dataset.food;

      const otherInput = document.getElementById('feedbackOtherInput');
      if (selectedFood === 'その他') {
        otherInput.style.display = 'block';
        otherInput.focus();
      } else {
        otherInput.style.display = 'none';
        otherInput.value = '';
      }

      updateSubmitBtn();
    });
  });

  // その他テキスト入力
  const otherInput = document.getElementById('feedbackOtherInput');
  if (otherInput) {
    otherInput.addEventListener('input', function () {
      updateSubmitBtn();
    });
  }

  // 星評価ボタンの生成・操作
  const starsRow = document.querySelector('.stars-row');
  if (starsRow) {
    for (let i = 1; i <= 5; i++) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'star-btn';
      btn.dataset.star = i;
      btn.textContent = '★';
      btn.setAttribute('aria-label', i + '点');

      btn.addEventListener('mouseenter', function () {
        const hovered = parseInt(this.dataset.star);
        starsRow.querySelectorAll('.star-btn').forEach(function (s) {
          s.classList.toggle('active', parseInt(s.dataset.star) <= hovered);
        });
      });

      btn.addEventListener('mouseleave', function () {
        starsRow.querySelectorAll('.star-btn').forEach(function (s) {
          s.classList.toggle('active', parseInt(s.dataset.star) <= selectedStar);
        });
      });

      btn.addEventListener('click', function () {
        selectedStar = parseInt(this.dataset.star);
        starsRow.querySelectorAll('.star-btn').forEach(function (s) {
          s.classList.toggle('active', parseInt(s.dataset.star) <= selectedStar);
        });
        updateSubmitBtn();
      });

      starsRow.appendChild(btn);
    }
  }

  function updateSubmitBtn() {
    const submitBtn = document.getElementById('feedbackSubmitBtn');
    if (!submitBtn) return;

    let foodValue = selectedFood;
    if (foodValue === 'その他') {
      const otherVal = document.getElementById('feedbackOtherInput');
      foodValue = otherVal ? otherVal.value.trim() : '';
    }

    const ready = foodValue && foodValue !== 'その他' && selectedStar >= 1;
    submitBtn.disabled = !ready;
  }

  // フィードバック送信
  window.submitFeedback = async function () {
    const submitBtn = document.getElementById('feedbackSubmitBtn');
    const resultId = window.FEEDBACK_RESULT_ID;

    let actualFood = selectedFood;
    if (actualFood === 'その他') {
      const otherInput = document.getElementById('feedbackOtherInput');
      actualFood = otherInput ? otherInput.value.trim() : '';
    }

    if (!actualFood || selectedStar < 1) return;

    submitBtn.disabled = true;
    submitBtn.textContent = '送信中...';

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          result_id: resultId,
          actual_food: actualFood,
          satisfaction: selectedStar,
        }),
      });
      const data = await res.json();

      if (data.success) {
        document.getElementById('feedbackForm').style.display = 'none';
        document.getElementById('feedbackDone').style.display = 'block';
      } else {
        alert('エラー: ' + (data.message || '送信に失敗しました'));
        submitBtn.disabled = false;
        submitBtn.textContent = 'フィードバックを送る';
      }
    } catch (e) {
      alert('通信エラーが発生しました');
      submitBtn.disabled = false;
      submitBtn.textContent = 'フィードバックを送る';
    }
  };
})();
