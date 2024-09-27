const osImageMap = {
    'endeavour': '../static/logo/linux.svg',
    'manjaro': '../static/logo/manjaro.svg',
    'arch': '../static/logo/arch.svg',
    'cent': '../static/logo/centos.svg',
    'fedora': '../static/logo/fedora.svg',
    'mac': '../static/logo/mac.svg',
    'windows': '../static/logo/windows.svg',
    'debian': '../static/logo/debian.svg',
    'hat': '../static/logo/hat.svg',
    'mint': '../static/logo/mint.svg',
    'suse': '../static/logo/suse.svg',
    'ubuntu': '../static/logo/ubuntu.svg'
};

const fetchSystemInfo = async () => {
    try {
        const response = await fetch('/api/system_info');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        const osName = data.sys_platform.toLowerCase();
        
        setOSImage(osName);
        
    } catch (error) {
        console.error('Error fetching system info:', error);
    }
};

const setOSImage = (osName) => {
    const osIconElement = document.getElementById('os_icon');
    
    for (const key in osImageMap) {
        if (osName.includes(key)) {
            osIconElement.src = osImageMap[key];
            return;
        }
    }
    
    osIconElement.src = '../static/logo/os.svg';
};

fetchSystemInfo();
