const key = new URLSearchParams(location.search).get('key');
const auth = {'X-Lora-Key': key || ''};
const list = document.querySelector('#media-list'), video = document.querySelector('#video'), image = document.querySelector('#image');
const empty = document.querySelector('#empty'), exportButton = document.querySelector('#export'), status = document.querySelector('#status');
const pathsElement = document.querySelector('#paths');
const serverUrls = document.querySelector('#server-urls'), shutdownButton = document.querySelector('#shutdown');
const tools = document.querySelector('#video-tools'), seek = document.querySelector('#seek'), time = document.querySelector('#time');
let media = [], current = -1;
const isVideo = name => /\.(mp4|mov|mkv|avi|webm|m4v|flv)$/i.test(name);
const formatTime = n => { n = Math.max(0, Math.floor(n || 0)); return `${String(Math.floor(n/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`; };
async function loadMedia(){
  const response = await fetch('/api/media', {headers:auth}); if(!response.ok) throw new Error('无法读取媒体列表');
  media = (await response.json()).files; renderList(); if(current < 0 && media.length) select(0);
}
function renderList(){ list.innerHTML=''; media.forEach((item, index)=>{const b=document.createElement('button');b.className='media-item'+(index===current?' active':'');b.textContent=(isVideo(item.name)?'🎬 ':'🖼️ ')+item.name;b.onclick=()=>select(index);list.append(b);}); }
async function loadPaths(){
  const response = await fetch('/api/paths', {headers:auth}); if(!response.ok) throw new Error('无法读取保存位置');
  const paths = await response.json();
  document.querySelector('#upload-status').textContent='手机上传的视频和图片会保存到电脑：';
  pathsElement.textContent=`素材：${paths.upload_dir}\n导出 JPEG：${paths.export_dir}`;
  status.textContent=`导出 JPEG 会保存到：${paths.export_dir}`;
}
async function loadServerInfo(){
  const response=await fetch('/api/server-info',{headers:auth});if(!response.ok)throw new Error('无法读取手机地址');
  const urls=(await response.json()).urls;serverUrls.textContent='';
  if(!urls.length){serverUrls.textContent='未检测到局域网地址；请确认电脑已连接 Wi-Fi。';return;}
  urls.forEach(url=>{const a=document.createElement('a');a.href=url;a.textContent=url;serverUrls.append(a);});
}
function select(index){
  if(index < 0 || index >= media.length) return; current=index; const item=media[index], url=item.url+'?key='+encodeURIComponent(key); renderList();
  exportButton.disabled=false; empty.hidden=true; status.textContent='预览中：'+item.name;
  if(isVideo(item.name)){ image.hidden=true; video.hidden=false; tools.hidden=false; video.src=url; video.load(); }
  else { video.pause(); video.hidden=true; tools.hidden=true; image.hidden=false; image.src=url; }
}
function updateTime(){seek.max=video.duration||0;seek.value=video.currentTime||0;time.textContent=`${formatTime(video.currentTime)} / ${formatTime(video.duration)}`;}
video.addEventListener('loadedmetadata',updateTime);video.addEventListener('timeupdate',updateTime);seek.oninput=()=>{video.currentTime=Number(seek.value);};
document.querySelector('#files').onchange=async event=>{
  const files=[...event.target.files]; if(!files.length)return; const fd=new FormData(); files.forEach(file=>fd.append('files',file));
  document.querySelector('#upload-status').textContent=`正在上传 ${files.length} 个文件… 大视频请保持此页面打开。`;
  try {const r=await fetch('/api/upload?key='+encodeURIComponent(key),{method:'POST',body:fd});const data=await r.json();if(!r.ok)throw new Error(data.error||'上传失败');document.querySelector('#upload-status').textContent=`已导入：${data.saved.join('、')}`;current=-1;await loadMedia();}catch(e){document.querySelector('#upload-status').textContent='上传失败：'+e.message;}event.target.value='';
};
async function exportFrame(){
  if(current < 0)return; const canvas=document.createElement('canvas'); let width,height;
  if(!video.hidden){width=video.videoWidth;height=video.videoHeight;}else{width=image.naturalWidth;height=image.naturalHeight;} if(!width||!height){status.textContent='媒体尚未加载完成，请稍后再试。';return;}
  canvas.width=width;canvas.height=height;canvas.getContext('2d').drawImage(video.hidden?image:video,0,0,width,height);
  exportButton.disabled=true;status.textContent='正在保存 JPEG…';
  try {const r=await fetch('/api/export?key='+encodeURIComponent(key),{method:'POST',headers:{...auth,'Content-Type':'application/json'},body:JSON.stringify({image:canvas.toDataURL('image/jpeg',0.95),sourceName:media[current].name})});const data=await r.json();if(!r.ok)throw new Error(data.error||'保存失败');status.textContent=`已保存：${data.name}（${data.folder}）`; }catch(e){status.textContent='保存失败：'+e.message;}finally{exportButton.disabled=false;}
}
exportButton.onclick=exportFrame;document.querySelector('#refresh').onclick=()=>loadMedia().catch(e=>status.textContent=e.message);document.querySelector('#previous').onclick=()=>select(current-1);document.querySelector('#next').onclick=()=>select(current+1);
shutdownButton.onclick=async()=>{shutdownButton.disabled=true;shutdownButton.textContent='正在停止…';try{const response=await fetch('/api/shutdown',{method:'POST',headers:auth});if(!response.ok)throw new Error('停止失败');serverUrls.textContent='WebUI 已停止，可以关闭此页面。';shutdownButton.textContent='已停止';}catch(e){shutdownButton.disabled=false;shutdownButton.textContent='停止 WebUI';status.textContent=e.message;}};
if(!key){status.textContent='缺少访问口令。请从启动程序打开的完整链接进入。';}else {loadMedia().catch(e=>status.textContent=e.message);loadPaths().catch(e=>status.textContent=e.message);loadServerInfo().catch(e=>serverUrls.textContent=e.message);}
