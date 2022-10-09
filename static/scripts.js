function myFunction() {
  var x = document.getElementById("myLinks");
  var y = document.getElementById("spacer");
  if (x.style.display === "flex") {
    x.style.display = "none";
    y.style.padding = "2.5rem";
  } else {
    x.style.display = "flex";
    y.style.padding = "5rem";
  }
}