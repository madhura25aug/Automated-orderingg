// Chart.js Visualizers for CanteenFlow AI
document.addEventListener("DOMContentLoaded", function () {
  // Orders by Hour Chart
  const ordersHourCanvas = document.getElementById("chartOrdersByHour");
  if (ordersHourCanvas) {
    new Chart(ordersHourCanvas, {
      type: "line",
      data: {
        labels: ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
        datasets: [
          {
            label: "Actual Orders",
            data: [12, 18, 45, 120, 145, 65, 30, 25, 80, 50],
            borderColor: "#0d6efd",
            backgroundColor: "rgba(13, 110, 253, 0.1)",
            fill: true,
            tension: 0.4,
          },
          {
            label: "AI Forecasted Demand",
            data: [15, 20, 50, 130, 150, 70, 35, 30, 85, 55],
            borderColor: "#ff6b35",
            borderDash: [5, 5],
            fill: false,
            tension: 0.4,
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  // Food Waste & Saved Meals Chart
  const wasteCanvas = document.getElementById("chartFoodWaste");
  if (wasteCanvas) {
    new Chart(wasteCanvas, {
      type: "doughnut",
      data: {
        labels: ["Meals Saved", "Orders Donated", "SmartSwapped", "Waste Remaining"],
        datasets: [
          {
            data: [37, 18, 12, 5],
            backgroundColor: ["#10b981", "#3b82f6", "#8b5cf6", "#ef4444"],
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  // Popular Food Items Chart
  const foodCanvas = document.getElementById("chartPopularFoods");
  if (foodCanvas) {
    new Chart(foodCanvas, {
      type: "bar",
      data: {
        labels: ["Masala Dosa", "Veg Burger", "Cold Coffee", "Paneer Roll", "Lemon Juice"],
        datasets: [
          {
            label: "Units Sold Today",
            data: [92, 78, 65, 54, 48],
            backgroundColor: ["#0d6efd", "#38bdf8", "#818cf8", "#c084fc", "#f472b6"],
            borderRadius: 6,
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }
});
