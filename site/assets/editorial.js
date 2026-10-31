(function(){
  var bar=document.querySelector('.read-progress');
  function progress(){var total=document.documentElement.scrollHeight-innerHeight;bar.style.width=(total>0?scrollY/total*100:0)+'%';}
  addEventListener('scroll',progress,{passive:true});addEventListener('resize',progress);progress();
})();
(function(){
 var control=document.getElementById('coverMotionToggle');
 if(!control)return;
 var reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 var en=document.documentElement.lang==='en';
 function setPaused(paused){document.body.classList.toggle('motion-paused',paused);control.setAttribute('aria-pressed',String(paused));control.setAttribute('aria-label',en?(paused?'Play cover animation':'Pause cover animation'):(paused?'Включить движение обложки':'Остановить движение обложки'));control.innerHTML=paused?'<span aria-hidden="true">▶</span> '+(en?'Play':'Движение'):'<span aria-hidden="true">Ⅱ</span> '+(en?'Pause':'Пауза');}
 setPaused(reduced);
 if(reduced){control.disabled=true;control.innerHTML=en?'Motion off':'Без движения';control.title=en?'Animation disabled by your system preference':'Движение отключено системной настройкой';}
 control.addEventListener('click',function(){setPaused(!document.body.classList.contains('motion-paused'));});
})();
