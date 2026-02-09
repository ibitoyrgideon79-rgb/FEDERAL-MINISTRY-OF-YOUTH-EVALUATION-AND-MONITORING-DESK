const API_BASE = window.location.origin; // Use same origin as frontend
let currentEmail = "";
const EMAILJS_CONFIG = window.EMAILJS_CONFIG || {};
let emailjsReady = false;

function isEmailJSConfigured() {
  return (
    EMAILJS_CONFIG &&
    typeof EMAILJS_CONFIG.serviceId === "string" &&
    EMAILJS_CONFIG.serviceId.trim() &&
    typeof EMAILJS_CONFIG.templateId === "string" &&
    EMAILJS_CONFIG.templateId.trim() &&
    typeof EMAILJS_CONFIG.publicKey === "string" &&
    EMAILJS_CONFIG.publicKey.trim()
  );
}

function initEmailJS() {
  if (emailjsReady) return;
  if (!window.emailjs) return;
  if (!isEmailJSConfigured()) return;
  window.emailjs.init({ publicKey: EMAILJS_CONFIG.publicKey });
  emailjsReady = true;
}

async function sendOtpEmail(email, code) {
  if (!window.emailjs) {
    throw new Error("EmailJS library is not loaded");
  }
  if (!isEmailJSConfigured()) {
    throw new Error("EmailJS is not configured");
  }
  initEmailJS();

  const subject = "Your login OTP";
  const message = `Your OTP is ${code}. It expires in ${EMAILJS_CONFIG.otpExpiryMinutes || 5} minutes.`;

  return window.emailjs.send(
    EMAILJS_CONFIG.serviceId,
    EMAILJS_CONFIG.templateId,
    {
      to_email: email,
      subject,
      message,
    },
  );
}

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

    const data = await response.json();
    currentEmail = email;

    if (data && data.otp_code) {
      try {
        await sendOtpEmail(email, data.otp_code);
      } catch (err) {
        if (emailError) {
          emailError.textContent = err.message || "Failed to send OTP email.";
          emailError.style.display = "block";
        }
        return;
      }
    }

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
    const payload = { email: currentEmail, code: otp };
    console.log("Sending verify request with payload:", payload);

    const response = await fetch(`${API_BASE}/auth/verify-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload),
    });

    console.log("Response status:", response.status);
    console.log("Response ok:", response.ok);

    const responseText = await response.text();
    console.log("Response text:", responseText);

    if (!response.ok) {
      let errorDetail = "Invalid or expired OTP. Please try again.";
      try {
        const errorData = JSON.parse(responseText);
        errorDetail = errorData.detail || errorDetail;
      } catch (e) {
        errorDetail = responseText || "Server error";
      }
      if (otpError) {
        otpError.textContent = errorDetail;
        otpError.style.display = "block";
      }
      return;
    }

    let userData;
    try {
      userData = JSON.parse(responseText);
    } catch (e) {
      console.error("Could not parse response JSON:", e);
      if (otpError) {
        otpError.textContent = "Invalid server response: " + responseText;
        otpError.style.display = "block";
      }
      return;
    }

    console.log("Login successful:", userData);

    // Redirect only admins
    if (userData.role === "admin") {
      window.location.href = "/admin.html";
    } else {
      if (otpError) {
        otpError.textContent = "Admin access only.";
        otpError.style.display = "block";
      }
    }
  } catch (err) {
    console.error("Error verifying OTP:", err);
    if (otpError) {
      otpError.textContent = "Network error: " + err.message;
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
