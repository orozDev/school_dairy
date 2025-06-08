let e_year = document.getElementById('e_year')
let date = new Date()


if (parseInt(date.getMonth()) > 6 ) e_year.innerHTML= date.getFullYear()+'-'+(parseInt(date.getFullYear())+1)
else if(parseInt(date.getMonth()) < 6) e_year.innerHTML= (parseInt(date.getFullYear())-1)+'-'+date.getFullYear()