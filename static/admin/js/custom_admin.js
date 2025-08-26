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
