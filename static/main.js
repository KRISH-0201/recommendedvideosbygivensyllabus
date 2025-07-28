document.addEventListener("DOMContentLoaded", function() {
    const blobDiv = document.getElementById('animated-blob');
    if (blobDiv) {
        blobDiv.innerHTML = `
        <svg viewBox="0 0 220 220">
            <path id="blob" d="M66.6,-65.7C85.9,-49.7,97.9,-24.9,98.3,0.8C98.8,26.4,87.8,52.9,68.5,67.4C49.2,81.9,21.6,84.4,-6.7,86.6C-35.1,88.8,-70.2,90.8,-86.8,76.5C-103.3,62.1,-101.2,31,-96.3,6.4C-91.3,-18.2,-83.5,-36.5,-68.5,-52.2C-53.5,-67.9,-31.3,-81,-7,-82.2C17.2,-83.4,34.5,-72.6,66.6,-65.7Z"
                fill="#ffd767ae"/>
        </svg>
        `;
        const path = document.getElementById('blob');
        let t = 0;
        function animateBlob() {
            t += 0.02;
            const scale = 1 + 0.04 * Math.sin(t * 2.12);
            path.setAttribute('transform', `scale(${scale}) translate(${110-scale*110}, ${110-scale*110})`);
            requestAnimationFrame(animateBlob);
        }
        animateBlob();
    }
    document.querySelectorAll('.video-card').forEach((el, i) => {
        el.style.opacity = 0;
        setTimeout(() => {
            el.classList.add('animate__animated', 'animate__zoomIn');
            el.style.opacity = 1;
        }, 120 + i * 80);
    });
});
