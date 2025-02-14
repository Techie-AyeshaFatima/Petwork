document.addEventListener('DOMContentLoaded',function() {
  follow_btn = document.querySelector("#follow-btn");
  follow_btn.addEventListener("click", (e) => {
    user = follow_btn.getAttribute("data-user");
    action = follow_btn.textContent.trim();
    form = new FormData();
    form.append("user", user);
    form.append("action", action);
    fetch("/follow/", {
      method: "POST",
      body: form,
    })
    .then((response) => response.json())
    .then((response) => {
      if (response.status == 201) {
        follow_btn.textContent = response.action;
        document.querySelector("#followers").innerHTML = response.follower_count;
      }
    });
  });
});