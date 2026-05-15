document.addEventListener('DOMContentLoaded', () => {
    // --- Dark Mode Mantığı ---
    const themeBtn = document.getElementById('theme-toggle');
    const body = document.body;
    const icon = themeBtn.querySelector('i');

    // LocalStorage kontrolü
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        icon.classList.replace('fa-moon', 'fa-sun');
    }

    themeBtn.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        if (body.classList.contains('dark-mode')) {
            localStorage.setItem('theme', 'dark');
            icon.classList.replace('fa-moon', 'fa-sun');
        } else {
            localStorage.setItem('theme', 'light');
            icon.classList.replace('fa-sun', 'fa-moon');
        }
        updateChartTheme(); // Temaya göre grafiği güncelle
    });

    // --- Toast Bildirimi ---
    function showToast(message, isError = false) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.style.backgroundColor = isError ? '#e63946' : '#2a9d8f';
        toast.style.color = '#fff';
        toast.className = 'toast show';
        setTimeout(() => { toast.className = toast.className.replace('show', ''); }, 3000);
    }

    // --- Chart.js Kurulumu ---
    let probChart;
    const ctx = document.getElementById('probChart').getContext('2d');
    
    function initChart() {
        const textColor = body.classList.contains('dark-mode') ? '#e0e0e0' : '#2b2d42';
        
        // 1'den 100'e kadar teorik eğri oluşturma
        let labels = [];
        let dataPoints = [];
        for(let n=1; n<=100; n+=2) {
            labels.push(n);
            let prob = 1.0;
            for(let i=0; i<n; i++) prob *= (365-i)/365.0;
            dataPoints.push((1 - prob) * 100);
        }

        probChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Çakışma İhtimali (%)',
                    data: dataPoints,
                    borderColor: '#e63946',
                    backgroundColor: 'rgba(230, 57, 70, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: {display: true, text: 'Kişi Sayısı', color: textColor}, ticks: {color: textColor} },
                    y: { title: {display: true, text: 'Olasılık (%)', color: textColor}, ticks: {color: textColor}, max: 100 }
                },
                plugins: {
                    legend: { labels: { color: textColor } }
                }
            }
        });
    }
    
    function updateChartTheme() {
        if(probChart) {
            const textColor = body.classList.contains('dark-mode') ? '#e0e0e0' : '#2b2d42';
            probChart.options.scales.x.title.color = textColor;
            probChart.options.scales.x.ticks.color = textColor;
            probChart.options.scales.y.title.color = textColor;
            probChart.options.scales.y.ticks.color = textColor;
            probChart.options.plugins.legend.labels.color = textColor;
            probChart.update();
        }
    }

    initChart();

    // --- API'den Veri Çekme ve UI Güncelleme ---
    async function fetchStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();

            // Rakamları güncelle
            document.getElementById('stat-total').textContent = data.total_participants;
            document.getElementById('stat-prob').textContent = `%${data.theoretical_prob}`;
            document.getElementById('stat-collisions').textContent = data.total_collisions;
            document.getElementById('stat-popular').textContent = data.most_popular;

            // Çakışma listesini güncelle
            const matchesContainer = document.getElementById('matches-list');
            matchesContainer.innerHTML = ''; // Temizle

            if (data.collisions.length === 0) {
                matchesContainer.innerHTML = '<p style="text-align:center; color:#6c757d; margin-top:20px;">Henüz bir eşleşme bulunamadı. Veri girdikçe burası dolacak!</p>';
            } else {
                data.collisions.forEach(match => {
                    const div = document.createElement('div');
                    div.className = 'match-item';
                    
                    // Tarih formatını (GG-AA) güzelleştir
                    const parts = match.date.split('-');
                    const dateStr = `${parts[0]}.${parts[1]}`;

                    div.innerHTML = `
                        <span class="match-count">${match.count} Kişi</span>
                        <div class="match-date"><i class="fa-solid fa-cake-candles"></i> ${dateStr}</div>
                        <div class="match-names">${match.names}</div>
                    `;
                    matchesContainer.appendChild(div);
                });
            }
        } catch (error) {
            console.error("Veri çekilemedi:", error);
        }
    }

    // Sayfa yüklendiğinde verileri çek
    fetchStats();

    // --- Form Gönderimi ---
    const form = document.getElementById('birthday-form');
    const submitBtn = document.getElementById('submit-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const birthday = document.getElementById('birthday').value;

        // Butonu devre dışı bırak (Çift tıklama engelleme)
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Gönderiliyor...';

        try {
            const response = await fetch('/api/participants', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, birthday })
            });

            const result = await response.json();

            if (response.ok) {
                showToast(result.message);
                form.reset();
                fetchStats(); // Verileri anında yenile
            } else {
                showToast(result.error, true);
            }
        } catch (error) {
            showToast("Bir hata oluştu. Lütfen tekrar deneyin.", true);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Veriyi Gönder <i class="fa-solid fa-paper-plane"></i>';
        }
    });
});