"""TAFWITA Desktop v10 - boutons icones + infobulles.
Installation : py -m pip install customtkinter requests
"""
import json, os, threading
from datetime import datetime
import tkinter.messagebox as messagebox
import customtkinter as ctk
import requests

API_BASE="https://tafwita-api.onrender.com"
CONFIG_FILE=os.path.join(os.path.expanduser("~"),".tafwita_cabinet.json")
BG="#F5F8F8"; SURFACE="#FFFFFF"; MINT="#F3FAF8"; BORDER="#DBEAE7"; TEAL="#329F9A"; TDARK="#237873"; TPALE="#DDF2EE"; TEXT="#28373E"; SOFT="#607078"; MUTED="#9BAAAF"; GREEN="#2C8B69"; RED="#BC5D62"; AMBER="#A97524"; BLUE="#4D82A8"; FONT="Segoe UI"
ctk.set_appearance_mode("light");ctk.set_default_color_theme("blue")

def load(p,d=None):
 try:
  with open(p,encoding="utf-8") as f:return json.load(f)
 except Exception:return d
def save(p,d):
 with open(p,"w",encoding="utf-8") as f:json.dump(d,f,ensure_ascii=False,indent=2)
def api(m,p,**kw):return requests.request(m,API_BASE.rstrip("/")+p,timeout=18,**kw)
def err(r):
 try:return str(r.json().get("detail") or r.json().get("message") or r.text)
 except Exception:return f"Erreur HTTP {r.status_code}"
def ui(w,fn):
 try:w.after(0,fn)
 except Exception:pass
def card(p):return ctk.CTkFrame(p,fg_color=SURFACE,corner_radius=18,border_width=1,border_color=BORDER)
def lbl(p,t,s=12,c=TEXT,b=False):return ctk.CTkLabel(p,text=t,font=(FONT,s,"bold" if b else "normal"),text_color=c)
def inp(p,ph,w=300,show=None):return ctk.CTkEntry(p,placeholder_text=ph,width=w,height=40,corner_radius=11,border_color=BORDER,fg_color="white",show=show,font=(FONT,12))
def valid_time(x):
 try:datetime.strptime(x,"%H:%M");return True
 except:return False

class Tooltip:
 def __init__(self,w,text):
  self.w=w;self.text=text;self.pop=None;w.bind("<Enter>",self.show);w.bind("<Leave>",self.hide);w.bind("<ButtonPress>",self.hide)
 def show(self,event=None):
  if self.pop:return
  self.pop=ctk.CTkToplevel(self.w);self.pop.overrideredirect(True);self.pop.attributes("-topmost",True);x=self.w.winfo_rootx()+4;y=self.w.winfo_rooty()+self.w.winfo_height()+5;self.pop.geometry(f"+{x}+{y}");lbl(self.pop,self.text,11,"white").pack(padx=10,pady=6);self.pop.configure(fg_color="#26363D")
 def hide(self,event=None):
  if self.pop:self.pop.destroy();self.pop=None

def icon_btn(p,icon,tip,fn,fg="#EEF5F4",hover="#DCEFEA",color=TEXT,w=40,h=36):
 b=ctk.CTkButton(p,text=icon,command=fn,width=w,height=h,corner_radius=11,fg_color=fg,hover_color=hover,text_color=color,font=(FONT,17,"bold"));Tooltip(b,tip);return b

def status_color(s):return {"waiting":TDARK,"returned":TDARK,"suspended":AMBER,"urgent":"#9C6915","serving":GREEN,"completed":MUTED,"cancelled":RED}.get(s,SOFT)
def status_label(s):return {"waiting":"En attente","returned":"Remis en attente","suspended":"Suspendu","urgent":"Urgence","serving":"En consultation","completed":"Termine","cancelled":"Annule"}.get(s,s)

class Login(ctk.CTkFrame):
 def __init__(self,m,done):super().__init__(m,fg_color=BG);self.done=done;self.build()
 def build(self):
  b=card(self);b.place(relx=.5,rely=.5,anchor="center");f=ctk.CTkFrame(b,fg_color="transparent");f.pack(padx=45,pady=42);lbl(f,"TAFWITA",28,TDARK,True).pack();lbl(f,"Connexion espace cabinet",19,TEXT,True).pack(pady=(15,14));self.slug=inp(f,"Identifiant cabinet",360);self.pin=inp(f,"Code PIN",360,"*");self.slug.pack(pady=5);self.pin.pack(pady=5);old=load(CONFIG_FILE,{}) or {};self.slug.insert(0,old.get("slug",""));self.msg=lbl(f,"",11,RED);self.msg.pack(pady=8);b=ctk.CTkButton(f,text="Se connecter",command=self.connect,fg_color=TEAL,hover_color=TDARK,width=360,height=44,corner_radius=13,font=(FONT,12,"bold"));b.pack();self.pin.bind("<Return>",lambda e:self.connect())
 def connect(self):
  sl=self.slug.get().strip();pi=self.pin.get().strip()
  if not sl or not pi:self.msg.configure(text="Identifiant et PIN obligatoires.");return
  def work():
   try:
    r=api("POST",f"/api/cabinets/{sl}/verify-pin",json={"code_pin":pi})
    if r.ok:
     d=r.json();cfg={"slug":sl,"pin":pi,"name":d.get("cabinet_nom",sl)};save(CONFIG_FILE,cfg);ui(self,lambda:self.done(cfg))
    else:ui(self,lambda m=err(r):self.msg.configure(text=m))
   except Exception as e:ui(self,lambda m=str(e):self.msg.configure(text=m))
  threading.Thread(target=work,daemon=True).start()

class AddDialog(ctk.CTkToplevel):
 def __init__(self,parent,app):
  super().__init__(parent);self.app=app;self.title("Ajouter un ticket papier");self.geometry("430x270");self.configure(fg_color=BG);self.grab_set();b=card(self);b.pack(fill="both",expand=True,padx=18,pady=18);f=ctk.CTkFrame(b,fg_color="transparent");f.pack(padx=24,pady=20);lbl(f,"Ajouter un ticket papier",17,TEXT,True).pack(anchor="w",pady=(0,8));self.name=inp(f,"Nom du patient",350);self.phone=inp(f,"Telephone (optionnel)",350);self.name.pack(pady=5);self.phone.pack(pady=5);self.msg=lbl(f,"",11,RED);self.msg.pack();row=ctk.CTkFrame(f,fg_color="transparent");row.pack(pady=12);icon_btn(row,"×","Fermer",self.destroy,"#F2F5F5","#E6EEEE",SOFT,72,36).pack(side="left",padx=5);icon_btn(row,"＋","Ajouter le ticket",self.submit,"#DDF2EE","#C9E9E2",TDARK,72,36).pack(side="left",padx=5)
 def submit(self):
  n=self.name.get().strip()
  if not n:self.msg.configure(text="Nom obligatoire.");return
  def work():
   try:
    r=api("POST","/api/tickets/add-manual",json={"cabinet_slug":self.app.slug,"nom_patient":n,"telephone":self.phone.get().strip() or None})
    if r.ok:ui(self,lambda:(self.destroy(),self.app.refresh()))
    else:ui(self,lambda m=err(r):self.msg.configure(text=m))
   except Exception as e:ui(self,lambda m=str(e):self.msg.configure(text=m))
  threading.Thread(target=work,daemon=True).start()

class App(ctk.CTk):
 def __init__(self):
  super().__init__();self.title("TAFWITA Cabinet v10");self.geometry("1220x780");self.minsize(1000,650);self.configure(fg_color=BG);self.cfg=None;self.data={};self.page="home";self.show_login()
 def clear(self):
  for x in self.winfo_children():x.destroy()
 def show_login(self):self.clear();Login(self,self.dashboard).pack(fill="both",expand=True)
 def dashboard(self,cfg):
  self.clear();self.cfg=cfg;self.slug=cfg["slug"];self.pin=cfg["pin"];self.name=cfg.get("name",self.slug);root=ctk.CTkFrame(self,fg_color=BG);root.pack(fill="both",expand=True);side=ctk.CTkFrame(root,fg_color=SURFACE,width=220,corner_radius=0);side.pack(side="left",fill="y");lbl(side,"TAFWITA",23,TDARK,True).pack(anchor="w",padx=22,pady=(27,3));lbl(side,self.name,11,MUTED).pack(anchor="w",padx=22,pady=(0,17));self.nav={}
  for k,t,ic in [("home","Accueil","⌂"),("history","Historique","☷"),("settings","Horaires et regles","⚙")]:
   b=ctk.CTkButton(side,text=f"{ic}  {t}",anchor="w",command=lambda x=k:self.go(x),fg_color="transparent",hover_color=TPALE,text_color=SOFT,height=42,corner_radius=10,font=(FONT,13));b.pack(fill="x",padx=15,pady=3);self.nav[k]=b
  ctk.CTkFrame(side,fg_color="transparent").pack(fill="both",expand=True);logout=icon_btn(side,"⇥","Se deconnecter",self.logout,"#FCEEEE","#F7DEDE",RED,178,40);logout.pack(padx=20,pady=20);self.area=ctk.CTkFrame(root,fg_color=BG);self.area.pack(side="left",fill="both",expand=True,padx=25,pady=22);self.go("home")
 def logout(self):
  if os.path.exists(CONFIG_FILE):os.remove(CONFIG_FILE)
  self.show_login()
 def go(self,k):
  self.page=k
  for w in self.area.winfo_children():w.destroy()
  for n,b in self.nav.items():b.configure(fg_color=TPALE if n==k else "transparent",text_color=TDARK if n==k else SOFT)
  if k=="home":self.home()
  elif k=="history":self.history()
  else:self.settings()
  self.refresh()
 def home(self):
  h=ctk.CTkFrame(self.area,fg_color="transparent");h.pack(fill="x",pady=(0,12));lbl(h,"Accueil",24,TEXT,True).pack(side="left");self.badge=lbl(h,"Chargement...",11,"white",True);self.badge.pack(side="right",padx=8,pady=5)
  stats=ctk.CTkFrame(self.area,fg_color="transparent");stats.pack(fill="x");self.stats=[]
  for title,col in [("En consultation",GREEN),("En attente",TEAL),("Tickets du jour",TDARK)]:
   c=card(stats);c.pack(side="left",expand=True,fill="x",padx=4);v=lbl(c,"-",27,col,True);v.pack(anchor="w",padx=17,pady=(12,0));lbl(c,title,11,SOFT,True).pack(anchor="w",padx=17,pady=(0,12));self.stats.append(v)
  a=card(self.area);a.pack(fill="x",pady=14);f=ctk.CTkFrame(a,fg_color="transparent");f.pack(fill="x",padx=17,pady=14);lbl(f,"Gestion de la journee",15,TEXT,True).pack(anchor="w");lbl(f,"Survolez une icone pour connaitre son action.",10,MUTED).pack(anchor="w",pady=(1,8));row=ctk.CTkFrame(f,fg_color="transparent");row.pack(anchor="w")
  self.start=icon_btn(row,"▶","Demarrer une nouvelle journee",self.start_day,"#E4F5EE","#CFEBDD",GREEN,44,39);self.start.pack(side="left",padx=3);icon_btn(row,"📣","Appeler le patient suivant",self.next,"#DDF2EE","#C8E8E1",TDARK,44,39).pack(side="left",padx=3);icon_btn(row,"＋","Ajouter un ticket papier",lambda:AddDialog(self,self),"#EAF1F8","#D7E7F4",BLUE,44,39).pack(side="left",padx=3);self.toggle=icon_btn(row,"II","Arreter la prise de tickets",self.toggle_tickets,"#FFF4DE","#FCE7BC",AMBER,44,39);self.toggle.pack(side="left",padx=3);icon_btn(row,"■","Cloturer la journee",self.close_day,"#FCECED","#F7D8DA",RED,44,39).pack(side="left",padx=3);self.msg=lbl(f,"",11,RED);self.msg.pack(anchor="w",pady=(8,0))
  q=card(self.area);q.pack(fill="both",expand=True);qi=ctk.CTkFrame(q,fg_color="transparent");qi.pack(fill="both",expand=True,padx=17,pady=15);lbl(qi,"File en direct",16,TEXT,True).pack(anchor="w");self.list=ctk.CTkScrollableFrame(qi,fg_color="transparent");self.list.pack(fill="both",expand=True,pady=(8,0))
 def history(self):
  lbl(self.area,"Historique",24,TEXT,True).pack(anchor="w");lbl(self.area,"Tickets du cabinet et trace des actions.",12,MUTED).pack(anchor="w",pady=(3,13));b=card(self.area);b.pack(fill="both",expand=True);self.hist=ctk.CTkScrollableFrame(b,fg_color="transparent");self.hist.pack(fill="both",expand=True,padx=16,pady=15)
 def settings(self):
  lbl(self.area,"Horaires et regles",24,TEXT,True).pack(anchor="w");lbl(self.area,"Les patients peuvent prendre un ticket avant l ouverture. Le mode manuel convient aux horaires variables.",12,MUTED).pack(anchor="w",pady=(3,14));b=card(self.area);b.pack(fill="both",expand=True);f=ctk.CTkFrame(b,fg_color="transparent");f.pack(anchor="nw",padx=28,pady=25);lbl(f,"Mode de fermeture",12,SOFT,True).pack(anchor="w");self.mode=ctk.CTkOptionMenu(f,values=["manual","fixed"],width=310,height=40,fg_color=TPALE,button_color=TEAL);self.mode.pack(anchor="w",pady=(4,10));self.fields={}
  for key,title,ph in [("ticket_start","Debut prise de tickets","06:00"),("ticket_end","Fin auto prise (vide en manuel)","15:30"),("opening","Ouverture cabinet","08:00"),("closing","Fermeture prevue (optionnel)","17:00"),("maximum","Maximum tickets par jour","35")]:
   lbl(f,title,11,SOFT,True).pack(anchor="w",pady=(6,3));e=inp(f,ph,310);e.pack(anchor="w");self.fields[key]=e
  self.setmsg=lbl(f,"",11,RED);self.setmsg.pack(anchor="w",pady=12);saveb=ctk.CTkButton(f,text="Enregistrer les regles",command=self.save_settings,fg_color=TEAL,hover_color=TDARK,width=310,height=42,corner_radius=12,font=(FONT,12,"bold"));saveb.pack(anchor="w")
 def refresh(self):
  def work():
   try:
    if self.page=="history":r=api("GET",f"/api/cabinets/{self.slug}/tickets");ui(self,lambda d=r.json() if r.ok else []:self.render_history(d));return
    r=api("GET",f"/api/queue/{self.slug}")
    if r.ok:ui(self,lambda d=r.json():self.render(d))
    elif hasattr(self,"msg"):ui(self,lambda m=err(r):self.msg.configure(text=m))
   except Exception as e:
    if hasattr(self,"msg"):ui(self,lambda m=str(e):self.msg.configure(text=m))
  threading.Thread(target=work,daemon=True).start()
 def render(self,d):
  self.data=d
  if self.page=="home":
   closed=d.get("day_closed");open_=d.get("accept_tickets");txt="JOURNEE CLOTUREE" if closed else "PRISE ACTIVE" if open_ else "PRISE ARRETEE";col=RED if closed else GREEN if open_ else AMBER;self.badge.configure(text=txt,fg_color=col,padx=10,pady=6,corner_radius=12);self.stats[0].configure(text=d.get("display_serving","-"));self.stats[1].configure(text=str(d.get("waiting_count",0)));self.stats[2].configure(text=str(d.get("total_issued",0)));self.start.configure(state="normal" if closed else "disabled");self.toggle.configure(text="▶" if not open_ else "⏸",fg_color="#E4F5EE" if not open_ else "#FFF4DE",hover_color="#CFEBDD" if not open_ else "#FCE7BC",text_color=GREEN if not open_ else AMBER,state="disabled" if closed else "normal")
   for w in self.list.winfo_children():w.destroy()
   ts=d.get("tickets",[])
   if not ts:lbl(self.list,"Aucun ticket actif.",12,MUTED).pack(pady=25)
   for t in ts:self.ticket_row(t)
  elif self.page=="settings":
   self.mode.set(d.get("ticket_mode","manual"));vals={"ticket_start":d.get("ticket_start_time","06:00"),"ticket_end":d.get("ticket_end_time") or "","opening":d.get("opening_time","08:00"),"closing":d.get("closing_time") or "","maximum":str(d.get("max_tickets_per_day") or "")}
   for k,v in vals.items():self.fields[k].delete(0,"end");self.fields[k].insert(0,v)
 def ticket_row(self,t):
  r=ctk.CTkFrame(self.list,fg_color=MINT,corner_radius=10);r.pack(fill="x",pady=4);lbl(r,f"P-{t.get('ticket_num',0):02d}",12,TDARK,True).pack(side="left",padx=9,pady=9);lbl(r,t.get("nom_patient","Patient"),12,SOFT).pack(side="left",padx=5);lbl(r,status_label(t.get("statut","waiting")),11,status_color(t.get("statut")),True).pack(side="left",padx=12);a=ctk.CTkFrame(r,fg_color="transparent");a.pack(side="right",padx=7);s=t.get("statut")
  if s in ["waiting","returned"]:icon_btn(a,"⏸","Suspendre ce ticket",lambda x=t:self.ticket_action(x,"suspend"),"#FFF4DE","#FCE7BC",AMBER,36,30).pack(side="left",padx=2)
  if s=="suspended":
   icon_btn(a,"↩","Remettre ce ticket dans la file",lambda x=t:self.ticket_action(x,"return-to-queue"),"#DDF2EE","#C8E8E1",TDARK,36,30).pack(side="left",padx=2)
   icon_btn(a,"📣","Enregistrer un passage sans reponse",lambda x=t:self.notify(x),"#EAF1F8","#D7E7F4",BLUE,36,30).pack(side="left",padx=2)
   icon_btn(a,"×","Annuler apres 5 passages",lambda x=t:self.cancel_ticket(x),"#FCECED","#F7D8DA",RED,36,30).pack(side="left",padx=2)
  if s not in ["serving","completed","cancelled"]:icon_btn(a,"!","Valider une priorite medicale",lambda x=t:self.urgent(x),"#FFF4DE","#FCE7BC",AMBER,36,30).pack(side="left",padx=2)
  icon_btn(a,"☷","Voir la trace du ticket",lambda x=t:self.trace(x),"#EEF4F4","#DFEBE9",SOFT,36,30).pack(side="left",padx=2)
 def ticket_action(self,t,action):self.do("POST",f"/api/tickets/{t['id']}/{action}",json={"code_pin":self.pin,"reason_code":"desktop","reason_note":"Action cabinet"})
 def notify(self,t):
  def work():
   try:
    r=api("POST",f"/api/tickets/{t['id']}/notify",params={"pin":self.pin});ui(self,lambda m=("Passage enregistre : "+str(r.json().get("notification_count")) if r.ok else err(r)),ok=r.ok:self.done(m,ok))
   except Exception as e:ui(self,lambda m=str(e):self.done(m,False))
  threading.Thread(target=work,daemon=True).start()
 def cancel_ticket(self,t):
  n=t.get("notification_count",0)
  if n<5:messagebox.showwarning("TAFWITA",f"Annulation impossible : {n}/5 passages enregistres.");return
  if messagebox.askyesno("Annuler",f"Le ticket P-{t['ticket_num']:02d} est suspendu et a {n} passages sans reponse. Confirmer l annulation ?"):self.do("POST",f"/api/tickets/{t['id']}/cabinet-cancel",json={"code_pin":self.pin,"reason_note":"Absence apres 5 passages"})
 def urgent(self,t):
  note=ctk.CTkInputDialog(text="Motif urgence :",title="Urgence").get_input()
  if note:self.do("POST",f"/api/tickets/{t['id']}/approve-urgent",json={"code_pin":self.pin,"urgent_reason":note})
 def trace(self,t):
  d=ctk.CTkToplevel(self);d.title(f"Trace P-{t['ticket_num']:02d}");d.geometry("580x430");d.configure(fg_color=BG);b=card(d);b.pack(fill="both",expand=True,padx=15,pady=15);box=ctk.CTkScrollableFrame(b,fg_color="transparent");box.pack(fill="both",expand=True,padx=15,pady=15)
  def work():
   try:
    r=api("GET",f"/api/tickets/{t['id']}/events")
    for e in (r.json() if r.ok else []):ui(box,lambda x=e:lbl(box,f"{x.get('created_at','')[:16]}  |  {x.get('event_type','')}  {x.get('reason_note') or ''}",12,SOFT).pack(anchor="w",pady=6))
   except Exception as e:ui(box,lambda m=str(e):lbl(box,m,11,RED).pack())
  threading.Thread(target=work,daemon=True).start()
 def render_history(self,ts):
  for w in self.hist.winfo_children():w.destroy()
  if not ts:lbl(self.hist,"Aucun historique.",12,MUTED).pack(pady=25)
  for t in ts:
   r=ctk.CTkFrame(self.hist,fg_color=MINT,corner_radius=10);r.pack(fill="x",pady=3);lbl(r,f"P-{t.get('ticket_num',0):02d}",12,TDARK,True).pack(side="left",padx=9,pady=9);lbl(r,t.get("nom_patient","Patient"),12,SOFT).pack(side="left",padx=6);lbl(r,status_label(t.get("statut","")),11,status_color(t.get("statut")),True).pack(side="left",padx=14);lbl(r,(t.get("created_at") or "")[:16].replace("T"," "),10,MUTED).pack(side="left",padx=8);icon_btn(r,"☷","Voir la trace du ticket",lambda x=t:self.trace(x),"#EEF4F4","#DFEBE9",SOFT,36,30).pack(side="right",padx=8)
 def do(self,m,p,**kw):
  def work():
   try:r=api(m,p,**kw);ui(self,lambda x=("Operation enregistree." if r.ok else err(r)),ok=r.ok:self.done(x,ok))
   except Exception as e:ui(self,lambda x=str(e):self.done(x,False))
  threading.Thread(target=work,daemon=True).start()
 def done(self,m,ok):
  if hasattr(self,"msg"):self.msg.configure(text=m,text_color=GREEN if ok else RED)
  self.refresh()
 def next(self):self.do("POST",f"/api/queue/{self.slug}/next",params={"pin":self.pin})
 def start_day(self):
  if messagebox.askyesno("Demarrer", "Demarrer une nouvelle journee et activer la prise de tickets ?"):self.do("POST",f"/api/cabinets/{self.slug}/start-day",json={"code_pin":self.pin})
 def close_day(self):
  if messagebox.askyesno("Cloturer", "Cloturer la journee ? Les tickets restants seront annules."):self.do("POST",f"/api/cabinets/{self.slug}/close-day",params={"pin":self.pin},json={"reason":"cabinet_closed","notify_patients":True})
 def toggle_tickets(self):self.do("PUT",f"/api/cabinets/{self.slug}/settings",params={"pin":self.pin},json={"accept_tickets":not self.data.get("accept_tickets",True)})
 def save_settings(self):
  st=self.fields["ticket_start"].get().strip();en=self.fields["ticket_end"].get().strip();op=self.fields["opening"].get().strip();cl=self.fields["closing"].get().strip();mx=self.fields["maximum"].get().strip()
  if not valid_time(st) or not valid_time(op) or (en and not valid_time(en)) or (cl and not valid_time(cl)):self.setmsg.configure(text="Format heures invalide : HH:MM.");return
  try:maximum=int(mx) if mx else None
  except:self.setmsg.configure(text="Maximum invalide.");return
  p={"ticket_mode":self.mode.get(),"ticket_start_time":st,"ticket_end_time":en or None,"opening_time":op,"closing_time":cl or None,"max_tickets_per_day":maximum}
  def work():
   try:r=api("PUT",f"/api/cabinets/{self.slug}/settings",params={"pin":self.pin},json=p);ui(self,lambda m=("Regles enregistrees." if r.ok else err(r)),ok=r.ok:self.setmsg.configure(text=m,text_color=GREEN if ok else RED));self.refresh()
   except Exception as e:ui(self,lambda m=str(e):self.setmsg.configure(text=m))
  threading.Thread(target=work,daemon=True).start()
if __name__=="__main__":App().mainloop()
