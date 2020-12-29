function process() {
  let input = document.getElementById('basic-url');
  let text = input.value.trim();
  console.log(text);

  var expression = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
  var regex = new RegExp(expression);

  if (text.match(regex)) {
    //AJAX
    let request = new XMLHttpRequest();
    request.open('POST', 'process');
    request.onreadystatechange = function(){
	     if(request.readyState === 4){
         let response = request.responseText;
         let result = document.getElementById('result');
         result.innerHTML = response;
         remove_gif();
         enable_download();
	     }
    };

    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.send("url="+text);

    let result = document.getElementById('result');
    result.innerHTML = "Waiting for process...";
    load_gif();


  } else {
    input.style.border = "2px solid red";
    alert("Not a valid url");
  }
}

function load_gif(){
  console.log("DEBUG");
  var img = document.createElement("img");
  img.src = "static/img/ajaxLoader.gif";
  img.alt = "wait for scan...";
  img.id = "gif_loader";

  document.body.appendChild(img);
}

function remove_gif(){
  let gif = document.getElementById("gif_loader");
  gif.remove();
}

function download() {
  let today = new Date();
  let date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
  let filename = "report-"+date;

  let textaera = document.getElementById("result");
  let text = textaera.innerHTML;

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function enable_download(){
  let download = document.getElementById("download_btn");
  download.removeAttribute("disabled");
}
