async function checkLatestRelease() {
    const owner = 'SDashS';
    const repo = "SDash";
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/releases/latest`;

    try {
        const versionResponse = await fetch('/api/version');
        if (!versionResponse.ok) {
            throw new Error(`HTTP error while fetching current version! status: ${versionResponse.status}`);
        }

        const versionData = await versionResponse.json();

        if (!versionData || !versionData.version) {
            throw new Error('Current version is undefined or missing from the response.');
        }

        const currentVersion = versionData.version; // Предполагается, что версия возвращается в формате { "version": "0.3.7" }

        const releaseResponse = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/vnd.github.v3+json',
            }
        });

        if (!releaseResponse.ok) {
            throw new Error(`HTTP error while fetching release data! status: ${releaseResponse.status}`);
        }

        const releaseData = await releaseResponse.json();

        if (!releaseData || !releaseData.tag_name) {
            throw new Error('Latest version is undefined or missing from the response.');
        }

        const latestVersion = releaseData.tag_name;

        function compareVersions(v1, v2) {
            const v1Parts = v1.split('.').map(Number);
            const v2Parts = v2.split('.').map(Number);

            for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
                const v1Part = v1Parts[i] || 0;
                const v2Part = v2Parts[i] || 0;

                if (v1Part > v2Part) return 1;
                if (v1Part < v2Part) return -1;
            }
            return 0;
        }

        const comparisonResult = compareVersions(latestVersion, currentVersion);

        if (comparisonResult > 0) {
            alert(`New version available: ${latestVersion}. Current version: ${currentVersion}.`);
        } else if (comparisonResult < 0) {
            alert(`You are using an incompatible version: ${currentVersion}. Latest version: ${latestVersion}.`);
        } else {
            alert(`You are using the latest version: ${currentVersion}.`);
        }
    } catch (error) {
        console.error('Error while checking for updates:', error);
    }
}

async function showVersion() {
    const versionResponse = await fetch('/api/version');

    if (!versionResponse.ok) {
        throw new Error(`HTTP error while fetching current version! status: ${versionResponse.status}`);
    }
    else {
        const versionData = await versionResponse.json();
        document.getElementById("version").innerHTML = versionData.version;
    }

}

showVersion();
