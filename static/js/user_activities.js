function deleteActivity(activityId) {
  if (confirm("Are you sure you want to delete this activity?")) {
    fetch(`/delete_activity/${activityId}`, {
        method: "DELETE"
      })
      .then(response => {
        if (response.ok) {
          location.reload(); // Làm mới trang web
        } else {
          throw new Error(`Error deleting activity: ${response.status} ${response.statusText}`);
        }
      })
      .catch(error => {
        console.error("Error deleting activity:", error);
      });
  }
}