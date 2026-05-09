

const headers=document.querySelectorAll('.event-header');
const line=document.querySelector('.line');
headers.forEach(header=>{
    header.addEventListener('click',()=>{
        
        const box=header.closest(".event");
        document.querySelectorAll(".event").forEach(e=>{
            if(e!==box)
                e.classList.remove('active')
                
        });
        box.classList.toggle('active');
        
        
    })
})

const openbtn=document.getElementById('openPopup');
const popupform=document.getElementById('popupform');
openbtn.addEventListener('click',()=>{
    popupform.style.display="flex";
    
})
popupform.addEventListener('click',(e)=>{
    if(e.target==popupform){
        popupform.style.display="none";
    }
})

const allocate_btn = document.querySelectorAll('.allocate_btn');
const popupformallocate = document.getElementById('popupformallocate');


const eventInput = document.querySelector('#popupformallocate input[name="event_id"]');

allocate_btn.forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const eventId = btn.getAttribute('data-id'); 
        eventInput.value = eventId; 
        popupformallocate.style.display = "flex";
    });
    
});

document.querySelectorAll('.inventory-action').forEach(card=>{
    const plus=card.querySelector('.plus');
    const minus=card.querySelector('.minus')
    const input=card.querySelector('.input');
    plus.addEventListener('click',()=>{
        input.stepUp();
    });
    minus.addEventListener('click',()=>{
        input.stepDown();
    })
})

document.querySelectorAll(".edit-btn").forEach(btn=>{
    btn.addEventListener("click",()=>{
    const eventid=btn.getAttribute("data-event");
window.location.href="/inventory?event_id="+eventid;
})
})

const exit=document.getElementById('exit');
exit.addEventListener("click",()=>{
popupformallocate.style.display="none";
})

const exit_inven=document.getElementById('exit-pop');
exit_inven.addEventListener("click",()=>{
popupform.style.display="none";
})
