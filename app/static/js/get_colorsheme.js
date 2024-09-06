// Function to extract colors from an image and set CSS variables
async function extractColorPalette(imagePath) {
    // Create an image element
    const img = new Image();
    img.src = imagePath;

    // Wait for the image to load
    await new Promise((resolve) => {
        img.onload = resolve;
    });

    // Create a canvas to draw the image
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    // Get image data
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    // Create an object to count color occurrences
    const colorCounts = {};
    for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const a = data[i + 3];

        // Ignore transparent pixels
        if (a > 0) {
            const color = `rgba(${r}, ${g}, ${b}, ${a / 255})`;
            colorCounts[color] = (colorCounts[color] || 0) + 1;
        }
    }

    // Sort colors by frequency
    const sortedColors = Object.entries(colorCounts).sort((a, b) => b[1] - a[1]);

    // Get the top 6 colors (or however many you want)
    const palette = sortedColors.slice(0, 6).map(color => color[0]);

    // Set CSS variables
    document.documentElement.style.setProperty('--bg', palette[0] || '#142943');
    document.documentElement.style.setProperty('--bg2', palette[1] || 'rgba(24, 25, 38, 0.3)');
    document.documentElement.style.setProperty('--fg', palette[2] || '#cad3f5');
    document.documentElement.style.setProperty('--accent', palette[3] || '#9ABFE5');
    document.documentElement.style.setProperty('--accent-hover', palette[4] || '#9ABFE5');
    document.documentElement.style.setProperty('--accent-pressed', palette[5] || '#babbf1');
}

// Example usage
const imagePath = '../static/bg.jpg'; // Replace with your image path
extractColorPalette(imagePath);
