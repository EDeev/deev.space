/* Стек в одну строку: что не влезает по ширине — прячется за «+N». */
(function () {
    function fit(box) {
        const tags = Array.from(box.querySelectorAll('.skill-tag'));
        const btn = box.querySelector('.skills-more-btn');
        tags.forEach(t => t.classList.remove('is-off'));
        if (box.classList.contains('is-open')) {
            btn.hidden = false;
            btn.textContent = 'свернуть';
            return;
        }
        btn.hidden = true;
        const gap = parseFloat(getComputedStyle(box).columnGap) || 0;
        const avail = box.clientWidth;
        const widths = tags.map(t => t.getBoundingClientRect().width);
        const total = widths.reduce((a, w) => a + w, 0) + gap * Math.max(tags.length - 1, 0);
        if (total <= avail + 0.5) return;

        btn.hidden = false;
        let used = 0, shown = 0;
        for (let i = 0; i < tags.length; i++) {
            btn.textContent = '+' + (tags.length - i - 1);
            const need = used + (i ? gap : 0) + widths[i] + gap + btn.getBoundingClientRect().width;
            if (need > avail + 0.5) break;
            used += (i ? gap : 0) + widths[i];
            shown = i + 1;
        }
        shown = Math.max(shown, 1);
        tags.forEach((t, i) => t.classList.toggle('is-off', i >= shown));
        btn.textContent = '+' + (tags.length - shown);
    }

    function init() {
        document.querySelectorAll('.skills-rows').forEach(root => {
            if (root.dataset.ready) return;
            root.dataset.ready = '1';
            const boxes = Array.from(root.querySelectorAll('.skills-row-tags'));
            const refit = () => boxes.forEach(fit);
            root.addEventListener('click', e => {
                const b = e.target.closest('.skills-more-btn');
                if (!b) return;
                b.parentElement.classList.toggle('is-open');
                fit(b.parentElement);
            });
            if ('ResizeObserver' in window) new ResizeObserver(refit).observe(root);
            else window.addEventListener('resize', refit);
            if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
            refit();
        });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
