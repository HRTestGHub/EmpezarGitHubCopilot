document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      const loadParticipants = async (name, listEl) => {
        try {
          const response = await fetch(
            `/activities/${encodeURIComponent(name)}/participants`
          );

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Unable to load participants");
          }

          const result = await response.json();
          listEl.innerHTML = "";

          if (result.participants.length === 0) {
            listEl.innerHTML = "<li>No participants yet.</li>";
            return;
          }

          result.participants.forEach((participant) => {
            const item = document.createElement("li");
            const textNode = document.createTextNode(participant);
            item.appendChild(textNode);

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className = "participant-delete";
            deleteButton.textContent = "Remove";
            deleteButton.addEventListener("click", async () => {
              const confirmed = window.confirm(
                `¿Eliminar a ${participant} de ${name}? Esta acción no se puede deshacer.`
              );
              if (!confirmed) {
                return;
              }

              try {
                const deleteResponse = await fetch(
                  `/activities/${encodeURIComponent(name)}/participants?email=${encodeURIComponent(participant)}`,
                  {
                    method: "DELETE",
                  }
                );

                if (!deleteResponse.ok) {
                  const error = await deleteResponse.json();
                  throw new Error(error.detail || "Could not remove participant");
                }

                const result = await deleteResponse.json();
                messageDiv.textContent = result.message;
                messageDiv.className = "success";
                messageDiv.classList.remove("hidden");
                setTimeout(() => {
                  messageDiv.classList.add("hidden");
                }, 5000);

                await fetchActivities();
              } catch (error) {
                messageDiv.textContent = error.message;
                messageDiv.className = "error";
                messageDiv.classList.remove("hidden");
              }
            });

            item.appendChild(deleteButton);
            listEl.appendChild(item);
          });
        } catch (error) {
          listEl.innerHTML = `<li class="error">${error.message}</li>`;
        }
      };

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        const participantsButton = document.createElement("button");
        participantsButton.type = "button";
        participantsButton.className = "participants-toggle";
        participantsButton.textContent = "Show participants";

        const participantsContainer = document.createElement("div");
        participantsContainer.className = "participants-container hidden";
        participantsContainer.innerHTML = `
          <h5>Participants</h5>
          <ul class="participants-list"></ul>
        `;

        participantsButton.addEventListener("click", async () => {
          const listEl = participantsContainer.querySelector(".participants-list");
          const isHidden = participantsContainer.classList.toggle("hidden");

          participantsButton.textContent = isHidden ? "Show participants" : "Hide participants";

          if (!isHidden) {
            await loadParticipants(name, listEl);
          }
        });

        activityCard.appendChild(participantsButton);
        activityCard.appendChild(participantsContainer);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
