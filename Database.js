// --------------------------
// Service Worker Registration
// --------------------------
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}

// --------------------------
// Toast Notification Logic
// --------------------------
function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.style.opacity = 1;
  setTimeout(() => {
    toast.style.opacity = 0;
  }, 2000);
}

// --------------------------
// Theme Toggle (Dark/Light)
// --------------------------
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('light');
  document.querySelector('.sidebar').classList.toggle('light');
  document.getElementById('loginBox').classList.toggle('light');
  document.getElementById('menuBtn').classList.toggle('light');
  themeToggle.classList.toggle('light');
  themeToggle.innerHTML = document.body.classList.contains('light')
    ? '<i class="fas fa-sun"></i>'
    : '<i class="fas fa-moon"></i>';
  localStorage.setItem(
    'theme',
    document.body.classList.contains('light') ? 'light' : 'dark'
  );
});
window.addEventListener('load', () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    themeToggle.click();
  }
  autoLanguage();
});
function autoTheme() {
  const hour = new Date().getHours();
  if (hour >= 7 && hour < 19 && !document.body.classList.contains('light')) {
    themeToggle.click();
  }
}
autoTheme();

// --------------------------
// Login Logic
// --------------------------
function handleLogin() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const loader = document.getElementById('loader');
  if (!username || !password) {
    showToast('Lütfen tüm alanları doldurun.');
    return;
  }
  loader.style.display = 'block';
  setTimeout(() => {
    loader.style.display = 'none';
    if (username === 'admin' && password === '1234') {
      document.getElementById('login').style.display = 'none';
      document.getElementById('panel').style.display = 'flex';
      renderChart();
      showToast('Giriş başarılı!');
    } else {
      showToast('Geçersiz giriş bilgileri');
    }
  }, 1000);
}

// --------------------------
// Sidebar Toggle Logic
// --------------------------
document.getElementById('menuBtn').addEventListener('click', () => {
  const sidebar = document.getElementById('sidebar');
  const btn = document.getElementById('menuBtn');
  sidebar.classList.toggle('open');
  if (sidebar.classList.contains('open')) {
    btn.innerHTML = '<i class="fas fa-times"></i>';
  } else {
    btn.innerHTML = '<i class="fas fa-bars"></i>';
  }
});

// --------------------------
// Section Navigation Logic
// --------------------------
function showSection(id) {
  document.querySelectorAll('.section').forEach((s) =>
    s.classList.remove('active')
  );
  document.getElementById(id).classList.add('active');
  if (window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('menuBtn').innerHTML = '<i class="fas fa-bars"></i>';
  }
}

// --------------------------
// Language Toggle Logic
// --------------------------
let lang = 'tr';
document.getElementById('langToggle').addEventListener('click', () => {
  lang = lang === 'tr' ? 'en' : 'tr';
  localizeText();
  document.getElementById('langToggle').textContent = lang.toUpperCase();
  localStorage.setItem('lang', lang);
});
function autoLanguage() {
  const savedLang = localStorage.getItem('lang');
  if (savedLang) {
    lang = savedLang;
    document.getElementById('langToggle').textContent = lang.toUpperCase();
    localizeText();
  }
}
function localizeText() {
  const dict = {
    en: {
      Anasayfa: 'Home',
      'TC Sorgu': 'ID Query',
      Telefon: 'Phone',
      İsimden: 'By Name',
      'Adres Sorgu': 'Address Query',
      'Plaka Sorgu': 'Plate Query',
      'E-Posta Sorgu': 'Email Query',
      'Ad Soyad': 'By Full Name',
      'Panel Girişi': 'Panel Login',
      'Kullanıcı Adı': 'Username',
      Şifre: 'Password',
      'Giriş Yap': 'Login',
      'Yeni API eklendi. Artık isimden doğum tarihi sorgusu yapılabilir!':
        'New API added. You can now query birthdate by name!',
      'Aktif API': 'Active APIs',
      Kullanıcı: 'Users',
      Premium: 'Premium',
      'Toplam Sorgu': 'Total Queries',
      Destek: 'Support',
      'TC numarasına ait temel bilgileri sorgulayabilirsiniz.':
        'You can query basic info by ID number.',
      'Telefon numarasına kayıtlı kişi bilgilerini sorgulayın.':
        'Query person info by phone number.',
      'Ad Soyad bilgisine göre kişi sorgusu yapabilirsiniz.':
        'You can query by full name.',
      'Adres bilgisine göre sorgulama yapabilirsiniz.':
        'You can query by address.',
      'Plaka bilgisiyle araç bilgilerini sorgulayın.':
        'Query vehicle info by license plate.',
      'E-posta adresiyle kullanıcı bilgilerini sorgulayın.':
        'Query user info by email address.',
    },
    tr: {},
  };
  document.querySelectorAll('[data-key]').forEach((el) => {
    const key = el.getAttribute('data-key');
    if (dict[lang][key]) el.textContent = dict[lang][key];
  });
}

// --------------------------
// Chart Rendering
// --------------------------
function renderChart() {
  const ctx = document.getElementById('apiChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
      datasets: [
        {
          label: 'Sorgu Adedi',
          data: [12, 19, 3, 5, 2, 3],
          borderColor: 'rgba(0, 255, 255, 0.8)',
          backgroundColor: 'rgba(0, 255, 255, 0.2)',
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

// --------------------------
// Generic Query Handler
// --------------------------
function handleQuery(type) {
  let inputId, resultId;
  if (type === 'tc') {
    inputId = 'tcInput';
    resultId = 'tcResult';
  }
  if (type === 'tel') {
    inputId = 'telInput';
    resultId = 'telResult';
  }
  if (type === 'isim') {
    inputId = 'isimInput';
    resultId = 'isimResult';
  }
  if (type === 'adres') {
    inputId = 'adresInput';
    resultId = 'adresResult';
  }
  if (type === 'plaka') {
    inputId = 'plakaInput';
    resultId = 'plakaResult';
  }
  if (type === 'eposta') {
    inputId = 'epostaInput';
    resultId = 'epostaResult';
  }
  const value = document.getElementById(inputId).value.trim();
  if (!value) {
    showToast('Lütfen bir değer girin.');
    return;
  }
  // Burada gerçek API çağrısı yapılabilir. Şimdilik örnek amaçlı sonucu gösteriyoruz.
  setTimeout(() => {
    document.getElementById(resultId).innerHTML = `<p>Sonuç: ${value} için veri bulunamadı.</p>
      <button onclick="shareResult('${type}','${value}')">
        <i class='fas fa-share'></i> Paylaş
      </button>`;
    updateHistory(type, value);
    showToast('Sorgu tamamlandı');
  }, 500);
}

// --------------------------
// Ad Soyad Query Handler (Türkçe karakter desteği var)
// --------------------------
function handleAdSoyadQuery() {
  const ad = document.getElementById('adInput').value.trim();
  const soyad = document.getElementById('soyadInput').value.trim();
  const il = document.getElementById('ilInput').value.trim();
  const resultDiv = document.getElementById('adsoyadResult');
  if (!ad || !soyad || !il) {
    resultDiv.innerHTML = "<p style='color:red;'>Tüm alanları doldurun.</p>";
    return;
  }
  resultDiv.innerHTML = '⏳ Sorgulanıyor...';

  // encodeURIComponent sayesinde "ü, ç, ğ" vb. karakterler doğru kodlanacak
  const url = `http://ramowlf.xyz/ramowlf/adsoyad.php?ad=${encodeURIComponent(
    ad
  )}&soyad=${encodeURIComponent(soyad)}&il=${encodeURIComponent(il)}`;

  fetch(url)
    .then((response) => response.text())
    .then((data) => {
      resultDiv.innerHTML = `<pre>${data}</pre>`;
    })
    .catch((error) => {
      resultDiv.innerHTML = `<p style='color:red;'>Hata oluştu: ${error}</p>`;
    });
}

// --------------------------
// History & Clipboard
// --------------------------
function updateHistory(type, value) {
  const key = type + 'History';
  let history = JSON.parse(localStorage.getItem(key)) || [];
  history.unshift({ value, time: new Date().toLocaleString() });
  if (history.length > 5) history.pop();
  localStorage.setItem(key, JSON.stringify(history));
}
function shareResult(type, text) {
  navigator.clipboard.writeText(text).then(() => showToast('Kopyalandı'));
}

// --------------------------
// Responsive Sidebar Reset
// --------------------------
window.addEventListener('resize', () => {
  if (window.innerWidth > 768) {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('menuBtn').innerHTML = '<i class="fas fa-bars"></i>';
  }
});
