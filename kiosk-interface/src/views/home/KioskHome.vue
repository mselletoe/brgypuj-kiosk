<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goTo(path) {
  router.replace(path)
}
</script>

<template>
  <div class="kiosk-home py-0 p-8">
    <div class="header-section">
      <div class="text-section">
        <h2 class="welcome-text">Welcome to</h2>
        <h1 class="title-text">Barangay Services</h1>
        <p class="subtitle">
          Select a service below to get started.<br>
          All services are designed for easy touch navigation.
        </p>
      </div>
      <div class="logo-section">
        <img src="@/assets/images/Pob1Logo.svg" alt="Barangay Logo" class="logo" />
      </div>           
    </div>

    <div class="service-container">
      <div class="service-box box1" @click="goTo('document-services')">
        <img src="@/assets/vectors/DocumentServices.svg" alt="Document Services" class="box-logo" />
        <p class="box-title">Document<br>Services</p>
        <p class="box-subtitle">Barangay ID, Clearances,<br>Certificates, and Permits</p>
      </div>
      <div class="service-box box2" @click="goTo('equipment-borrowing')">
        <img src="@/assets/vectors/EquipmentBorrowing.svg" alt="Equipment Borrowing" class="box-logo" />
        <p class="box-title">Equipment<br>Borrowing</p>
        <p class="box-subtitle">Borrow tents, chairs, and<br>other Barangay utilities</p>
      </div>
      <div class="service-box box3" @click="goTo('appointments')">
        <img src="@/assets/vectors/ScheduleAppointment.svg" alt="Schedule Appointment" class="box-logo" />
        <p class="box-title">Schedule<br>Appointment</p>
        <p class="box-subtitle">Schedule meetings with<br>Barangay Officials</p>
      </div>
      <div class="service-box box4" @click="goTo('help-and-support')">
        <img src="@/assets/vectors/HelpSupport.svg" alt="Help & Support" class="box-logo" />
        <p class="box-title">Help &<br>Support</p>
        <p class="box-subtitle">Find answers and<br>get assistance</p>
      </div>
      <div class="service-box box5" @click="goTo('feedback')">
        <img src="@/assets/vectors/Feedback.svg" alt="Feedback" class="box-logo" />
        <p class="box-title">Feedback</p>
        <p class="box-subtitle">Help us improve the<br>Barangay Kiosk<br>experience</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kiosk-home {
  font-family: 'Poppins', sans-serif;
  color: #003a6b;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-section {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.text-section {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.welcome-text {
  font-size: 50px;
  font-weight: 400;
  letter-spacing: -0.03em;
  text-shadow:
    3px 3px 5px rgba(0, 0, 0, 0.3),
    -2px -2px 4px rgba(255, 255, 255, 0.6);
}

.title-text {
  font-size: 68px;
  font-weight: 700;
  line-height: 0.6;
  letter-spacing: -0.03em;
  color: #003a6b;
  text-shadow:
    3px 3px 5px rgba(0, 0, 0, 0.3),
    -2px -2px 4px rgba(255, 255, 255, 0.6);
  margin-bottom: 0.5em;
}

.subtitle {
  font-size: 17.5px;
  font-weight: 400;
  line-height: 1.2;
  letter-spacing: 0em;
  margin: 0;
}

.service-container {
  display: flex;
  margin-top: 2.5em;
  justify-content: space-between;
  width: 100%;
  flex-wrap: wrap;
  gap: 1em;
}

.service-box {
  flex: 1;
  min-width: 165px;
  height: 220px;
  border-radius: 15px;
  box-shadow:
    inset 2px 2px 4px rgba(255, 255, 255, 0.6),
    inset -2px -2px 6px rgba(0, 0, 0, 0.15),
    4px 4px 8px rgba(0, 0, 0, 0.25);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 10px;
  box-sizing: border-box;
  cursor: pointer;
}

.service-box:hover {
  transform: scale(1.05) translateY(-3px);
  box-shadow:
    inset 2px 2px 4px rgba(255, 255, 255, 0.7),
    inset -2px -2px 6px rgba(0, 0, 0, 0.2),
    6px 6px 12px rgba(0, 0, 0, 0.35);
}

.service-box:active {
  transform: scale(0.97);
  box-shadow:
    inset 1px 1px 2px rgba(255, 255, 255, 0.5),
    inset -1px -1px 4px rgba(0, 0, 0, 0.1),
    3px 3px 6px rgba(0, 0, 0, 0.2);
}

.box1 { background-color: #2C67E7; }
.box2 { background-color: #F16C14; }
.box3 { background-color: #21C05C; }
.box4 { background-color: #A451F3; }
.box5 { background-color: #13B3A1; }

.box-logo {
  width: 105px;
  height: 105px;
  margin-bottom: 5px;
}

.box-title {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 18px;
  line-height: 20px;
  letter-spacing: 0;
  color: #ffffff;
  margin: 0 0 5px 0;
}

.box-subtitle {
  font-family: 'Poppins', sans-serif;
  font-weight: 400;
  font-size: 11px;
  line-height: 12px;
  letter-spacing: 0;
  color: #ffffff;
  margin: 0;
}

.logo {
  width: 180px;
  height: 180px;
}
</style>