(function(){
  var bar=document.querySelector('.read-progress');
  function progress(){var total=document.documentElement.scrollHeight-innerHeight;bar.style.width=(total>0?scrollY/total*100:0)+'%';}
  addEventListener('scroll',progress,{passive:true});addEventListener('resize',progress);progress();
})();
(function(){
 var control=document.getElementById('coverMotionToggle');
 if(!control)return;
 var reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 function setPaused(paused){document.body.classList.toggle('motion-paused',paused);control.setAttribute('aria-pressed',String(paused));control.setAttribute('aria-label',paused?'Включить движение обложки':'Остановить движение обложки');control.innerHTML=paused?'<span aria-hidden="true">▶</span> Движение':'<span aria-hidden="true">Ⅱ</span> Пауза';}
 setPaused(reduced);
 if(reduced){control.disabled=true;control.innerHTML="Без движения";control.title="Движение отключено системной настройкой";}
 control.addEventListener('click',function(){setPaused(!document.body.classList.contains('motion-paused'));});
})();
