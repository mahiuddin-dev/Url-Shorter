



  var removebtn = document.getElementsByClassName("removelink");
  Removelink(removebtn)


function Removelink(removebtn){
  var i,j;
  for(i = 0; i < removebtn.length; i++){
    removebtn[i].addEventListener('click', function(){
        var action = this.dataset.action;
        var shortlinkId = this.dataset.productId;

        if (User === "AnonymousUser") {
            console.log("User is not logged in");
        }
        else{
            updatelink(shortlinkId, action)
        }

    })
}

}

function updatelink(shortlinkId, action){
    var url = "/update_link/";

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({
        shortlinkId: shortlinkId,
        action: action,
      }),
    })
      .then((response) => {
        location.reload();
      })
      .then((data) => {
        location.reload();
      });
  }