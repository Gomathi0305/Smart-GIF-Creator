import os,sys,subprocess,tkinter as tk
from pathlib import Path
from tkinter import filedialog,messagebox
import customtkinter as ctk
from PIL import Image,ImageTk,ImageSequence
from src.gif_engine import create_gif
ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")

class App(ctk.CTk):
 def __init__(self):
  super().__init__(); self.title("Smart GIF Creator • Python"); self.geometry("1240x820"); self.minsize(1050,720)
  self.root=Path(__file__).parent; self.out=self.root/"assets/output"; self.ui=self.root/"assets/ui"; self.out.mkdir(parents=True,exist_ok=True)
  self.files=[]; self.last=None; self.hero=[]; self.hi=0; self.build(); self.load_visuals()
 def build(self):
  self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(1,weight=1)
  h=ctk.CTkFrame(self,corner_radius=0,fg_color="#11142B"); h.grid(row=0,column=0,sticky="ew"); h.grid_columnconfigure(1,weight=1)
  ctk.CTkLabel(h,text="✦ SMART GIF CREATOR",font=ctk.CTkFont(size=24,weight="bold")).grid(row=0,column=0,padx=26,pady=18,sticky="w")
  ctk.CTkLabel(h,text="Create • Animate • Customize",text_color="#A9B7FF",font=ctk.CTkFont(size=14,weight="bold")).grid(row=0,column=1,sticky="w")
  self.mode=ctk.CTkButton(h,text="Dark",width=85,command=self.toggle); self.mode.grid(row=0,column=2,padx=20)
  self.body=ctk.CTkScrollableFrame(self,fg_color="#090B18"); self.body.grid(row=1,column=0,sticky="nsew"); self.body.grid_columnconfigure(0,weight=1)
  hero=ctk.CTkFrame(self.body,corner_radius=22,fg_color="#151A35"); hero.grid(row=0,column=0,padx=24,pady=22,sticky="ew"); hero.grid_columnconfigure(0,weight=1)
  self.hero_label=ctk.CTkLabel(hero,text=""); self.hero_label.grid(row=0,column=0,padx=18,pady=18)
  ctk.CTkLabel(hero,text="Make ordinary photos move",font=ctk.CTkFont(size=25,weight="bold")).grid(row=1,column=0,pady=3)
  ctk.CTkLabel(hero,text="Build colorful GIFs from photos or videos with text, effects and resizing.",text_color="#B8C0E8").grid(row=2,column=0,pady=(0,18))
  cards=ctk.CTkFrame(self.body,fg_color="transparent"); cards.grid(row=1,column=0,padx=24,pady=5,sticky="ew")
  for i in range(4): cards.grid_columnconfigure(i,weight=1)
  self.cardlabs=[]
  for i in range(4):
   f=ctk.CTkFrame(cards,corner_radius=18,fg_color="#151A35"); f.grid(row=0,column=i,padx=6,sticky="ew")
   l=ctk.CTkLabel(f,text=""); l.pack(padx=8,pady=8); self.cardlabs.append(l)
  ws=ctk.CTkFrame(self.body,fg_color="transparent"); ws.grid(row=2,column=0,padx=24,pady=14,sticky="ew"); ws.grid_columnconfigure((0,1),weight=1)
  self.media_panel(ws); self.custom_panel(ws)
  act=ctk.CTkFrame(self.body,corner_radius=20,fg_color="#151A35"); act.grid(row=3,column=0,padx=24,pady=4,sticky="ew"); act.grid_columnconfigure((0,1,2),weight=1)
  for col,txt,color,cmd in [(0,"CREATE MY GIF","#7C3AED",self.generate),(1,"PREVIEW","#0EA5A4",self.preview),(2,"OPEN OUTPUT","#E35D9A",self.openout)]:
   ctk.CTkButton(act,text=txt,height=54,fg_color=color,font=ctk.CTkFont(size=15,weight="bold"),command=cmd).grid(row=0,column=col,padx=12,pady=16,sticky="ew")
  self.status=ctk.CTkLabel(self.body,text="● Ready — add photos or a video to begin",text_color="#A9B7FF",anchor="w"); self.status.grid(row=4,column=0,padx=28,pady=15,sticky="ew")
 def media_panel(self,p):
  f=ctk.CTkFrame(p,corner_radius=20,fg_color="#11162D"); f.grid(row=0,column=0,padx=(0,8),sticky="nsew"); f.grid_columnconfigure(0,weight=1)
  ctk.CTkLabel(f,text="01  ADD YOUR MEDIA",font=ctk.CTkFont(size=18,weight="bold")).grid(row=0,column=0,padx=20,pady=(20,4),sticky="w")
  ctk.CTkLabel(f,text="Photos become frames. Videos become moving frames.",text_color="#8F99C5").grid(row=1,column=0,padx=20,pady=5,sticky="w")
  b=ctk.CTkFrame(f,fg_color="transparent"); b.grid(row=2,column=0,padx=18,sticky="ew"); b.grid_columnconfigure((0,1),weight=1)
  ctk.CTkButton(b,text="Add Photos",fg_color="#2563EB",command=self.addimg).grid(row=0,column=0,padx=4,sticky="ew")
  ctk.CTkButton(b,text="Add Video",fg_color="#EC4899",command=self.addvid).grid(row=0,column=1,padx=4,sticky="ew")
  self.count=ctk.CTkLabel(f,text="No media selected",text_color="#B8C0E8"); self.count.grid(row=3,column=0,padx=20,pady=8,sticky="w")
  self.box=ctk.CTkTextbox(f,height=150,fg_color="#0B0F21"); self.box.grid(row=4,column=0,padx=18,pady=4,sticky="ew"); self.box.configure(state="disabled")
  ctk.CTkButton(f,text="Clear selection",fg_color="transparent",border_width=1,command=self.clear).grid(row=5,column=0,padx=18,pady=(8,20),sticky="ew")
 def custom_panel(self,p):
  f=ctk.CTkFrame(p,corner_radius=20,fg_color="#11162D"); f.grid(row=0,column=1,padx=(8,0),sticky="nsew"); f.grid_columnconfigure(1,weight=1)
  ctk.CTkLabel(f,text="02  CUSTOMIZE YOUR GIF",font=ctk.CTkFont(size=18,weight="bold")).grid(row=0,column=0,columnspan=2,padx=20,pady=20,sticky="w")
  self.duration=self.setting(f,1,"Frame duration","150")
  self.resize=self.combo(f,2,"Size",["Keep original","640 px wide","480 px wide","320 px wide"],"Keep original")
  self.effect=self.combo(f,3,"Effect",["None","Grayscale","Sepia","Brightness","Contrast"],"None")
  self.loop=self.combo(f,4,"Loop",["0 (Forever)","1","2","3","5"],"0 (Forever)")
  ctk.CTkLabel(f,text="Text on every frame",text_color="#DCE1FF").grid(row=5,column=0,padx=20,pady=10,sticky="w")
  self.text=tk.StringVar(); ctk.CTkEntry(f,textvariable=self.text,placeholder_text="Example: My First GIF").grid(row=5,column=1,padx=20,pady=10,sticky="ew")
  ctk.CTkLabel(f,text="Try: Happy Moments • College Day • your name",text_color="#7F8AB6").grid(row=6,column=0,columnspan=2,padx=20,pady=(0,20),sticky="w")
 def setting(self,f,r,label,val):
  ctk.CTkLabel(f,text=label,text_color="#DCE1FF").grid(row=r,column=0,padx=20,pady=5,sticky="w"); v=tk.StringVar(value=val); ctk.CTkEntry(f,textvariable=v).grid(row=r,column=1,padx=20,pady=5,sticky="ew"); return v
 def combo(self,f,r,label,vals,default):
  ctk.CTkLabel(f,text=label,text_color="#DCE1FF").grid(row=r,column=0,padx=20,pady=5,sticky="w"); v=tk.StringVar(value=default); ctk.CTkComboBox(f,values=vals,variable=v).grid(row=r,column=1,padx=20,pady=5,sticky="ew"); return v
 def load_visuals(self):
  im=Image.open(self.ui/"hero.gif"); self.hero=[ImageTk.PhotoImage(x.copy().convert("RGB").resize((760,230))) for x in ImageSequence.Iterator(im)]; self.animate()
  for i,l in enumerate(self.cardlabs,1):
   im=Image.open(self.ui/f"card_{i}.png"); ci=ctk.CTkImage(light_image=im,dark_image=im,size=(190,100)); l.configure(image=ci); l.image=ci
 def animate(self):
  self.hero_label.configure(image=self.hero[self.hi]); self.hi=(self.hi+1)%len(self.hero); self.after(100,self.animate)
 def toggle(self):
  dark=ctk.get_appearance_mode()=="Dark"; ctk.set_appearance_mode("light" if dark else "dark"); self.mode.configure(text="Light" if dark else "Dark")
 def updatebox(self):
  self.box.configure(state="normal"); self.box.delete("1.0","end")
  if self.files:
   for i,x in enumerate(self.files,1): self.box.insert("end",f"  {i:02d}   {Path(x).name}\n")
   self.count.configure(text=f"● {len(self.files)} media item(s) ready")
  else: self.box.insert("end","  Your selected photos/videos will appear here."); self.count.configure(text="No media selected")
  self.box.configure(state="disabled")
 def addimg(self):
  x=filedialog.askopenfilenames(filetypes=[("Images","*.png *.jpg *.jpeg *.bmp *.webp")])
  if x:self.files.extend(x);self.updatebox();self.status.configure(text=f"● Added {len(x)} photo(s)")
 def addvid(self):
  x=filedialog.askopenfilename(filetypes=[("Videos","*.mp4 *.avi *.mov *.mkv *.webm")])
  if x:self.files.append(x);self.updatebox();self.status.configure(text="● Video added")
 def clear(self): self.files=[];self.updatebox()
 def generate(self):
  if not self.files:return messagebox.showwarning("Add media","Please add at least one image or video.")
  try:d=int(self.duration.get()); assert 20<=d<=5000
  except: return messagebox.showerror("Frame duration","Enter 20–5000 milliseconds.")
  rw={"640 px wide":640,"480 px wide":480,"320 px wide":320}.get(self.resize.get())
  out=self.out/"smart_gif_output.gif"; self.status.configure(text="● Creating your GIF..."); self.update_idletasks()
  try:
   create_gif(self.files,out,d,int(self.loop.get().split()[0]),rw,self.effect.get(),self.text.get().strip()); self.last=out; self.status.configure(text="● Done! Your GIF is ready."); messagebox.showinfo("GIF Created",str(out))
  except Exception as e: messagebox.showerror("Error",str(e))
 def preview(self):
  if not self.last or not self.last.exists(): return messagebox.showinfo("Preview","Create your GIF first.")
  if sys.platform.startswith("win"): os.startfile(str(self.last))
  elif sys.platform=="darwin": subprocess.run(["open",str(self.last)])
  else: subprocess.run(["xdg-open",str(self.last)])
 def openout(self):
  if sys.platform.startswith("win"): os.startfile(str(self.out))
  elif sys.platform=="darwin": subprocess.run(["open",str(self.out)])
  else: subprocess.run(["xdg-open",str(self.out)])
if __name__=="__main__": App().mainloop()
