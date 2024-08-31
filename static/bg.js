const system_colors = {
    manjaro: "#50FA7B",
    arch: "#8BE9FD",
    kali: "#6272A4",
    endevaour: "#BD93F9",
    centos: "#F1FA8C",
    debian: "#FF5555",
    ubuntu: "#FFB86C",
    suse: "#50FA7B",
    parrot: "#191849"
}

fetch('/get_os')
    .then(response => response.json())
    .then(data => {
        const main_block = document.getElementsByClassName('html')[0];
        const system_block = document.getElementById('system_info');

        if (main_block) {
            const osName = data.os_name;
            let logoColor = 'gray';
            let logoPath = "../static/logo/os.svg";

            if (osName.toLowerCase().includes('arch')) {
                logoColor = system_colors.arch;
                logoPath = "../static/logo/arch.svg";
            } else if (osName.toLowerCase().includes('debian')) {
                logoColor = system_colors.debian;
                logoPath = "../static/logo/debian.svg";
            } else if (osName.toLowerCase().includes('ubuntu')) {
                logoColor = system_colors.ubuntu;
                logoPath = "../static/logo/ubuntu.svg";
            } else if (osName.toLowerCase().includes('suse')) {
                logoColor = system_colors.suse;
                logoPath = "../static/logo/suse.svg";
            } else if (osName.toLowerCase().includes('manjaro')) {
                logoColor = system_colors.manjaro;
                logoPath = "../static/logo/manjaro.svg";
            } else if (osName.toLowerCase().includes('centos')) {
                logoColor = system_colors.centos;
                logoPath = "../static/logo/centos.svg";
            } else if (osName.toLowerCase().includes('kali')) {
                logoColor = system_colors.kali;
                logoPath = "../static/logo/os.svg";
            } else if (osName.toLowerCase().includes('endeavour')) {
                logoColor = system_colors.endevaour;
                logoPath = "../static/logo/linux.svg";
            } else if (osName.toLowerCase().includes('parrot')) {
                logoColor = system_colors.parrot;
                logoPath = "../static/logo/os.svg";
            } else if (osName.toLowerCase().includes('fedora')) {
                logoColor = system_colors.kali;
                logoPath = "../static/logo/fedora.svg";
            } else if (osName.toLowerCase().includes('red hat')) {
                logoColor = system_colors.debian;
                logoPath = "../static/logo/hat.svg";
            } else if (osName.toLowerCase().includes('mac')) {
                logoColor = system_colors.centos;
                logoPath = "../static/logo/mac.svg";
            }

            console.debug(logoPath)
            console.debug(logoColor)

            const backgroundStyle = "" + colors.bg + "";

            main_block.style.background = backgroundStyle;
            system_block.style.backgroundImage = `url('${logoPath}')`;
            system_block.style.backgroundRepeat = 'no-repeat';
            system_block.style.backgroundPosition = 'center';
            system_block.style.backgroundSize = '30%';
        } else {
            console.error("Element with class 'html' not found.");
        }
    })
    .catch(error => console.error(error))
