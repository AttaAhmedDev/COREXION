// 3. OFFICE SELECTION - مع تحديث البيانات
const officeData = {
  "United Kingdom": {
    name: "COREXION — UNITED KINGDOM",
    address: "United Kingdom office<br>Contact our team for project enquiries.",
    email: "info@corexion.com",
    cta_title: "START A CONVERSATION",
    cta_desc:
      "Tell us about your project and our experts will get back to you.",
  },
  USA: {
    name: "COREXION — USA",
    address: "USA office<br>Contact our team for project enquiries.",
    email: "info@corexion.com",
    cta_title: "START A CONVERSATION",
    cta_desc:
      "Tell us about your project and our experts will get back to you.",
  },
  Canada: {
    name: "COREXION — CANADA",
    address: "Canada office<br>Contact our team for project enquiries.",
    email: "info@corexion.com",
    cta_title: "START A CONVERSATION",
    cta_desc:
      "Tell us about your project and our experts will get back to you.",
  },
  Malaysia: {
    name: "COREXION ASIA PACIFIC — MALAYSIA",
    address: "Malaysia office<br>Contact our team for project enquiries.",
    email: "info@corexion.com",
    cta_title: "START A CONVERSATION",
    cta_desc:
      "Tell us about your project and our experts will get back to you.",
  },
  "Saudi Arabia": {
    name: "COREXION MIDDLE EAST — SAUDI ARABIA",
    address: "Saudi Arabia office<br>Contact our team for project enquiries.",
    email: "info@corexion.com",
    cta_title: "START A CONVERSATION",
    cta_desc:
      "Tell us about your project and our experts will get back to you.",
  },
  Egypt: {
    name: "COREXION — EGYPT",
    address: "Egypt office<br>Contact our team for project enquiries.",
    email: "info@corexion.com",
    cta_title: "START A CONVERSATION",
    cta_desc:
      "Tell us about your project and our experts will get back to you.",
  },
};

const offices = document.querySelectorAll(".office");
const officeName = document.getElementById("officeName");
const officeAddress = document.getElementById("officeAddress");
const officeEmail = document.getElementById("officeEmail");
const officeCtaTitle = document.getElementById("officeCtaTitle");
const officeCtaDesc = document.getElementById("officeCtaDesc");

offices.forEach((office) => {
  office.addEventListener("click", function () {
    offices.forEach((o) => o.classList.remove("active"));
    this.classList.add("active");
    const key = this.dataset.office;
    if (officeData[key]) {
      officeName.textContent = officeData[key].name;
      officeAddress.innerHTML = officeData[key].address;
      officeEmail.textContent = officeData[key].email;
      officeEmail.href = `mailto:${officeData[key].email}`;
      officeCtaTitle.textContent = officeData[key].cta_title;
      officeCtaDesc.textContent = officeData[key].cta_desc;
    }
  });
});

// 4. CONTACT FORM
document.getElementById("contactForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const message = document.getElementById("formMessage");
  message.className = "form-message success";
  message.textContent =
    "Thank you. Your enquiry has been prepared successfully.";
  this.reset();
});
