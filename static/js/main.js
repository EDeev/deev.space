/**
 * deev.space - Main JavaScript
 * @author Егор Деев
 */

(function() {
    'use strict';

    // ===== DOM Ready =====
    document.addEventListener('DOMContentLoaded', function() {
        initAOS();
        initNavigation();
        initBackToTop();
        initMessages();
        initContactForm();
        initCodeBlocks();
        addHeaderAnchors();
    });

    // ===== AOS Animation =====
    function initAOS() {
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 600,
                easing: 'ease-out-cubic',
                once: true,
                offset: 50,
                delay: 0
            });
        }
    }

    // ===== Navigation =====
    function initNavigation() {
        const navbar = document.getElementById('navbar');
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');

        // Mobile menu toggle
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', function() {
                const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
                navToggle.setAttribute('aria-expanded', !isExpanded);
                navToggle.classList.toggle('active');
                navMenu.classList.toggle('active');
                document.body.classList.toggle('nav-open');
            });

            // Close menu on link click
            navMenu.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', () => {
                    navToggle.setAttribute('aria-expanded', 'false');
                    navToggle.classList.remove('active');
                    navMenu.classList.remove('active');
                    document.body.classList.remove('nav-open');
                });
            });

            // Close menu on outside click
            document.addEventListener('click', function(e) {
                if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                    navToggle.setAttribute('aria-expanded', 'false');
                    navToggle.classList.remove('active');
                    navMenu.classList.remove('active');
                    document.body.classList.remove('nav-open');
                }
            });
        }

        // Navbar scroll effect
        let lastScroll = 0;
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;

            if (currentScroll > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            // Hide/show on scroll
            if (currentScroll > lastScroll && currentScroll > 200) {
                navbar.classList.add('hidden');
            } else {
                navbar.classList.remove('hidden');
            }

            lastScroll = currentScroll;
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    const headerOffset = 100;
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ===== Back to Top Button =====
    function initBackToTop() {
        const backToTop = document.getElementById('backToTop');
        if (!backToTop) return;

        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 500) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });

        backToTop.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ===== Messages =====
    function initMessages() {
        const messagesContainer = document.getElementById('messagesContainer');
        if (!messagesContainer) return;

        messagesContainer.querySelectorAll('.message').forEach(message => {
            // Auto hide after 5 seconds
            setTimeout(() => {
                hideMessage(message);
            }, 5000);

            // Close button
            const closeBtn = message.querySelector('.message-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => hideMessage(message));
            }
        });
    }

    function hideMessage(message) {
        message.classList.add('hiding');
        setTimeout(() => message.remove(), 300);
    }

    // ===== Contact Form =====
    function initContactForm() {
        const contactForm = document.getElementById('contact-form');
        if (!contactForm) return;

        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const submitBtn = this.querySelector('button[type="submit"]');
            const originalContent = submitBtn.innerHTML;

            // Disable button and show loading
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';

            try {
                const formData = new FormData(this);
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();

                if (data.success) {
                    contactForm.reset();
                    showNotification(data.message || 'Сообщение успешно отправлено!', 'success');

                    // Reset reCAPTCHA if exists
                    if (typeof grecaptcha !== 'undefined') {
                        grecaptcha.reset();
                    }
                } else {
                    const errorMsg = data.errors ? Object.values(data.errors).flat().join(', ') : 'Ошибка при отправке';
                    showNotification(errorMsg, 'error');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                showNotification('Произошла ошибка. Попробуйте позже.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalContent;
            }
        });
    }

    // ===== CSRF Token =====
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // ===== Notifications =====
    window.showNotification = function(message, type = 'info') {
        const container = document.getElementById('messagesContainer') || createNotificationContainer();

        const notification = document.createElement('div');
        notification.className = `message message-${type}`;
        notification.innerHTML = `
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button type="button" class="message-close" aria-label="Закрыть">&times;</button>
        `;

        container.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 10);

        // Close button
        notification.querySelector('.message-close').addEventListener('click', () => {
            hideMessage(notification);
        });

        // Auto hide
        setTimeout(() => hideMessage(notification), 5000);
    };

    function createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'messagesContainer';
        container.className = 'messages-container';
        document.body.appendChild(container);
        return container;
    }

    function getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    // ===== Article Like/Dislike =====
    window.toggleArticleLike = async function(articleId, isLike) {
        try {
            const response = await fetch(`/api/article/${articleId}/like/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ is_like: isLike })
            });

            if (!response.ok) {
                if (response.status === 403) {
                    showNotification('Войдите, чтобы оценить статью', 'warning');
                    return;
                }
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            if (data.success) {
                updateVoteButtons(`article-${articleId}`, data);
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Ошибка при оценке статьи', 'error');
        }
    };

    // ===== Comment Like/Dislike =====
    window.toggleCommentLike = async function(commentId, isLike) {
        try {
            const response = await fetch(`/api/comment/${commentId}/like/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ is_like: isLike })
            });

            if (!response.ok) {
                if (response.status === 403) {
                    showNotification('Войдите, чтобы оценить комментарий', 'warning');
                    return;
                }
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            if (data.success) {
                updateVoteButtons(`comment-${commentId}`, data);
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Ошибка при оценке комментария', 'error');
        }
    };

    function updateVoteButtons(prefix, data) {
        const likesEl = document.getElementById(`${prefix}-likes`);
        const dislikesEl = document.getElementById(`${prefix}-dislikes`);
        const likeBtn = document.getElementById(`${prefix}-like-btn`);
        const dislikeBtn = document.getElementById(`${prefix}-dislike-btn`);

        if (likesEl) likesEl.textContent = data.likes;
        if (dislikesEl) dislikesEl.textContent = data.dislikes;

        if (likeBtn && dislikeBtn) {
            likeBtn.classList.remove('active');
            dislikeBtn.classList.remove('active');

            // Update icons
            const likeIcon = likeBtn.querySelector('i');
            const dislikeIcon = dislikeBtn.querySelector('i');

            if (likeIcon) {
                likeIcon.className = data.user_vote === true ? 'fas fa-thumbs-up' : 'far fa-thumbs-up';
            }
            if (dislikeIcon) {
                dislikeIcon.className = data.user_vote === false ? 'fas fa-thumbs-down' : 'far fa-thumbs-down';
            }

            if (data.user_vote === true) {
                likeBtn.classList.add('active');
            } else if (data.user_vote === false) {
                dislikeBtn.classList.add('active');
            }
        }
    }

    // ===== Comments =====
    window.submitComment = async function(articleId, parentId = null) {
        const form = parentId
            ? document.getElementById(`reply-form-${parentId}`)
            : document.getElementById('comment-form');

        if (!form) return;

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalContent = submitBtn.innerHTML;
        const textarea = form.querySelector('textarea');
        const content = textarea.value.trim();

        if (!content) {
            showNotification('Введите текст комментария', 'warning');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            const formData = new FormData(form);
            if (parentId) {
                formData.append('parent_id', parentId);
            }

            const response = await fetch(`/api/article/${articleId}/comment/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                showNotification('Комментарий добавлен!', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                const errorMsg = data.errors ? Object.values(data.errors).flat().join(', ') : 'Ошибка';
                showNotification(errorMsg, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Ошибка при добавлении комментария', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalContent;
        }
    };

    window.showReplyForm = function(commentId) {
        // Hide all reply forms first
        document.querySelectorAll('.reply-form-container').forEach(form => {
            form.style.display = 'none';
        });

        // Show the specific reply form
        const replyForm = document.getElementById(`reply-form-container-${commentId}`);
        if (replyForm) {
            replyForm.style.display = 'block';
            const textarea = replyForm.querySelector('textarea');
            if (textarea) {
                textarea.focus();
            }
        }
    };

    window.hideReplyForm = function(commentId) {
        const replyForm = document.getElementById(`reply-form-container-${commentId}`);
        if (replyForm) {
            replyForm.style.display = 'none';
        }
    };

    // ===== Copy to Clipboard =====
    window.copyToClipboard = function(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.classList.add('copied');

            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.classList.remove('copied');
            }, 2000);

            showNotification('Скопировано!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            showNotification('Ошибка копирования', 'error');
        });
    };

    // ===== Code Copy Functionality =====
    function initCodeBlocks() {
        const codeBlocks = document.querySelectorAll('.article-body pre');
        
        codeBlocks.forEach((pre) => {
            // Проверяем, не добавлена ли уже кнопка
            if (pre.querySelector('.code-copy-btn')) {
                return;
            }
            
            const codeElement = pre.querySelector('code');
            if (!codeElement) return;
            
            // Создаём кнопку копирования
            const copyButton = document.createElement('button');
            copyButton.className = 'code-copy-btn';
            copyButton.type = 'button';
            copyButton.setAttribute('aria-label', 'Копировать код');
            copyButton.innerHTML = '<i class="fas fa-copy"></i><span class="copy-text">Копировать</span>';
            
            // Обработчик клика
            copyButton.addEventListener('click', async function(e) {
                e.preventDefault();
                
                // Получаем текст кода без HTML-тегов
                const codeText = codeElement.textContent || codeElement.innerText;
                
                try {
                    await navigator.clipboard.writeText(codeText);
                    
                    // Изменяем визуальное состояние кнопки
                    copyButton.innerHTML = '<i class="fas fa-check"></i><span class="copy-text">Сохранено!</span>';
                    copyButton.classList.add('copied');
                    
                    // Возвращаем исходное состояние через 2 секунды
                    setTimeout(() => {
                        copyButton.innerHTML = '<i class="fas fa-copy"></i><span class="copy-text">Копировать</span>';
                        copyButton.classList.remove('copied');
                    }, 2000);
                    
                } catch (err) {
                    console.error('Ошибка при копировании:', err);
                    
                    // Fallback для старых браузеров
                    const textArea = document.createElement('textarea');
                    textArea.value = codeText;
                    textArea.style.position = 'fixed';
                    textArea.style.left = '-999999px';
                    document.body.appendChild(textArea);
                    textArea.select();
                    
                    try {
                        document.execCommand('copy');
                        copyButton.innerHTML = '<i class="fas fa-check"></i><span class="copy-text">Сохранено!</span>';
                        copyButton.classList.add('copied');
                        
                        setTimeout(() => {
                            copyButton.innerHTML = '<i class="fas fa-copy"></i><span class="copy-text">Копировать</span>';
                            copyButton.classList.remove('copied');
                        }, 2000);
                    } catch (err2) {
                        showNotification('Не удалось скопировать код', 'error');
                    }
                    
                    document.body.removeChild(textArea);
                }
            });
            
            // Добавляем кнопку в блок кода
            pre.style.position = 'relative';
            pre.appendChild(copyButton);
        });
    }

    function addHeaderAnchors() {
        const headers = document.querySelectorAll('.article-body h2, .article-body h3');
        headers.forEach(header => {
            const id = header.textContent
                .toLowerCase()
                .replace(/[^a-zа-яё0-9]+/g, '-')
                .replace(/^-|-$/g, '');
            
            header.id = id;
            
            const anchor = document.createElement('a');
            anchor.className = 'header-anchor';
            anchor.href = `#${id}`;
            anchor.innerHTML = '<i class="fas fa-link"></i>';
            anchor.setAttribute('aria-label', 'Ссылка на раздел');
            
            header.appendChild(anchor);
        });
    }

})();