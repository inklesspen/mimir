function callReady(fn) {
  if (document.readyState !== 'loading') {
    fn();
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}

function forEachEl(selector, func) {
  Array.prototype.forEach.call(document.querySelectorAll(selector), func);
}

const timgHeight = 480;
const timgWidth = 760;

const thresholdHeight = 500;
const thresholdWidth = 800;


function timgSetup() {
  forEachEl("img[data-mirrored]", (el) => {
    const actualWidth = parseInt(el.getAttribute('data-width'), 10);
    const actualHeight = parseInt(el.getAttribute('data-height'), 10);
    let constrainHeight = false, constrainWidth = false;
    if (actualHeight > thresholdHeight) {
      constrainHeight = true;
    } else if (actualWidth > thresholdWidth) {
      constrainWidth = true;
    } else {
      el.classList.remove('timg');
      return;
    }
    const toggler = () => {
      el.classList.toggle('collapsed');
      if (el.classList.contains('collapsed')) {
        if (constrainHeight) {
          el.setAttribute("height", timgHeight);
        } else if (constrainWidth) {
          el.setAttribute("width", timgWidth);
        }
      } else {
        el.removeAttribute("height");
        el.removeAttribute("width");
      }
    };

    el.classList.add('collapsable');
    el.addEventListener("click", toggler);
    toggler();
  });
}

callReady(timgSetup);
