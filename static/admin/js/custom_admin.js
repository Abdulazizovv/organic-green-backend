// Custom Admin JavaScript for Product Management

(function($) {
    $(document).ready(function() {
        
        // Add CSS classes based on product status
        function styleProductRows() {
            $('.field-status_display').each(function() {
                var $row = $(this).closest('tr');
                var statusText = $(this).text().trim();
                
                if (statusText.includes('O\'chirilgan')) {
                    $row.addClass('deleted');
                } else if (statusText.includes('Nofaol')) {
                    $row.addClass('inactive');
                }
            });
            
            // Style featured products
            $('.field-is_featured input:checked').each(function() {
                $(this).closest('tr').addClass('featured');
            });
            
            // Style low stock products
            $('.field-stock_status').each(function() {
                var $row = $(this).closest('tr');
                var stockText = $(this).text().trim();
                
                if (stockText.includes('Tugagan')) {
                    $row.addClass('out-of-stock');
                } else if (stockText.includes('Kam qoldi')) {
                    $row.addClass('low-stock');
                }
            });
        }
        
        // Price calculation and validation
        function setupPriceCalculation() {
            var $priceField = $('#id_price');
            var $salePriceField = $('#id_sale_price');
            var $finalPriceField = $('.field-final_price .readonly');
            
            function calculateFinalPrice() {
                var price = parseFloat($priceField.val()) || 0;
                var salePrice = parseFloat($salePriceField.val()) || 0;
                var finalPrice = salePrice > 0 && salePrice < price ? salePrice : price;
                
                if ($finalPriceField.length) {
                    $finalPriceField.text(finalPrice.toFixed(2) + ' so\'m');
                }
                
                // Validate sale price
                if (salePrice > 0 && salePrice >= price) {
                    $salePriceField.css('border-color', '#dc3545');
                    showNotification('Chegirmali narx asosiy narxdan kichik bo\'lishi kerak!', 'error');
                } else {
                    $salePriceField.css('border-color', '#28a745');
                }
            }
            
            $priceField.on('input', calculateFinalPrice);
            $salePriceField.on('input', calculateFinalPrice);
            
            // Initial calculation
            calculateFinalPrice();
        }
        
        // Stock level warnings
        function setupStockWarnings() {
            var $stockField = $('#id_stock');
            
            $stockField.on('input', function() {
                var stock = parseInt($(this).val()) || 0;
                var $warning = $('#stock-warning');
                
                // Remove existing warning
                $warning.remove();
                
                if (stock === 0) {
                    $(this).after('<div id="stock-warning" class="bulk-action-warning">Diqqat: Mahsulot zaxirasi tugagan!</div>');
                } else if (stock <= 10) {
                    $(this).after('<div id="stock-warning" class="bulk-action-warning">Ogohlantirish: Kam zaxira (' + stock + ' ta qoldi)</div>');
                }
            });
        }
        
        // Auto-generate slug from Uzbek name
        function setupSlugGeneration() {
            var $nameUzField = $('#id_name_uz');
            var $slugField = $('#id_slug');
            
            if ($slugField.val() === '') {
                $nameUzField.on('input', function() {
                    var name = $(this).val();
                    var slug = name.toLowerCase()
                        .replace(/[^a-zA-Z0-9\s]/g, '')
                        .replace(/\s+/g, '-')
                        .replace(/-+/g, '-')
                        .trim('-');
                    $slugField.val(slug);
                });
            }
        }
        
        // Enhanced search functionality
        function setupEnhancedSearch() {
            var $searchInput = $('#searchbar');
            
            if ($searchInput.length) {
                $searchInput.attr('placeholder', 'Mahsulot nomi, kategoriya yoki tavsif bo\'yicha qidiring...');
                
                // Add search suggestions (if needed in future)
                $searchInput.on('input', function() {
                    var query = $(this).val();
                    if (query.length > 2) {
                        // Future: implement search suggestions
                    }
                });
            }
        }
        
        // Confirmation for bulk actions
        function setupBulkActionConfirmation() {
            $('button[name="index"]').on('click', function(e) {
                var action = $('select[name="action"]').val();
                var selectedCount = $('input[name="_selected_action"]:checked').length;
                
                if (selectedCount === 0) {
                    e.preventDefault();
                    showNotification('Iltimos, kamida bitta mahsulotni tanlang!', 'error');
                    return false;
                }
                
                var confirmActions = [
                    'soft_delete_products',
                    'make_inactive',
                    'remove_featured'
                ];
                
                if (confirmActions.includes(action)) {
                    var actionText = {
                        'soft_delete_products': 'o\'chirish',
                        'make_inactive': 'nofaol qilish',
                        'remove_featured': 'tavsiya etilgan holatini olib tashlash'
                    };
                    
                    if (!confirm(selectedCount + ' ta mahsulotni ' + actionText[action] + ' xohlaysizmi?')) {
                        e.preventDefault();
                        return false;
                    }
                }
            });
        }
        
        // Notification system
        function showNotification(message, type) {
            var $notification = $('<div class="bulk-action-' + (type === 'error' ? 'warning' : 'success') + '">' + message + '</div>');
            $('.breadcrumbs').after($notification);
            
            setTimeout(function() {
                $notification.fadeOut(function() {
                    $(this).remove();
                });
            }, 5000);
        }
        
        // Category and tag management
        function setupCategoryTagManagement() {
            // Add visual indicators for categories and tags
            $('.field-category select option').each(function() {
                if ($(this).val()) {
                    $(this).text('📁 ' + $(this).text());
                }
            });
            
            // Enhanced tag selection
            if ($('#id_tags').length) {
                $('#id_tags option').each(function() {
                    if ($(this).val()) {
                        $(this).text('🏷️ ' + $(this).text());
                    }
                });
            }
        }
        
        // Initialize all enhancements
        styleProductRows();
        setupPriceCalculation();
        setupStockWarnings();
        setupSlugGeneration();
        setupEnhancedSearch();
        setupBulkActionConfirmation();
        setupCategoryTagManagement();
        
        // Add custom CSS class to body for styling
        $('body').addClass('enhanced-product-admin');
        
        // Refresh enhancements when using AJAX (for inline editing)
        $(document).ajaxComplete(function() {
            styleProductRows();
        });
        
        // Keyboard shortcuts
        $(document).keydown(function(e) {
            // Ctrl+S to save (if in edit mode)
            if (e.ctrlKey && e.which === 83) {
                if ($('.submit-row').length) {
                    e.preventDefault();
                    $('.default').click();
                }
            }
            
            // Escape to cancel/go back
            if (e.which === 27) {
                if ($('.cancel-link').length) {
                    window.location.href = $('.cancel-link').attr('href');
                }
            }
        });
        
        console.log('✅ Product Admin enhancements loaded successfully!');
    });
})(django.jQuery);

// ===== COURSE ADMIN JAVASCRIPT =====

// Course Admin Enhanced Functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Add course-specific classes to admin pages
    if (window.location.pathname.includes('/course/')) {
        document.body.classList.add('course-admin');
        
        if (window.location.pathname.includes('/course/course/')) {
            document.body.classList.add('course-changelist');
            document.querySelector('.results')?.classList.add('course-changelist');
        }
        
        if (window.location.pathname.includes('/courseapplication/')) {
            document.body.classList.add('application-changelist');
        }
    }
    
    // Enhanced status update functionality
    window.updateApplicationStatus = function(applicationId, status) {
        if (confirm(`Are you sure you want to ${status} this application?`)) {
            // This would typically make an AJAX call to update status
            console.log(`Updating application ${applicationId} to ${status}`);
            // For now, just show a success message
            alert(`Application ${status} successfully!`);
            location.reload();
        }
    };
    
    // Quick contact functionality
    window.quickContact = function(type, value) {
        if (type === 'phone') {
            window.open(`tel:${value}`);
        } else if (type === 'email') {
            window.open(`mailto:${value}`);
        }
    };
    
    // Enhanced search functionality
    const searchInput = document.querySelector('#searchbar');
    if (searchInput && document.body.classList.contains('course-admin')) {
        searchInput.placeholder = 'Search courses, applications, names, phones...';
        
        // Add search suggestions
        const searchSuggestions = [
            'course:python', 'status:pending', 'level:beginner', 
            'format:online', 'city:tashkent', 'approved today'
        ];
        
        searchInput.addEventListener('focus', function() {
            if (!this.value) {
                this.placeholder = 'Try: ' + searchSuggestions[Math.floor(Math.random() * searchSuggestions.length)];
            }
        });
    }
    
    // Auto-refresh for pending applications (every 30 seconds)
    if (window.location.pathname.includes('/courseapplication/') && 
        document.querySelector('.status-pending')) {
        setInterval(function() {
            if (document.hidden) return; // Don't refresh if tab is not active
            
            const url = new URL(window.location);
            url.searchParams.set('app_status', 'pending');
            
            fetch(url.toString())
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newResults = doc.querySelector('.results tbody');
                    const currentResults = document.querySelector('.results tbody');
                    
                    if (newResults && currentResults && 
                        newResults.innerHTML !== currentResults.innerHTML) {
                        // Flash notification for new applications
                        showNotification('New applications received!', 'info');
                    }
                })
                .catch(error => console.log('Auto-refresh failed:', error));
        }, 30000);
    }
    
    // Course capacity warnings
    document.querySelectorAll('.course-metric-card').forEach(card => {
        const applicationsCount = parseInt(card.querySelector('h3')?.textContent || '0');
        if (applicationsCount > 50) {
            card.style.background = 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)';
            card.title = 'High demand course!';
        }
    });
    
    // Application timeline animations
    document.querySelectorAll('.application-timeline').forEach(timeline => {
        const items = timeline.querySelectorAll('.timeline-item');
        items.forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.classList.add('timeline-animate');
        });
    });
    
    // Enhanced tooltips for action buttons
    document.querySelectorAll('.course-action-btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'course-tooltip';
            tooltip.textContent = this.title || this.textContent;
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - 30) + 'px';
            
            setTimeout(() => tooltip.style.opacity = '1', 10);
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });
    
    // Keyboard shortcuts for course admin
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'n': // Ctrl+N - New course
                    if (document.body.classList.contains('course-changelist')) {
                        e.preventDefault();
                        window.location.href = './add/';
                    }
                    break;
                case 'f': // Ctrl+F - Focus search
                    if (document.body.classList.contains('course-admin')) {
                        e.preventDefault();
                        document.querySelector('#searchbar')?.focus();
                    }
                    break;
                case 'r': // Ctrl+R - Refresh with notification
                    if (document.body.classList.contains('course-admin')) {
                        showNotification('Refreshing data...', 'info');
                    }
                    break;
            }
        }
    });
    
    // Notification system
    window.showNotification = function(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `course-notification course-notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };
    
    // Course analytics real-time updates
    if (window.location.pathname.includes('/admin/course/course/analytics/')) {
        setInterval(updateAnalytics, 60000); // Update every minute
    }
    
    function updateAnalytics() {
        fetch('/api/course/admin/statistics/')
            .then(response => response.json())
            .then(data => {
                // Update analytics numbers
                document.querySelectorAll('.course-analytics-number').forEach(elem => {
                    const metric = elem.dataset.metric;
                    if (data[metric] !== undefined) {
                        animateNumber(elem, parseInt(elem.textContent), data[metric]);
                    }
                });
            })
            .catch(error => console.log('Analytics update failed:', error));
    }
    
    function animateNumber(element, from, to) {
        const duration = 1000;
        const start = Date.now();
        
        function update() {
            const progress = (Date.now() - start) / duration;
            if (progress < 1) {
                const current = Math.floor(from + (to - from) * progress);
                element.textContent = current.toLocaleString();
                requestAnimationFrame(update);
            } else {
                element.textContent = to.toLocaleString();
            }
        }
        
        requestAnimationFrame(update);
    }
    
    // Initialize course admin enhancements
    initializeCourseEnhancements();
});

function initializeCourseEnhancements() {
    // Add loading states to action buttons
    document.querySelectorAll('.course-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (!this.classList.contains('course-btn-loading')) {
                this.classList.add('course-btn-loading');
                this.style.opacity = '0.7';
                this.style.pointerEvents = 'none';
                
                setTimeout(() => {
                    this.classList.remove('course-btn-loading');
                    this.style.opacity = '';
                    this.style.pointerEvents = '';
                }, 2000);
            }
        });
    });
    
    // Auto-save draft functionality for course forms
    const courseForm = document.querySelector('form.course-form');
    if (courseForm) {
        const inputs = courseForm.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                const draftKey = `course_draft_${window.location.pathname}`;
                const formData = new FormData(courseForm);
                const draftData = Object.fromEntries(formData.entries());
                localStorage.setItem(draftKey, JSON.stringify(draftData));
                
                showNotification('Draft saved automatically', 'info');
            });
        });
    }
    
    console.log('Course admin enhancements initialized successfully!');
}
