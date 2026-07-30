(function () {
    const data = window.dashboardData || {};

    const chartColors = {
        low: '#16a34a',
        medium: '#d97706',
        high: '#dc2626',
        feature: '#4f46e5'
    };

    const donutCtx = document.getElementById('riskDonutChart');
    if (donutCtx) {
        new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'At Risk', 'High Risk'],
                datasets: [{
                    data: [data.lowRisk || 0, data.mediumRisk || 0, data.highRisk || 0],
                    backgroundColor: [chartColors.low, chartColors.medium, chartColors.high],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                cutout: '72%',
                plugins: { legend: { display: false } },
                maintainAspectRatio: false
            }
        });
    }

    const trendCtx = document.getElementById('riskTrendChart');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: data.trendMonths || [],
                datasets: [
                    {
                        label: 'Low Risk',
                        data: data.trendLow || [],
                        borderColor: chartColors.low,
                        backgroundColor: chartColors.low,
                        tension: 0.4,
                        pointRadius: 4
                    },
                    {
                        label: 'At Risk',
                        data: data.trendMedium || [],
                        borderColor: chartColors.medium,
                        backgroundColor: chartColors.medium,
                        tension: 0.4,
                        pointRadius: 4
                    },
                    {
                        label: 'High Risk',
                        data: data.trendHigh || [],
                        borderColor: chartColors.high,
                        backgroundColor: chartColors.high,
                        tension: 0.4,
                        pointRadius: 4
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { usePointStyle: true, boxWidth: 8 }
                    }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f0f1f5' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    const featureCtx = document.getElementById('featureImportanceChart');
    if (featureCtx) {
        new Chart(featureCtx, {
            type: 'bar',
            data: {
                labels: ['Attendance %', 'GPA', 'Assignments', 'Sem. Performance', 'Family Income'],
                datasets: [{
                    data: [0.32, 0.24, 0.18, 0.12, 0.06],
                    backgroundColor: chartColors.feature,
                    borderRadius: 6,
                    barThickness: 16
                }]
            },
            options: {
                indexAxis: 'y',
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: '#f0f1f5' } },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    const shareBtn = document.getElementById('shareReportBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            const url = window.location.href;
            if (navigator.share) {
                navigator.share({ title: 'EduPulse Dashboard Report', url });
            } else if (navigator.clipboard) {
                navigator.clipboard.writeText(url);
                shareBtn.querySelector('h4').textContent = 'Link Copied!';
                setTimeout(() => {
                    shareBtn.querySelector('h4').textContent = 'Share Report';
                }, 2000);
            }
        });
    }
})();
