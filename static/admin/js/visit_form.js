/**
 * Visit Form JavaScript - City-Center-Doctor Filtering
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
        centerSelect.innerHTML = '<option value="">اختر المستشفى</option>';
        
        if (!selectedCityId) {
            // Clear doctors when no city is selected
            filterDoctors();
            return;
        }
        
        // Make AJAX request to get centers for the selected city
        $.ajax({
            url: '/api/v1/patients/admin/get-centers-by-city/',
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
                        option.textContent = center.name;
                        centerSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'لا توجد مستشفيات في هذه المدينة';
                    centerSelect.appendChild(option);
                }
            },
            error: function() {
                console.error('Error loading centers');
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'خطأ في تحميل المستشفيات';
                centerSelect.appendChild(option);
            }
        });
    }
    
    // Function to filter doctors based on selected center
    function filterDoctors() {
        const centerSelect = document.getElementById('id_center');
        const doctorSelect = document.getElementById('id_doctor');
        
        if (!centerSelect || !doctorSelect) return;
        
        const selectedCenterId = centerSelect.value;
        
        // Clear doctor options
        doctorSelect.innerHTML = '<option value="">اختر الطبيب</option>';
        
        if (!selectedCenterId) {
            return;
        }
        
        // Make AJAX request to get doctors for the selected center
        $.ajax({
            url: '/api/v1/patients/admin/get-doctors-by-center/',
            type: 'GET',
            data: {
                'center_id': selectedCenterId
            },
            success: function(data) {
                // Add doctors to the dropdown
                if (data.doctors && data.doctors.length > 0) {
                    data.doctors.forEach(function(doctor) {
                        const option = document.createElement('option');
                        option.value = doctor.id;
                        option.textContent = doctor.name + ' - ' + doctor.specialization;
                        doctorSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'لا يوجد أطباء في هذا المستشفى';
                    doctorSelect.appendChild(option);
                }
            },
            error: function() {
                console.error('Error loading doctors');
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'خطأ في تحميل الأطباء';
                doctorSelect.appendChild(option);
            }
        });
    }
    
    // Make functions available globally
    window.filterCenters = filterCenters;
    window.filterDoctors = filterDoctors;
    
    // Initialize when document is ready
    $(document).ready(function() {
        // Add event listeners
        $('#id_city').on('change', function() {
            filterCenters();
        });
        
        $('#id_center').on('change', function() {
            filterDoctors();
        });
        
        // If city is already selected, filter centers
        if ($('#id_city').val()) {
            filterCenters();
        }
        
        // If center is already selected, filter doctors
        if ($('#id_center').val()) {
            filterDoctors();
        }
    });

})(window.jQuery || window.django?.jQuery || jQuery);
