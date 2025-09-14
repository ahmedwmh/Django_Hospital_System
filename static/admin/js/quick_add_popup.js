/**
 * Universal Quick Add Popup System for Django Admin
 * Adds quick add buttons to all select boxes
 */

(function($) {
    'use strict';

    // Configuration for different model types
    const QUICK_ADD_CONFIG = {
        'id_user': {
            title: 'إضافة مستخدم جديد',
            url: '/admin/accounts/user/add/',
            fields: ['first_name', 'last_name', 'email', 'role'],
            successMessage: 'تم إنشاء المستخدم بنجاح'
        },
        'id_center': {
            title: 'إضافة مركز جديد',
            url: '/admin/hospital/center/add/',
            fields: ['name', 'city', 'address', 'phone_number'],
            successMessage: 'تم إنشاء المركز بنجاح'
        },
        'id_city': {
            title: 'إضافة مدينة جديدة',
            url: '/admin/hospital/city/add/',
            fields: ['name', 'state', 'country'],
            successMessage: 'تم إنشاء المدينة بنجاح'
        },
        'id_doctor': {
            title: 'إضافة طبيب جديد',
            url: '/admin/hospital/doctor/add/',
            fields: ['user', 'center', 'specialization'],
            successMessage: 'تم إنشاء الطبيب بنجاح'
        },
        'id_medicine': {
            title: 'إضافة دواء جديد',
            url: '/admin/hospital/medicine/add/',
            fields: ['name', 'generic_name', 'dosage_form', 'strength'],
            successMessage: 'تم إنشاء الدواء بنجاح'
        },
        'id_disease': {
            title: 'إضافة مرض جديد',
            url: '/admin/hospital/disease/add/',
            fields: ['name', 'category', 'description'],
            successMessage: 'تم إنشاء المرض بنجاح'
        },
        'id_patient': {
            title: 'إضافة مريض جديد',
            url: '/admin/patients/patient/add/',
            fields: ['first_name', 'last_name', 'phone_number', 'date_of_birth'],
            successMessage: 'تم إنشاء المريض بنجاح'
        },
        'id_visit': {
            title: 'إضافة زيارة جديدة',
            url: '/admin/patients/visit/add/',
            fields: ['patient', 'doctor', 'visit_type', 'visit_date', 'chief_complaint'],
            successMessage: 'تم إنشاء الزيارة بنجاح'
        }
    };

    // Create quick add popup
    function createQuickAddPopup(selectElement) {
        const fieldId = selectElement.attr('id');
        const config = QUICK_ADD_CONFIG[fieldId];
        
        if (!config) return;

        // Create popup HTML
        const popupHtml = `
            <div id="quick-add-popup" class="quick-add-popup" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <div class="popup-content" style="
                    background: white;
                    border-radius: 12px;
                    padding: 30px;
                    max-width: 500px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
                ">
                    <div class="popup-header" style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 20px;
                        padding-bottom: 15px;
                        border-bottom: 2px solid #e5e7eb;
                    ">
                        <h3 style="margin: 0; color: #1f2937; font-size: 1.25rem; font-weight: 700;">
                            ${config.title}
                        </h3>
                        <button id="close-popup" style="
                            background: none;
                            border: none;
                            font-size: 24px;
                            cursor: pointer;
                            color: #6b7280;
                            padding: 5px;
                        ">×</button>
                    </div>
                    <div class="popup-body">
                        <iframe id="quick-add-iframe" 
                                src="${config.url}?popup=1" 
                                style="
                                    width: 100%;
                                    height: 400px;
                                    border: none;
                                    border-radius: 8px;
                                ">
                        </iframe>
                    </div>
                    <div class="popup-footer" style="
                        margin-top: 20px;
                        padding-top: 15px;
                        border-top: 1px solid #e5e7eb;
                        text-align: center;
                    ">
                        <button id="cancel-popup" style="
                            background: #6b7280;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 6px;
                            cursor: pointer;
                            margin-right: 10px;
                        ">إلغاء</button>
                    </div>
                </div>
            </div>
        `;

        // Add popup to page
        $('body').append(popupHtml);

        // Handle popup events
        $('#close-popup, #cancel-popup').on('click', function() {
            $('#quick-add-popup').remove();
        });

        // Handle iframe load
        $('#quick-add-iframe').on('load', function() {
            const iframe = this;
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            
            // Listen for form submission in iframe
            $(iframeDoc).on('submit', 'form', function(e) {
                setTimeout(function() {
                    // Check if form was successful
                    if (iframeDoc.querySelector('.success') || 
                        iframeDoc.querySelector('.alert-success') ||
                        iframeDoc.URL.includes('changelist')) {
                        
                        // Refresh the select options
                        refreshSelectOptions(selectElement);
                        
                        // Show success message
                        showSuccessMessage(config.successMessage);
                        
                        // Close popup
                        $('#quick-add-popup').remove();
                    }
                }, 1000);
            });
        });
    }

    // Refresh select options
    function refreshSelectOptions(selectElement) {
        const fieldName = selectElement.attr('name');
        const currentValue = selectElement.val();
        
        // Make AJAX request to get updated options
        $.ajax({
            url: window.location.href,
            type: 'GET',
            success: function(data) {
                const newSelect = $(data).find(`select[name="${fieldName}"]`);
                if (newSelect.length) {
                    selectElement.html(newSelect.html());
                    selectElement.val(currentValue);
                }
            }
        });
    }

    // Show success message
    function showSuccessMessage(message) {
        const messageHtml = `
            <div id="success-message" style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: #10b981;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                z-index: 10001;
                font-weight: 600;
            ">
                ✅ ${message}
            </div>
        `;
        
        $('body').append(messageHtml);
        
        setTimeout(function() {
            $('#success-message').fadeOut(500, function() {
                $(this).remove();
            });
        }, 3000);
    }

    // Add quick add buttons to select elements
    function addQuickAddButtons() {
        $('select').each(function() {
            const $select = $(this);
            const fieldId = $select.attr('id');
            
            // Skip if already has quick add button, RelatedFieldWidgetWrapper, or no config
            if ($select.next('.quick-add-btn').length || 
                $select.parent().find('.related-widget-wrapper').length ||
                !QUICK_ADD_CONFIG[fieldId]) {
                return;
            }
            
            // Create quick add button
            const quickAddBtn = $(`
                <button type="button" class="quick-add-btn" style="
                    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    margin-left: 8px;
                    font-size: 12px;
                    font-weight: 600;
                    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
                    transition: all 0.2s ease;
                " title="إضافة جديد">
                    ➕ إضافة
                </button>
            `);
            
            // Add hover effects
            quickAddBtn.hover(
                function() {
                    $(this).css({
                        'background': 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
                        'transform': 'translateY(-1px)',
                        'box-shadow': '0 4px 8px rgba(59, 130, 246, 0.4)'
                    });
                },
                function() {
                    $(this).css({
                        'background': 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                        'transform': 'translateY(0)',
                        'box-shadow': '0 2px 4px rgba(59, 130, 246, 0.3)'
                    });
                }
            );
            
            // Add click handler
            quickAddBtn.on('click', function(e) {
                e.preventDefault();
                createQuickAddPopup($select);
            });
            
            // Insert button after select
            $select.after(quickAddBtn);
        });
    }

    // Initialize when document is ready
    $(document).ready(function() {
        // Add quick add buttons
        addQuickAddButtons();
        
        // Re-add buttons when new content is loaded
        $(document).on('DOMNodeInserted', function() {
            setTimeout(addQuickAddButtons, 100);
        });
    });

})(window.jQuery || window.django?.jQuery || window.$);
