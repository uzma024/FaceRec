console.log("This is javascript");
const video = document.querySelector("#videoElement");
const showVideo = document.querySelector("#stop");
const icon = document.querySelector("#stop .btn");

console.log("This is javascript");
function stop() {
    let stream = video.srcObject;
    let tracks = stream.getTracks();
    for (let i=0; i<tracks.length; i++) { tracks[i].stop(); }
    video.srcObject = null;
    icon.classList.remove('fa-video');
    icon.classList.add('fa-video-slash');
    showVideo.style.backgroundColor = 'rgb(255, 117, 117)';
}

function start(){
    if(navigator.mediaDevices.getUserMedia){
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream)
        .catch(() => {
            console.log("Something went wrong!");
            alert("Could not start the camera");
        });
    }
    else{ alert("Could not start the camera"); }
    icon.classList.remove('fa-video-slash');
    icon.classList.add('fa-video');
    showVideo.style.backgroundColor = 'white';
}

showVideo.addEventListener("click", (e) => {
    console.log("This is addEventListener");
    e.preventDefault();
    if(video.srcObject != null){ stop(); }
    else{ start(); };
});


// Camera things
const capture = document.querySelector("#capture .btn");
const canvas = document.querySelector("#canvas");
const input = document.getElementById('imageInput');
const form = document.getElementById('postImage');
const user_sno = document.getElementById('sno');
const user_name = document.getElementById('username');

const main_main = document.getElementById('main')
const main_success = document.getElementById('success')
const main_success_att = document.getElementById('att_success')
const main_failure = document.getElementById('failure')
const camera_button = document.getElementById('capture')
// let sound = new Audio('/static/scripts/sound.mp3')

const success_page = ['Successfully logged in', 'User was successfully registered']
const failure_page = ['No Face Detected', 'Multiple Faces Detected', 'No Match Found', 'Fake Face Detected', 'Fake Face Detected', 'Face Matched with existing user']

capture.addEventListener('click', (e) => {
    e.preventDefault();
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    if(video.srcObject != '' && video.srcObject != undefined && video.srcObject != null){ 
        camera_button.style.backgroundColor = 'white'
        // sound.play()
        video.pause()
        setTimeout(() => {
            video.play();
            camera_button.style.backgroundColor = 'rgb(255, 117, 117)'
        }, 1000);

        let img_src = canvas.toDataURL('image/jpeg');
        let src = img_src.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");
        let message = { image: src, sno: user_sno.innerText, name: user_name.innerText};
        console.log("Here is your message: " + message);
        

        var sno_string= user_sno.innerText;
        console.log(user_sno);
        console.log(sno_string.length);

        if(sno_string == '-1'){
            alert("Kindly wait till we are analysing your face");
            $.post('/test-image', JSON.stringify(message), response => {
                $("#res-prediction").text(response.prediction.result)
                console.log(response);
                main_main.style.display = "none";
                console.log("This is response1: "+response.prediction.result);
                var found=false;
    
                if(success_page[0] == response.prediction.result || success_page[1] == response.prediction.result){
                    console.log("Successfully Logged in as admin");
                    main_success.style.display = 'block';
                    found=true;
                }
                
                if(!found){
                    console.log("Failure");
                    main_failure.style.display = 'block';
                }
            });
        }else{
            $.post('/test-image', JSON.stringify(message), response => {
                $("#res-prediction").text(response.prediction.result)
                console.log(response);
                main_main.style.display = "none";
                console.log("This is response2: "+response.prediction.result);
                var found=false;
    
                if(success_page[1] == response.prediction.result){
                    console.log("User was successfully registered");
                    main_success.style.display = 'block';
                    found=true;
                }
                
                if(!found){
                    console.log("Failure");
                    main_failure.style.display = 'block';
                }
            });
        }
        
        // input.setAttribute('value', JSON.stringify(message));
        // form.submit();
    }
});
