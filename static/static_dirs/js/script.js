let btn = document.getElementById('btn');
let bar = document.getElementById('bars');


btn.onclick = function () {
    bar.classList.toggle('hid');

    if(btn.children[0].classList[1] === 'fa-bars'){
        btn.children[0].classList.replace('fa-bars', 'fa-times');
    }
    else{
        btn.children[0].classList.replace('fa-times', 'fa-bars');
    }
};




