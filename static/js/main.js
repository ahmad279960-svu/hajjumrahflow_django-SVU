// static/js/main.js

document.addEventListener("DOMContentLoaded", function() {
    // --- Chart.js for Manager Dashboard with Brand Colors ---
    const occupancyChartEl = document.getElementById('occupancyChart');
    if (occupancyChartEl) {
        // In a real implementation, this data would be fetched or embedded in the template.
        const tripLabels = ['Umrah Rajab', 'Umrah Shaban', 'Hajj 2026', 'Quick Umrah', 'Ramadan Special'];
        const tripOccupancy = [85, 60, 95, 40, 78];

        new Chart(occupancyChartEl, {
            type: 'bar',
            data: {
                labels: tripLabels,
                datasets: [{
                    label: '% Occupancy',
                    data: tripOccupancy,
                    backgroundColor: 'rgba(10, 35, 66, 0.8)',   // var(--primary-deep-blue)
                    borderColor: 'rgba(212, 175, 55, 1)',     // var(--accent-gold)
                    borderWidth: 1,
                    borderRadius: 5,
                    hoverBackgroundColor: 'rgba(212, 175, 55, 0.8)' // Gold on hover
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) { return value + "%" }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // --- Sidebar Toggle for Mobile (if needed) ---
    // Can be added here if a mobile-first responsive layout is required.
});