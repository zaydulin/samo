    const startVideoButton = document.getElementById('startVideo');
    const shareScreenButton = document.getElementById('shareScreen');
    const localVideo = document.getElementById('localVideo');

    let localStream = null;

    startVideoButton.addEventListener('click', async () => {
        try {
            localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            localVideo.srcObject = localStream;
        } catch (error) {
            console.error('Error accessing media devices.', error);
        }
    });

    shareScreenButton.addEventListener('click', async () => {
        try {
            const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
            const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Combine screen and audio streams
            const combinedStream = new MediaStream([...screenStream.getTracks(), ...audioStream.getTracks()]);

            localVideo.srcObject = combinedStream;

            // Handle end of screen sharing
            screenStream.getVideoTracks()[0].addEventListener('ended', () => {
                localVideo.srcObject = localStream;
            });
        } catch (error) {
            console.error('Error sharing screen.', error);
        }
    });