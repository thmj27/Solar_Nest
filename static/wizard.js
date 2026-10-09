const NAMES=["Location","Property","Appliances","Usage","Solar needs","Results"];
const S=INIT||{state:"",city:"",property_type:"Homestay",rooms:6,guests:12,roof_area:80,budget:600000,occupancy:70,night_share:55,backup_days:1,name:"",
 appliances:APPS.filter(a=>["light","fan","fridge"].includes(a.key)).map(a=>({key:a.key,name:a.name,qty:a.qty,watts:a.watts,hours:a.hours}))};
let step=0;const $=id=>document.getElementById(id);
const tip=t=>`<span class="tip" title="${t}">?</span>`;
const num=(k,l,min,max,h)=>`<div><label>${l}</label><input type="number" min="${min}" max="${max}" value="${S[k]}" data-k="${k}"><p class="help">${h||""}</p></div>`;
const views=[
()=>`<h2>Where is your property?</h2><p class="help">Your location helps us estimate how much solar energy your system can generate.</p>
 <label>State</label><select id="state"><option value="">Select state</option>${Object.keys(STATES).map(s=>`<option ${s==S.state?"selected":""}>${s}</option>`).join("")}</select>
 <label>City / area</label><select id="city"></select>`,
()=>`<h2>Tell us about your property</h2><label>Property type</label><div class="opt">${[["Homestay","🏡"],["Eco-resort","🌴"],["Other","🏠"]].map(([t,e])=>`<div class="pick ${S.property_type==t?"sel":""}" data-type="${t}"><div class="e">${e}</div>${t}</div>`).join("")}</div>
 <div class="grid g2">${num("rooms","Number of rooms",1,200)}${num("guests","Typical guests at once",1,1000)}${num("roof_area","Usable roof area (m²)",5,5000,"Rough shadow-free area. A 3×3 m room is about 9 m².")}${num("budget","Budget (₹)",0,100000000,"Enter 0 if you have no limit.")}</div>`,
()=>`<h2>What do you use?</h2><p class="help">Tap to select. Defaults are typical values; experts can edit them.</p><div class="opt">${APPS.map(a=>{const x=S.appliances.find(z=>z.key==a.key);return `<div class="pick ${x?"sel":""}" data-app="${a.key}"><div class="e">${a.icon}</div>${a.name}
 <div class="approw">${x?[["qty","Qty"],["watts","Watts"],["hours","Hrs/day"]].map(([f,l])=>`<div><label>${l}</label><input type="number" min="0" value="${x[f]}" data-a="${a.key}" data-f="${f}"></div>`).join(""):""}</div></div>`}).join("")}</div>`,
()=>`<h2>How is it used?</h2><label>Average occupancy: <b id="ov">${S.occupancy}</b>% ${tip("Share of the year your rooms are typically occupied. Lower occupancy means lower electricity use.")}</label><input type="range" min="10" max="100" value="${S.occupancy}" data-k="occupancy" data-o="ov">
 <label>Evening and night usage: <b id="nv">${S.night_share}</b>% ${tip("Peak usage is usually evenings. This share of daily energy must come from the battery.")}</label><input type="range" min="0" max="100" value="${S.night_share}" data-k="night_share" data-o="nv">
 <label>Battery backup ${tip("How many days of night usage the battery should cover. 0 means no battery.")}</label><select data-k="backup_days">${[[0,"No battery (grid at night)"],[0.5,"Half a day"],[1,"One day (recommended)"],[2,"Two days (cloudy regions)"]].map(([v,t])=>`<option value="${v}" ${v==S.backup_days?"selected":""}>${t}</option>`).join("")}</select>
 <p class="help">Daily energy consumption = roughly how much electricity your property uses in one day.</p>`,
()=>`<h2>Almost there</h2><p>We'll calculate solar capacity, battery size, cost, savings and CO₂ benefit for <b>${S.city}, ${S.state}</b> with <b>${S.appliances.length}</b> appliance types.</p>
 <label>Project name</label><input data-k="name" value="${S.name}" placeholder="e.g. Hill Homestay"><p class="help">All results are estimates for planning, not a final engineering design.</p>`];
function render(){
 $("steps").innerHTML=NAMES.map((n,i)=>`<div class="${i<=step?"on":""}">${i+1}. ${n}</div>`).join("");
 $("panel").innerHTML=views[step]();$("err").innerHTML="";$("back").style.visibility=step?"visible":"hidden";
 $("next").textContent=step==4?(EDIT_ID?"Save & Calculate":"Calculate my plan"):"Continue";
 const st=$("state");if(st){const fill=()=>{$("city").innerHTML='<option value="">Select city</option>'+(STATES[st.value]||[]).map(c=>`<option ${c==S.city?"selected":""}>${c}</option>`).join("")};st.onchange=()=>{S.state=st.value;S.city="";fill()};$("city").onchange=e=>S.city=e.target.value;fill()}
 document.querySelectorAll("[data-type]").forEach(e=>e.onclick=()=>{S.property_type=e.dataset.type;render()});
 document.querySelectorAll("[data-app]").forEach(e=>e.onclick=ev=>{if(ev.target.tagName=="INPUT")return;const k=e.dataset.app,i=S.appliances.findIndex(x=>x.key==k);
  if(i>=0)S.appliances.splice(i,1);else{const a=APPS.find(x=>x.key==k);S.appliances.push({key:k,name:a.name,qty:a.qty,watts:a.watts,hours:a.hours})}render()});
 document.querySelectorAll("[data-a]").forEach(e=>e.oninput=()=>S.appliances.find(x=>x.key==e.dataset.a)[e.dataset.f]=+e.value);
 document.querySelectorAll("[data-k]").forEach(e=>e.oninput=()=>{S[e.dataset.k]=e.type=="number"||e.type=="range"||e.tagName=="SELECT"?+e.value:e.value;if(e.dataset.o)$(e.dataset.o).textContent=e.value});
}
function check(){const e=[];
 if(step==0&&(!S.state||!S.city))e.push("Please choose a state and a city.");
 if(step==1){if(!(S.rooms>=1))e.push("Rooms must be at least 1.");if(!(S.guests>=1))e.push("Guests must be at least 1.");if(!(S.roof_area>=5))e.push("Roof area must be at least 5 m².");if(S.budget<0)e.push("Budget cannot be negative.")}
 if(step==2){if(!S.appliances.length)e.push("Select at least one appliance.");S.appliances.forEach(a=>{if(!(a.qty>0&&a.qty<=500))e.push(a.name+": quantity must be 1-500.");if(!(a.watts>0))e.push(a.name+": watts must be above 0.");if(!(a.hours>0&&a.hours<=24))e.push(a.name+": hours must be 0-24.")})}
 if(step==4&&!S.name.trim())e.push("Please name your project.");
 $("err").innerHTML=e.map(m=>`<div class="flash error">${m}</div>`).join("");return !e.length}
$("back").onclick=()=>{step--;render()};
$("next").onclick=async()=>{if(!check())return;if(step<4){step++;return render()}
 $("next").disabled=true;$("next").textContent="Calculating…";
 const r=await fetch(EDIT_ID?`/api/projects/${EDIT_ID}`:"/api/projects",{method:EDIT_ID?"PUT":"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(S)});
 const j=await r.json();if(r.ok)location=j.url;else{$("err").innerHTML=j.errors.map(m=>`<div class="flash error">${m}</div>`).join("");$("next").disabled=false;$("next").textContent="Calculate my plan"}};
render();
