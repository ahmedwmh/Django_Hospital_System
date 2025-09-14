/**
 * Staff Form JavaScript - City-Center Filtering
 */

(function($) {
    'use strict';

    // Function to filter centers based on selected city
    function filterCenters() {
        const citySelect = document.getElementById('id_city');
        const centerSelect = document.getElementById('id_center');
        
        if (!citySelect || !centerSelect) return;
        
        const selectedCityId = citySelect.value;
        
        // Clear center options
        centerSelect.innerHTML = '<option value="">اختر المركز</option>';
        
        if (!selectedCityId) {
            return;
        }
        
        // Make AJAX request to get centers for the selected city
        $.ajax({
            url: '/api/v1/hospital/centers-by-city/',
            type: 'GET',
            data: {
                'city_id': selectedCityId
            },
            success: function(data) {
                // Add centers to the dropdown
                if (data.centers && data.centers.length > 0) {
                    data.centers.forEach(function(center) {
                        const option = document.createElement('option');
                        option.value = center.id;
                        option.textContent = center.name + ' - ' + center.city_name;
                        centerSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'لا توجد مراكز في هذه المدينة';
                    centerSelect.appendChild(option);
                }
            },
            error: function() {
                console.error('Error loading centers');
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'خطأ في تحميل المراكز';
                centerSelect.appendChild(option);
            }
        });
    }
    
    // Make filterCenters available globally
    window.filterCenters = filterCenters;
    
    // Initialize when document is ready
    $(document).ready(function() {
        // Add event listener to city select
        $('#id_city').on('change', filterCenters);
        
        // If city is already selected, filter centers
        if ($('#id_city').val()) {
            filterCenters();
        }
    });

})(django.jQuery || jQuery);
