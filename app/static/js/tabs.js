function switchTab(tab) {
    const tabs = ['monitor', 'info', 'control'];
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

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modal');
    const closeButton = document.getElementsByClassName('close-button')[0];
    const tabButtons = document.getElementsByClassName('tab-button');

    document.addEventListener('keydown', function(event) {
        if (event.shiftKey && event.key === 'C') {
            modal.style.display = 'block';
        }
    });

    closeButton.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    Array.from(tabButtons).forEach(button => {
        button.addEventListener('click', function() {
            const activeButton = document.querySelector('.tab-button.active');
            activeButton.classList.remove('active');
            this.classList.add('active');

            const tab = this.getAttribute('data-tab');
            switchTab(tab);
        });
    });

    function switchTab(tab) {
        const tabContents = document.getElementsByClassName('tab-content');
        Array.from(tabContents).forEach(content => {
            if (content.id === tab) {
                content.classList.add('active');
                content.classList.remove('hidden');
            } else {
                content.classList.remove('active');
                content.classList.add('hidden');
            }
        });
    }

    switchTab('monitor');
});
