function process() {
  let input = document.getElementById('input');
  let text = input.value.trim();
  console.log(text);

  var expression = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
  var regex = new RegExp(expression);

  if (text.match(regex)) {
    //AJAX
    let request = new XMLHttpRequest();
    request.open('POST', 'process');
    request.onreadystatechange = function(){
	     if(request.readyState == 4){
         let response = request.responseText;
         let result = document.getElementById('result');
         result.innerHTML = response;
	     }
    };

    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.send("url="+text);

    let result = document.getElementById('result');
    result.innerHTML = "Waiting for process...";


  } else {
    input.style.border = "2px solid red";
    alert("Not a valid url");
  }
}
