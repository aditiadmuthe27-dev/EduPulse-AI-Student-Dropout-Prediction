(function () {
    const data = window.dashboardData || {};

    const donutCtx = document.getElementById('riskDonutChart');
    if (donutCtx) {
        new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'At Risk', 'High Risk'],
                datasets: [{
                    data: [data.lowRisk || 0, data.mediumRisk || 0, data.highRisk || 0],
                    backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
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
                        borderColor: '#22c55e',
                        backgroundColor: '#22c55e',
                        tension: 0.4,
                        pointRadius: 4
                    },
                    {
                        label: 'At Risk',
                        data: data.trendMedium || [],
                        borderColor: '#f59e0b',
                        backgroundColor: '#f59e0b',
                        tension: 0.4,
                        pointRadius: 4
                    },
                    {
                        label: 'High Risk',
                        data: data.trendHigh || [],
                        borderColor: '#ef4444',
                        backgroundColor: '#ef4444',
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
                    backgroundColor: '#6366f1',
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
