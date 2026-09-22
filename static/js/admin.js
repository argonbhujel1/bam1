document.addEventListener('DOMContentLoaded', () => {
  // Live color inputs
  document.querySelectorAll('input[type="color"]').forEach(input => {
    input.addEventListener('input', () => {
      const preview = document.getElementById('theme-preview');
      if (preview) {
        const name = input.name.replace(/_/g, '-');
        preview.style.setProperty('--' + name, input.value);
      }
    });
  });

  // Image upload → fill URL field + preview
  const csrf = document.querySelector('input[name="csrf_token"]')
    || { value: (document.querySelector('meta[name="csrf-token"]') || {}).content };
  document.querySelectorAll('.js-upload').forEach(input => {
    input.addEventListener('change', async () => {
      const file = input.files && input.files[0];
      if (!file) return;
      const targetId = input.getAttribute('data-target');
      const previewId = input.getAttribute('data-preview');
      const target = targetId ? document.getElementById(targetId) : null;
      const preview = previewId ? document.getElementById(previewId) : null;
      const fd = new FormData();
      fd.append('file', file);
      fd.append('folder', input.getAttribute('data-folder') || 'bam-studio');
      if (csrf) fd.append('csrf_token', csrf.value);
      try {
        input.disabled = true;
        const res = await fetch('/admin/upload', { method: 'POST', body: fd, credentials: 'same-origin' });
        const data = await res.json();
        if (data.url) {
          if (target) target.value = data.url;
          if (preview) {
            preview.src = data.url;
            preview.style.display = 'block';
          }
        } else {
          alert(data.error || 'Upload failed');
        }
      } catch (e) {
        alert('Upload error: ' + e.message);
      } finally {
        input.disabled = false;
      }
    });
  });
});
