const deleteBtn = document.getElementById("delete-button");
deleteBtn.onclick = function (e) {
  const venueId = e.target.dataset['id'];
  fetch('/venues/' + venueId, {
    method: 'DELETE'
  })
    .then(function () {
      window.location.href = '/venues';
    })
    .catch(function (e) {
      console.log('error', e);
    })
}