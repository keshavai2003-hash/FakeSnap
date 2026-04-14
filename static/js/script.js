// PARTICLE BACKGROUND
function createParticles() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particles';
    canvas.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
    `;
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    for (let i = 0; i < 80; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 2 + 0.5,
            speedX: (Math.random() - 0.5) * 0.5,
            speedY: (Math.random() - 0.5) * 0.5,
            opacity: Math.random() * 0.5 + 0.1
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.x += p.speedX;
            p.y += p.speedY;
            if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
            if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(74, 144, 226, ${p.opacity})`;
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}
createParticles();
// Load realtime stats on page load
async function loadStats() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        animateNumber('stat-checked', data.total_checked);
        animateNumber('stat-fake', data.total_fake_caught);
    } catch(e) {
        console.log('Stats error:', e);
    }
}

// Animate number counter
function animateNumber(id, target) {
    const el = document.getElementById(id);
    let current = 0;
    const step = Math.ceil(target / 50) || 1;
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.innerText = current.toLocaleString();
    }, 30);
}

function previewImage(event) {
    if (event.target.files.length === 0) return;
    const img = document.getElementById('preview-img');
    img.src = URL.createObjectURL(event.target.files[0]);
    document.getElementById('preview-container').style.display = 'block';
    document.getElementById('upload-area').style.display = 'none';
}

function removeImage() {
    document.getElementById('preview-container').style.display = 'none';
    document.getElementById('upload-area').style.display = 'block';
    document.getElementById('preview-img').src = '';
    document.getElementById('image-input').value = '';
}

async function predict() {
    const text = document.getElementById('news-text').value;
    const imageInput = document.getElementById('image-input');

    if (!text && imageInput.files.length === 0) {
        alert('Please enter text or upload an image!');
        return;
    }

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result-card').style.display = 'none';
    document.getElementById('error-msg').style.display = 'none';

    const formData = new FormData();
    formData.append('news_text', text);
    if (imageInput.files.length > 0) {
        formData.append('image', imageInput.files[0]);
    }

    const response = await fetch('/predict', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    // Hide loading
    document.getElementById('loading').style.display = 'none';

    // Show error
    if (data.error) {
        const errorDiv = document.getElementById('error-msg');
        errorDiv.style.display = 'block';
        errorDiv.innerText = '⚠️ ' + data.error;
        return;
    }

    // Show result card
    const resultCard = document.getElementById('result-card');
    resultCard.style.display = 'block';

    const resultLabel = document.getElementById('result-label');

    if (data.prediction === 'FAKE') {
        resultCard.className = 'result-card result-fake';
        resultLabel.innerHTML = '❌ FAKE NEWS DETECTED';
        resultLabel.className = 'result-label fake-label';
    } else if (data.prediction === 'SUSPICIOUS') {
        resultCard.className = 'result-card result-suspicious';
        resultLabel.innerHTML = '⚠️ SUSPICIOUS NEWS';
        resultLabel.className = 'result-label suspicious-label';
    } else {
        resultCard.className = 'result-card result-real';
        resultLabel.innerHTML = '✅ REAL NEWS';
        resultLabel.className = 'result-label real-label';
    }

    // ML verdict badge
    document.getElementById('ml-verdict').innerText = data.prediction;

    // Extracted text
    document.getElementById('extracted-text').innerText = data.extracted_text;

    // Keywords
    let keywordsHtml = '';
    data.fake_keywords.forEach(w => {
        keywordsHtml += `<span class="keyword-fake">🔴 ${w}</span>`;
    });
    data.real_keywords.forEach(w => {
        keywordsHtml += `<span class="keyword-real">🟢 ${w}</span>`;
    });
    if (keywordsHtml === '') {
        keywordsHtml = '<span style="color:#555;font-size:13px">No specific keywords found</span>';
    }
    document.getElementById('keywords-display').innerHTML = keywordsHtml;

    // TYPING EFFECT
    function typeText() {
    const text = 'FakeSnap';
    const el = document.getElementById('typed-text');
    let i = 0;
    const timer = setInterval(() => {
        el.innerText += text[i];
        i++;
        if (i >= text.length) clearInterval(timer);
    }, 150);
}
    typeText();

    // Graph — only on conflict
    if (data.show_graph) {
        document.getElementById('graph-section').style.display = 'block';
        document.getElementById('fake-percent').innerText = data.graph_fake + '%';
        document.getElementById('real-percent').innerText = data.graph_real + '%';
        document.getElementById('reason-box').innerText = '🔍 ' + data.reason;

        setTimeout(() => {
            document.getElementById('fake-bar').style.width = data.graph_fake + '%';
            document.getElementById('real-bar').style.width = data.graph_real + '%';
        }, 300);
    } else {
        document.getElementById('graph-section').style.display = 'none';
    }

    // Reload stats
    loadStats();
}

// Load stats on page load
loadStats();
// Accordion
function toggleAccordion(header) {
    const body = header.nextElementSibling;
    const icon = header.querySelector('.accordion-icon');
    const isOpen = body.style.display === 'block';
    
    // Close all
    document.querySelectorAll('.accordion-body').forEach(b => b.style.display = 'none');
    document.querySelectorAll('.accordion-icon').forEach(i => i.textContent = '+');
    
    // Open clicked
    if (!isOpen) {
        body.style.display = 'block';
        icon.textContent = '−';
    }
}

// Contact form
function sendContact() {
    const name = document.getElementById('contact-name').value;
    const email = document.getElementById('contact-email').value;
    const message = document.getElementById('contact-message').value;
    const status = document.getElementById('contact-status');

    if (!name || !email || !message) {
        status.style.color = '#f87171';
        status.textContent = '⚠️ Please fill all fields!';
        return;
    }

    status.style.color = '#4ade80';
    status.textContent = '✅ Message sent successfully! We will get back to you soon.';

    document.getElementById('contact-name').value = '';
    document.getElementById('contact-email').value = '';
    document.getElementById('contact-message').value = '';
}
// Dynamic greeting
function setGreeting() {
    const hour = new Date().getHours();
    const greetingEl = document.getElementById('greeting-text');
    if (!greetingEl) return;
    if (hour < 12) greetingEl.textContent = 'Good Morning,';
    else if (hour < 17) greetingEl.textContent = 'Good Afternoon,';
    else greetingEl.textContent = 'Good Evening,';
}
setGreeting();
