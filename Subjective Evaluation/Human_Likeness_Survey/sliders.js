/*Credit: https://www.w3schools.com/howto/howto_js_rangeslider.asp (this extends to the html and js files in this directory)*/
var slider1 = document.getElementById("slider1");
var output1 = document.getElementById("slider_output1");
output1.innerHTML = slider1.value;
  
slider1.oninput = function() {
	output1.innerHTML = this.value;
	}

var slider2 = document.getElementById("slider2");
var output2 = document.getElementById("slider_output2");
output2.innerHTML = slider2.value;
  
slider2.oninput = function() {
	output2.innerHTML = this.value;
	}

var slider3 = document.getElementById("slider3");
var output3 = document.getElementById("slider_output3");
output3.innerHTML = slider3.value;
  
slider3.oninput = function() {
	output3.innerHTML = this.value;
	}
	
var slider4 = document.getElementById("slider4");
var output4 = document.getElementById("slider_output4");
output4.innerHTML = slider4.value;
  
slider4.oninput = function() {
	output4.innerHTML = this.value;
	}

/*Credit: https://stackoverflow.com/questions/3665115/how-to-create-a-file-in-memory-for-user-to-download-but-not-through-server */
function download(studyseq, ba_score, n_score, new_score, sc_score) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + 'Cond_BA: ' + encodeURIComponent(ba_score) + '\nCond_N: ' + encodeURIComponent(n_score)
						+ '\nCond_New: ' + encodeURIComponent(new_score) + '\nCond_SC: ' + encodeURIComponent(sc_score) );
  element.setAttribute('download', studyseq);
  element.style.display = 'none';
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}