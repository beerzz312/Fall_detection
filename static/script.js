// script.js

// รับอ้างอิงฟอร์ม HTML
const selfForm = document.getElementById('self');

// เมื่อฟอร์มถูกส่ง
selfForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // ป้องกันการโหลดหน้าใหม่เมื่อส่งฟอร์ม

    // รับค่าจากฟอร์ม
    const name = document.getElementById('name').value;
    const age = document.getElementById('age').value;
    const cd = document.getElementById('cd').value;
    const pm = document.getElementById('pm').value;
    const ecall = document.getElementById('ecall').value;
    const ad = document.getElementById('ad').value;
    const map = document.getElementById('map').value;

    // สร้างข้อมูลที่จะส่งไปยัง API
    const formData = {
        name: name,
        age: age,
        cd: cd,
        pm: pm,
        ecall: ecall,
        ad: ad,
        map: map
    };

    // เรียกใช้ API เพื่อส่งข้อมูล
    try {
        const response = await fetch('/patients', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('เกิดข้อผิดพลาดในการส่งข้อมูล');
        }

        // รับคำตอบ
        const data = await response.json();
        console.log('ข้อมูลถูกส่งไปยังเซิร์ฟเวอร์:', data);

        // รีเซ็ตฟอร์ม
        form.reset();
    } catch (error) {
        console.error('เกิดข้อผิดพลาด:', error.message);
    }
    loadPatients();
});


// รับอ้างอิงข้อมูลแสดงผลผู้ป่วย
const patientList = document.getElementById('patientList');

// ฟังก์ชันสำหรับโหลดข้อมูลผู้ป่วยและแสดงผล
async function loadPatients() {
    try {
        const response = await fetch('/patients/');
        const patients = await response.json();
        
        // เคลียร์รายการผู้ป่วยเดิมทั้งหมด
        patientList.innerHTML = '';

        // สร้างรายการผู้ป่วยใหม่
        patients.forEach(patient => {
            const patientDiv = document.createElement('div');
            patientDiv.innerHTML = `
                <strong>Name:</strong> ${patient.name}<br>
                <strong>age:</strong> ${patient.age}<br>
                <strong>CD:</strong> ${patient.cd}<br>
                <strong>pm:</strong> ${patient.pm}<br>
                <strong>ECALL:</strong> ${patient.ecall}<br>
                <strong>AD:</strong> ${patient.ad}<br>
                <strong>Map:</strong> ${patient.map}<br>
            `;
            patientList.appendChild(patientDiv);
        });
    } catch (error) {
        console.error('Error:', error);
    }
}


// เรียกใช้ฟังก์ชันเพื่อโหลดข้อมูลผู้ป่วยและแสดงผลเมื่อหน้าเว็บโหลดเสร็จ
loadPatients();

const updatePatientForm = document.getElementById('updatePatientForm');

updatePatientForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const name = document.getElementById('updateName').value;
  const cd = document.getElementById('updateCd').value;
  const age = document.getElementById('updateAge').value;
  const pm = document.getElementById('updatePm').value;
  const ecall = document.getElementById('updateEcall').value;
  const ad = document.getElementById('updateAd').value;
  const map = document.getElementById('updateMap').value;
  const patientId = prompt('Enter patient ID to update:');
  
  try {
    const response = await fetch(`/patients/${patientId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name,age, cd,pm, ecall, ad, map })
    });

    if (response.ok) {
      console.log('Patient updated successfully');
      loadPatients(); // รีโหลดรายการผู้ป่วยหลังจากอัปเดตสำเร็จ
    } else {
      console.error(`Failed to update patient. Status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
});



const form = document.getElementById('cameraForm');
const camerasList = document.getElementById('cameras');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const number = document.getElementById('number').value;
    const ip = document.getElementById('ip').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
        const response = await fetch('/cameras/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              number,
              ip,
              username,
              password,
            })
        });
        const data = await response.json();
        console.log(data);
        // Clear form fields after successful submission
        form.reset();
        // Reload cameras list
        loadCameras();
    } catch (error) {
        console.error('Error:', error);
    }
});
async function loadCameras() {
    try {
      const response = await fetch('/cameras/');
      const data = await response.json();
      console.log(data);
      camerasList.innerHTML = '';
      data.forEach(camera => {
        const cameraDiv = document.createElement('div');
        cameraDiv.innerHTML = `
        <strong>Camera ID:</strong> ${camera.id}<br>
        <strong>Camera Number:</strong> ${camera.number}<br>
        <strong>IP Address:</strong> ${camera.ip}<br>
        <strong>Username:</strong> ${camera.username}<br>
        <strong>Password:</strong> ${camera.password}<br>
        `;
        camerasList.appendChild(cameraDiv);
      });
  
    } catch (error) {
      console.error('Error:', error);
    }
  }

const updateCameraForm = document.getElementById('updateCameraForm');

updateCameraForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const number = document.getElementById('updateNumber').value;
  const ip = document.getElementById('updateIp').value;
  const username = document.getElementById('updateUsername').value;
  const password = document.getElementById('updatePassword').value;
  const cameraId = prompt('Enter camera ID to update:');
  try {
    const response = await fetch(`/cameras/${cameraId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ number, ip, username, password, ad, map })
    });

    if (response.ok) {
      console.log('Camera updated successfully');
      loadCameras(); // Reload cameras list after successful update
    } else {
      console.error(`Failed to update camera. Status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
});
// Load cameras initially


      const tokenInput = document.getElementById("tokenInput");
      const addButton = document.getElementById("addButton");
      const tokenList = document.getElementById("tokenList");

      addButton.addEventListener("click", addToken);

      async function addToken() {
        const token = tokenInput.value.trim();
        if (token) {
          try {
            const response = await fetch("/tokens/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ token }),
            });

            if (response.ok) {
              tokenInput.value = "";
              updateTokenList();
            } else {
              const errorData = await response.json();
              console.error("Error adding token:", errorData.error);
            }
          } catch (error) {
            console.error("Error adding token:", error);
          }
        }
      }

      async function updateTokenList() {
        try {
          const response = await fetch("/tokens/");
          const tokens = await response.json();

          tokenList.innerHTML = "";
          tokens.forEach((token) => {
            const li = document.createElement("li");
            li.textContent = token.token;
            tokenList.appendChild(li);
          });
        } catch (error) {
          console.error("Error retrieving tokens:", error);
        }
      }

      loadCameras();
      updateTokenList();

// const iframeContainer = document.querySelector('.iframe-container');
// const iframe = iframeContainer.querySelector('iframe');

// function resizeIframe() {
//   const containerWidth = iframeContainer.offsetWidth;
//   const containerHeight = iframeContainer.offsetHeight;

//   const iframeRatio = iframe.width / iframe.height;
//   const newIframeWidth = Math.min(containerWidth, containerHeight * iframeRatio);
//   const newIframeHeight = Math.min(containerHeight, newIframeWidth / iframeRatio);

//   iframe.style.width = `${newIframeWidth}px`;
//   iframe.style.height = `${newIframeHeight}px`;
// }

// resizeIframe();
// window.addEventListener('resize', resizeIframe);