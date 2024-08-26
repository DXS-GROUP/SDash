function switchTab(tab) {
    const tabs = ['monitor', 'info', 'services', 'control', 'logs'];
    tabs.forEach(t => {
        const tabContent = document.getElementById(t);
        if (t === tab) {
            tabContent.classList.add('active');
            tabContent.classList.remove('hidden');
        } else {
            tabContent.classList.remove('active');
            tabContent.classList.add('hidden');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    switchTab('monitor');
});
