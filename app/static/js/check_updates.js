async function fetchCurrentVersion() {
    const response = await fetch('/api/version');
    if (!response.ok) {
        throw new Error(`HTTP error while fetching current version! status: ${response.status}`);
    }

    const versionData = await response.json();
    if (!versionData || !versionData.version) {
        throw new Error('Current version is undefined or missing from the response.');
    }
    return versionData.version;
}

async function fetchLatestRelease() {
    const apiUrl = `https://api.github.com/repos/DXS-GROUP/SDash/releases/latest`;
    const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
            'Accept': 'application/vnd.github.v3+json',
        }
    });

    if (!response.ok) {
        throw new Error(`HTTP error while fetching release data! status: ${response.status}`);
    }

    const releaseData = await response.json();
    if (!releaseData || !releaseData.tag_name) {
        throw new Error('Latest version is undefined or missing from the response.');
    }
    return releaseData.tag_name;
}

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

async function checkLatestRelease() {
    try {
        const currentVersion = await fetchCurrentVersion();
        const latestVersion = await fetchLatestRelease();
        
        handleVersionComparison(latestVersion, currentVersion);
        
    } catch (error) {
        console.error('Error while checking for updates:', error);
    }
}

function handleVersionComparison(latestVersion, currentVersion) {
    const comparisonResult = compareVersions(latestVersion, currentVersion);

    if (comparisonResult > 0) {
        alert(`New version available: ${latestVersion}. Current version: ${currentVersion}.`);
    } else if (comparisonResult < 0) {
        alert(`You are using an incompatible version: ${currentVersion}. Latest version: ${latestVersion}.`);
    } else {
        alert(`You are using the latest version: ${currentVersion}.`);
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
