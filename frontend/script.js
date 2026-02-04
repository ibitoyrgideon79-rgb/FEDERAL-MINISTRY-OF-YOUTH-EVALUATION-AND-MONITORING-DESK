const API_BASE = "http://localhost:8000";
let currentEmail = "";
const ADMIN_EMAIL = "ibitoyrgideon79@gmail.com";

function showEmailBox() {
  const emailBox = document.getElementById("email-box");
  const loginButton = document.getElementById("login-button");
  if (emailBox && loginButton) {
    emailBox.style.display = "block";
    loginButton.style.display = "none";
    const emailInput = document.getElementById("email-input");
    if (emailInput) emailInput.focus();
  }
}

function showOtpBox() {
  const otpBox = document.getElementById("otp-box");
  const emailBox = document.getElementById("email-box");
  if (otpBox && emailBox) {
    otpBox.style.display = "block";
    emailBox.style.display = "none";
    otpBox.scrollIntoView({ behavior: "smooth", block: "center" });
    const otpInput = document.getElementById("otp-input");
    if (otpInput) otpInput.focus();
  }
}

async function requestOtp() {
  const emailInput = document.getElementById("email-input");
  const email = emailInput?.value?.trim();
  const emailError = document.getElementById("email-error");

  if (!email) {
    if (emailError) {
      emailError.textContent = "Please enter your email address.";
      emailError.style.display = "block";
    }
    return;
  }

  if (emailError) {
    emailError.style.display = "none";
  }

  try {
    const response = await fetch(`${API_BASE}/auth/request-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const data = await response.json();
      if (emailError) {
        emailError.textContent = data.detail || "Failed to send OTP. Please try again.";
        emailError.style.display = "block";
      }
      return;
    }

    currentEmail = email;
    showOtpBox();
  } catch (err) {
    console.error("Error requesting OTP:", err);
    if (emailError) {
      emailError.textContent = "Network error. Please check your connection.";
      emailError.style.display = "block";
    }
  }
}

async function verifyOtp() {
  const otpInput = document.getElementById("otp-input");
  const otp = otpInput?.value?.trim();
  const otpError = document.getElementById("otp-error");

  if (!otp || otp.length !== 6) {
    if (otpError) {
      otpError.textContent = "Please enter a valid 6-digit code.";
      otpError.style.display = "block";
    }
    return;
  }

  if (otpError) {
    otpError.style.display = "none";
  }

  try {
    const response = await fetch(`${API_BASE}/auth/verify-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email: currentEmail, code: otp }),
    });

    if (!response.ok) {
      const data = await response.json();
      if (otpError) {
        otpError.textContent = data.detail || "Invalid or expired OTP. Please try again.";
        otpError.style.display = "block";
      }
      return;
    }

    const userData = await response.json();
    console.log("Login successful:", userData);

    // Redirect based on role
    if (userData.role === "admin" || userData.email === ADMIN_EMAIL) {
      window.location.href = "/admin";
    } else {
      window.location.href = "/dashboard";
    }
  } catch (err) {
    console.error("Error verifying OTP:", err);
    if (otpError) {
      otpError.textContent = "Network error. Please try again.";
      otpError.style.display = "block";
    }
  }
}

// Allow Enter key for email and OTP inputs
document.addEventListener("DOMContentLoaded", () => {
  const emailInput = document.getElementById("email-input");
  const otpInput = document.getElementById("otp-input");

  if (emailInput) {
    emailInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") requestOtp();
    });
  }

  if (otpInput) {
    otpInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") verifyOtp();
    });
  }
});
