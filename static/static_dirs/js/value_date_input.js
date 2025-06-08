tag = document.getElementById('date');
date = new Date();
let month = '';
let day = '';
if (date.getMonth() < 10) month = '0'+date.getMonth()
else  month = date.getMonth()

if (date.getDate() < 10) day = '0'+date.getDate()
else day = date.getDate()

tag.value = date.getFullYear()+'-'+month+'-'+day