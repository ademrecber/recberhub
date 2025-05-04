export function initSozlukForm() {
    const form = document.getElementById('sozluk-form');
    const errorDiv = document.getElementById('form-errors');
    if (!form || !errorDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const formData = new FormData(form);
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                form.reset();
                alert('Kelime başarıyla eklendi!');
            } else {
                errorDiv.classList.remove('d-none');
                for (const [field, message] of Object.entries(data.errors)) {
                    errorDiv.innerHTML += `<p>${message}</p>`;
                }
            }
        } catch (error) {
            console.error('Form gönderim hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.innerHTML = '<p>Bir hata oluştu, lütfen tekrar deneyin.</p>';
        }
    });
}

export function initSozlukLoader(harf) {
    let offset = 20;
    let hasMore = true;
    let loading = false;

    const kelimeList = document.getElementById('kelime-list');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error-message');

    const loadMoreKelimeler = async () => {
        if (loading || !hasMore) return;
        loading = true;
        loadingDiv.style.display = 'block';
        errorDiv.classList.add('d-none');

        try {
            const response = await fetch(`/sozluk/harf-yukle/?harf=${harf}&offset=${offset}`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);
            const data = await response.json();
            if (data.kelimeler && Array.isArray(data.kelimeler)) {
                const fragment = document.createDocumentFragment();
                data.kelimeler.forEach(kelime => {
                    const kelimeDiv = document.createElement('div');
                    kelimeDiv.className = 'kelime-item mb-2';
                    kelimeDiv.dataset.kelimeId = kelime.id;
                    kelimeDiv.innerHTML = `
                        <div class="d-flex justify-content-between align-items-start">
                            <a href="/sozluk/kelime/${kelime.id}/" class="text-decoration-none">
                                <strong>${kelime.kelime}</strong>
                                <p class="text-muted small">${kelime.detay}</p>
                            </a>
                            ${kelime.is_owner ? `
                                <div class="dropdown">
                                    <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li>
                                            <button class="dropdown-item text-danger delete-kelime-btn" data-kelime-id="${kelime.id}">Sil</button>
                                        </li>
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `;
                    fragment.appendChild(kelimeDiv);
                });
                kelimeList.appendChild(fragment);
                offset += 20;
                hasMore = data.has_more;

                // Silme butonlarına olay dinleyici ekle
                document.querySelectorAll('.delete-kelime-btn').forEach(btn => {
                    btn.addEventListener('click', async () => {
                        if (!confirm('Bu kelimeyi silmek istediğinizden emin misiniz?')) return;
                        try {
                            const response = await fetch(`/sozluk/kelime-sil/${btn.dataset.kelimeId}/`, {
                                method: 'POST',
                                headers: {
                                    'X-Requested-With': 'XMLHttpRequest',
                                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                                }
                            });
                            const data = await response.json();
                            if (data.success) {
                                document.querySelector(`.kelime-item[data-kelime-id="${btn.dataset.kelimeId}"]`).remove();
                                alert('Kelime başarıyla silindi!');
                            } else {
                                errorDiv.classList.remove('d-none');
                                errorDiv.textContent = data.error || 'Kelime silinirken hata oluştu.';
                            }
                        } catch (error) {
                            console.error('Silme hatası:', error);
                            errorDiv.classList.remove('d-none');
                            errorDiv.textContent = 'Bir hata oluştu, lütfen tekrar deneyin.';
                        }
                    });
                });
            } else {
                hasMore = false;
            }
        } catch (error) {
            console.error('Kelime yükleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.textContent = 'Kelimeler yüklenirken hata oluştu: ' + error.message;
        } finally {
            loading = false;
            loadingDiv.style.display = 'none';
        }
    };

    const scrollHandler = () => {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100 && !loading) {
            loadMoreKelimeler();
        }
    };
    window.addEventListener('scroll', scrollHandler);

    // İlk yüklemedeki silme butonları için olay dinleyici
    document.querySelectorAll('.delete-kelime-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Bu kelimeyi silmek istediğinizden emin misiniz?')) return;
            try {
                const response = await fetch(`/sozluk/kelime-sil/${btn.dataset.kelimeId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    }
                });
                const data = await response.json();
                if (data.success) {
                    document.querySelector(`.kelime-item[data-kelime-id="${btn.dataset.kelimeId}"]`).remove();
                    alert('Kelime başarıyla silindi!');
                } else {
                    errorDiv.classList.remove('d-none');
                    errorDiv.textContent = data.error || 'Kelime silinirken hata oluştu.';
                }
            } catch (error) {
                console.error('Silme hatası:', error);
                errorDiv.classList.remove('d-none');
                errorDiv.textContent = 'Bir hata oluştu, lütfen tekrar deneyin.';
            }
        });
    });
}